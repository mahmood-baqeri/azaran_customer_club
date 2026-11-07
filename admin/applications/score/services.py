"""
سرویس ثبت تراکنش‌های امتیاز.
تنها راه مجاز برای تغییر امتیاز کاربران.

قواعد کلیدی:
- همه چیز داخل transaction.atomic
- cap check بعد از select_for_update (جلوگیری از race)
- idempotency check به‌صورت بهینه در ابتدا (بدون lock)
- کاربر نمی‌تواند از طریق endpoint معمولی به SPENT منفی برسه
"""
from typing import Optional

from django.db import transaction
from django.utils import timezone

from applications.score.constants import (
    FIXED_EARNED_CODES,
    FIXED_SPENT_CODES,
)
from applications.score.helpers import (
    build_idempotency_key,
    check_cap,
    get_rule,
)
from applications.score.models import ScoreRule, UserScore, UserScoreLog


class ScoreError(Exception):
    """خطای منطقی ثبت امتیاز (پیام فارسی قابل نمایش به کاربر)."""


# ═══════════════════════════════════════════════════════════
# ثبت تراکنش (قلب سیستم)
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def record_score_transaction(
    *,
    user_id: int,
    code: str,
    base_value: Optional[int] = None,       # برای PERCENT
    units: Optional[int] = None,            # برای PER_UNIT
    level: Optional[str] = None,            # برای PER_LEVEL
    direction: Optional[str] = None,        # اگر None → از code استنتاج
    amount_override: Optional[int] = None,  # برای refund و ADMIN_ADJUST
    reference_type: Optional[str] = None,
    reference_id: Optional[str] = None,
    source: str = UserScoreLog.Source.SYSTEM,
    created_by_id: Optional[int] = None,
    reason: Optional[str] = None,
    extra: Optional[dict] = None,
    reverses_log_id: Optional[int] = None,
) -> tuple[UserScoreLog, bool]:
    """
    ثبت اتمیک یک تراکنش امتیاز.

    Returns
    -------
    (log, created)
        created=False ⇒ به دلیل idempotency، تراکنش تکراری ثبت نشد.
    """
    # ── ۱) اعتبارسنجی کد ─────────────────────────────
    if code not in UserScoreLog.TransactionCode.values:
        raise ScoreError(f"کد تراکنش نامعتبر است: {code}")

    # ── ۲) گرفتن قاعده ───────────────────────────────
    rule = get_rule(code)

    # ── ۳) بررسی reference در صورت نیاز ──────────────
    if rule.requires_reference and not reference_id:
        raise ScoreError(f"تراکنش {rule.get_code_display()} نیاز به مرجع دارد")

    # ── ۴) ساخت idempotency_key ──────────────────────
    idem = build_idempotency_key(rule, user_id, reference_id)

    # ── ۵) idempotent fast-path (بدون lock) ──────────
    if idem:
        existing = UserScoreLog.objects.filter(
            user_id=user_id, idempotency_key=idem,
        ).first()
        if existing:
            return existing, False

    # ── ۶) محاسبه مقدار ─────────────────────────────
    if amount_override is not None:
        amount = amount_override
    else:
        amount = rule.compute_amount(
            base_value=base_value, units=units, level=level,
        )

    if amount < 0:
        raise ScoreError("مقدار امتیاز نمی‌تواند منفی باشد")

    # ── ۷) تعیین جهت ─────────────────────────────────
    if direction is None:
        if code in FIXED_SPENT_CODES:
            direction = UserScoreLog.Direction.SPENT
        elif code in FIXED_EARNED_CODES:
            direction = UserScoreLog.Direction.EARNED
        elif code == UserScoreLog.TransactionCode.ADMIN_ADJUST:
            raise ScoreError("برای ADMIN_ADJUST باید direction صریح داده شود")
        else:
            direction = UserScoreLog.Direction.EARNED

    if direction not in UserScoreLog.Direction.values:
        raise ScoreError(f"جهت نامعتبر: {direction}")

    # ── ۸) قفل ردیف امتیاز ───────────────────────────
    score, _ = (
        UserScore.objects
        .select_for_update()
        .get_or_create(user_id=user_id)
    )

    # ── ۹) cap check داخل lock (جلوگیری از race) ─────
    allowed, msg = check_cap(user_id, rule)
    if not allowed:
        raise ScoreError(msg)

    # ── ۱۰) بررسی موجودی برای SPENT ─────────────────
    if direction == UserScoreLog.Direction.SPENT:
        if amount > score.current_balance and code not in {
            UserScoreLog.TransactionCode.EXPIRE,
            UserScoreLog.TransactionCode.ADMIN_ADJUST,
        }:
            raise ScoreError("موجودی امتیاز کافی نیست")

    # ── ۱۱) محاسبه موجودی ───────────────────────────
    balance_before = score.current_balance
    if direction == UserScoreLog.Direction.EARNED:
        score.current_balance += amount
        score.total_earned   += amount
    else:
        score.current_balance -= amount
        score.total_spent    += amount
    score.save(update_fields=["current_balance", "total_earned", "total_spent"])

    # ── ۱۲) ثبت لاگ ─────────────────────────────────
    log = UserScoreLog.objects.create(
        user_id=user_id,
        transaction_code=code,
        direction=direction,
        amount=amount,
        balance_before=balance_before,
        balance_after=score.current_balance,
        reference_type=reference_type,
        reference_id=reference_id,
        idempotency_key=idem,
        source=source,
        created_by_id=created_by_id,
        reason=reason,
        extra_data=extra or {},
        reverses_log_id=reverses_log_id,
    )

    # ── ۱۳) علامت‌گذاری برگشت ───────────────────────
    if reverses_log_id:
        UserScoreLog.objects.filter(pk=reverses_log_id).update(
            is_reversed=True, reversed_at=timezone.now(),
        )

    return log, True


# ═══════════════════════════════════════════════════════════
# بازگشت تراکنش (refund)
# ═══════════════════════════════════════════════════════════
def reverse_score_transaction(
    *,
    log_id: int,
    reason: str,
    created_by_id: Optional[int] = None,
) -> tuple[UserScoreLog, bool]:
    """
    بازگشت یک تراکنش مشخص (لغو سفارش، اصلاح خطا).
    از ORDER_REFUND استفاده می‌کند و تراکنش اصلی را is_reversed می‌کند.
    """
    original = UserScoreLog.objects.filter(pk=log_id).first()
    if not original:
        raise ScoreError("تراکنش اصلی یافت نشد")
    if original.is_reversed:
        raise ScoreError("این تراکنش قبلاً برگشت خورده است")

    reverse_direction = (
        UserScoreLog.Direction.SPENT
        if original.direction == UserScoreLog.Direction.EARNED
        else UserScoreLog.Direction.EARNED
    )

    return record_score_transaction(
        user_id=original.user_id,
        code=UserScoreLog.TransactionCode.ORDER_REFUND,
        direction=reverse_direction,
        amount_override=original.amount,
        reference_type=original.reference_type,
        reference_id=original.reference_id,
        source=UserScoreLog.Source.SYSTEM,
        created_by_id=created_by_id,
        reason=reason,
        reverses_log_id=original.id,
        extra={"original_log_id": original.id},
    )


# ═══════════════════════════════════════════════════════════
# تنظیم دستی توسط ادمین
# ═══════════════════════════════════════════════════════════
def admin_adjust_score(
    *,
    user_id: int,
    amount: int,
    direction: str,
    created_by_id: int,
    reason: str,
    extra: Optional[dict] = None,
) -> tuple[UserScoreLog, bool]:
    """تنظیم دستی امتیاز توسط ادمین (بدون کنترل موجودی)."""
    return record_score_transaction(
        user_id=user_id,
        code=UserScoreLog.TransactionCode.ADMIN_ADJUST,
        direction=direction,
        amount_override=amount,
        source=UserScoreLog.Source.ADMIN,
        created_by_id=created_by_id,
        reason=reason,
        extra=extra,
    )

# نمونه استفاده در جای‌های مختلف

# ثبت‌نام + تکمیل پروفایل
# # when user signs up (بعد از تأیید مدارک)
# record_score_transaction(
#     user_id=user.id,
#     code="SIGNUP",
#     amount=score_rule("SIGNUP"),   # از تنظیمات
#     reason="ثبت‌نام کاربر",
# )

# # تکمیل مشخصات فردی
# record_score_transaction(
#     user_id=user.id,
#     code="PROFILE_PERSONAL_INFO",
#     amount=10,
#     reason="تکمیل مشخصات فردی",
# )


# کوئیز روزانه (روزی یک‌بار، حتی غلط → ۰)
# log, created = record_score_transaction(
#     user_id=user.id,
#     code="DAILY_QUIZ",
#     amount=1 if correct else 0,
#     extra={"quiz_id": quiz.id, "correct": correct},
# )
# if not created:
#     raise ScoreError("کوئیز امروز را قبلاً انجام داده‌اید")



# ثبت فاکتور (با reference)
# record_score_transaction(
#     user_id=user.id,
#     code="INVOICE",
#     amount=calculated_points,
#     reference_type="invoice",
#     reference_id=str(invoice.id),
#     extra={"invoice_amount": int(invoice.total)},
#     reason="ثبت فاکتور تأییدشده",
# )


# خرید هدیه (SPEND با کنترل موجودی)
# log, created = record_score_transaction(
#     user_id=user.id,
#     code="GIFT_REDEEM",
#     amount=4000,
#     reference_type="gift_order",
#     reference_id=str(order.id),
#     extra={"gift_id": gift.id, "tier_discount": 10},
#     source=UserScoreLog.Source.USER,
# )


# لغو سفارش → refund
# def refund_gift_order(order):
#     # پیدا کردن لاگ اصلی خرید
#     original = UserScoreLog.objects.filter(
#         user_id=order.user_id,
#         transaction_code="GIFT_REDEEM",
#         reference_id=str(order.id),
#     ).first()
#     if not original or original.is_reversed:
#         return

#     record_score_transaction(
#         user_id=order.user_id,
#         code="ORDER_REFUND",
#         amount=original.amount,
#         reference_type="gift_order",
#         reference_id=str(order.id),
#         reverses_log_id=original.id,
#         reason=f"لغو سفارش هدیه #{order.id}",
#     )
    
    
# تنظیم دستی توسط ادمین
# record_score_transaction(
#     user_id=target_user.id,
#     code="ADMIN_ADJUST",
#     direction=UserScoreLog.Direction.EARNED,   # یا SPENT
#     amount=50,
#     source=UserScoreLog.Source.ADMIN,
#     created_by_id=admin.id,
#     reason="جبران خطای سیستم",
#     extra={"admin_name": admin.full_name, "ticket_id": "T-123"},
# )



