"""
تنها سطح عمومی برای بقیه اپ‌ها.
از این توابع استفاده کن، نه از record_score_transaction مستقیم.
"""
from typing import Optional

from django.db.models import Q
from django.utils import timezone

from applications.score.helpers import check_cap, get_period_start, get_rule
from applications.score.models import ScoreRule, UserScore, UserScoreLog
from applications.score.services import (
    ScoreError,
    admin_adjust_score,
    record_score_transaction,
    reverse_score_transaction,
)


# ═══════════════════════════════════════════════════════════
# اعطا
# ═══════════════════════════════════════════════════════════
def award(
    user,
    code: str,
    *,
    base_value: Optional[int] = None,
    units: Optional[int] = None,
    level: Optional[str] = None,
    reference_type: Optional[str] = None,
    reference_id: Optional[str] = None,
    reason: Optional[str] = None,
    extra: Optional[dict] = None,
    amount_override: Optional[int] = None,
    created_by=None,
    source: str = UserScoreLog.Source.SYSTEM,
) -> Optional[UserScoreLog]:
    """
    اعطای امتیاز.
    برمی‌گرداند UserScoreLog یا None اگه idempotent (تکراری) بود.
    """
    user_id = user.id if hasattr(user, "id") else int(user)
    try:
        log, created = record_score_transaction(
            user_id=user_id,
            code=code,
            base_value=base_value,
            units=units,
            level=level,
            reference_type=reference_type,
            reference_id=reference_id,
            source=source,
            created_by_id=created_by.id if created_by else None,
            reason=reason,
            extra=extra,
            amount_override=amount_override,
        )
        return log if created else None
    except ScoreError:
        # امتیاز عوارض جانبی است — خطا نباید عملیات اصلی را fail کند
        return None


# ═══════════════════════════════════════════════════════════
# کسر
# ═══════════════════════════════════════════════════════════
def spend(
    user,
    code: str,
    *,
    amount: Optional[int] = None,
    reference_type: Optional[str] = None,
    reference_id: Optional[str] = None,
    reason: Optional[str] = None,
    extra: Optional[dict] = None,
    created_by=None,
    source: str = UserScoreLog.Source.USER,
) -> UserScoreLog:
    """
    کسر امتیاز. برخلاف award، اینجا خطا throw می‌شه چون
    اگه موجودی کافی نباشه، عملیات خرید باید fail بشه.
    """
    user_id = user.id if hasattr(user, "id") else int(user)
    log, _ = record_score_transaction(
        user_id=user_id,
        code=code,
        direction=UserScoreLog.Direction.SPENT,
        amount_override=amount,
        reference_type=reference_type,
        reference_id=reference_id,
        source=source,
        created_by_id=created_by.id if created_by else None,
        reason=reason,
        extra=extra,
    )
    return log


# ═══════════════════════════════════════════════════════════
# برگشت
# ═══════════════════════════════════════════════════════════
def refund(log_id: int, *, reason: str, created_by=None) -> UserScoreLog:
    log, _ = reverse_score_transaction(
        log_id=log_id,
        reason=reason,
        created_by_id=created_by.id if created_by else None,
    )
    return log


# ═══════════════════════════════════════════════════════════
# تنظیم دستی (ادمین)
# ═══════════════════════════════════════════════════════════
def adjust(
    user, amount: int, direction: str,
    *, admin, reason: str, extra: Optional[dict] = None,
) -> UserScoreLog:
    user_id = user.id if hasattr(user, "id") else int(user)
    log, _ = admin_adjust_score(
        user_id=user_id, amount=amount, direction=direction,
        created_by_id=admin.id, reason=reason, extra=extra,
    )
    return log


# ═══════════════════════════════════════════════════════════
# خواندن
# ═══════════════════════════════════════════════════════════
def can_do(user, code: str) -> tuple[bool, str]:
    user_id = user.id if hasattr(user, "id") else int(user)
    try:
        rule = get_rule(code)
    except ValueError as e:
        return False, str(e)
    return check_cap(user_id, rule)


def get_balance(user) -> dict:
    user_id = user.id if hasattr(user, "id") else int(user)
    score = UserScore.objects.filter(user_id=user_id).first()
    if not score:
        return {"current_balance": 0, "total_earned": 0, "total_spent": 0}
    return {
        "current_balance": score.current_balance,
        "total_earned": score.total_earned,
        "total_spent": score.total_spent,
    }


def get_daily_progress(user) -> list[dict]:
    """وضعیت امروز بازی‌ها و چالش‌ها برای نمایش در UI."""
    user_id = user.id if hasattr(user, "id") else int(user)
    result = []
    rules = ScoreRule.objects.filter(
        is_active=True, cap_period=ScoreRule.CapPeriod.DAILY,
    ).order_by("code")
    for rule in rules:
        period_start = get_period_start(rule.cap_period)
        used = UserScoreLog.objects.filter(
            user_id=user_id,
            transaction_code=rule.code,
            created_at__gte=period_start,
        ).count()
        max_count = rule.cap_count or 0
        result.append({
            "code": rule.code,
            "code_display": rule.get_code_display(),
            "used": used,
            "max": max_count,
            "available": max_count == 0 or used < max_count,
        })
    return result
