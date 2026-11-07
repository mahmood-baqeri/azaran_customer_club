"""
توابع کمکی برای کار با قواعد امتیاز و بررسی سقف تکرار.
"""
from datetime import timedelta
from typing import Optional

from django.db.models import Sum
from django.utils import timezone

from applications.score.models import ScoreRule, UserScoreLog


def get_rule(code: str) -> ScoreRule:
    """گرفتن قاعده معتبر یا خطا."""
    rule = ScoreRule.objects.filter(code=code).first()
    if not rule:
        raise ValueError(f"قاعده‌ای برای {code} تعریف نشده است")
    if not rule.is_currently_valid():
        raise ValueError(f"قاعده {code} در حال حاضر فعال نیست")
    return rule


def get_period_start(period: str):
    """شروع دوره فعلی برای cap_period."""
    now = timezone.now()
    if period == ScoreRule.CapPeriod.DAILY:
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == ScoreRule.CapPeriod.WEEKLY:
        days_since_sat = (now.weekday() + 2) % 7   # شنبه = شروع هفته در ایران
        start = now - timedelta(days=days_since_sat)
        return start.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == ScoreRule.CapPeriod.MONTHLY:
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if period == ScoreRule.CapPeriod.YEARLY:
        return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return None  # ONCE


def check_cap(user_id: int, rule: ScoreRule) -> tuple[bool, str]:
    """
    بررسی محدودیت تکرار.
    Returns (allowed, message).
    """
    if not rule.cap_period:
        return True, ""

    if rule.cap_period == ScoreRule.CapPeriod.ONCE:
        if UserScoreLog.objects.filter(
            user_id=user_id,
            transaction_code=rule.code,
        ).exists():
            return False, "شما قبلاً این امتیاز را دریافت کرده‌اید"
        return True, ""

    period_start = get_period_start(rule.cap_period)
    qs = UserScoreLog.objects.filter(
        user_id=user_id,
        transaction_code=rule.code,
        created_at__gte=period_start,
    )

    if rule.cap_count is not None and qs.count() >= rule.cap_count:
        return False, f"سقف {rule.cap_count} بار در این دوره پر شده است"

    if rule.max_amount_per_period is not None:
        total = qs.aggregate(t=Sum("amount"))["t"] or 0
        if total >= rule.max_amount_per_period:
            return False, "سقف امتیاز این دوره پر شده است"

    return True, ""


def build_idempotency_key(
    rule: ScoreRule,
    user_id: int,
    reference_id: Optional[str],
) -> Optional[str]:
    """
    ساخت کلید یکتایی برای جلوگیری از درج تکراری.

    ⚠️ نکته مهم: برای cap_period=DAILY که cap_count > 1 است
    (مثل TREASURE_HUNT با ۳ فرصت)، کلید از تاریخ ساخته نمی‌شود،
    چون کاربر باید بتواند ۳ بار در یک روز ثبت کند.
    """
    if rule.cap_period == ScoreRule.CapPeriod.ONCE:
        return f"{rule.code}:user_{user_id}"

    if (
        rule.cap_period == ScoreRule.CapPeriod.DAILY
        and rule.cap_count == 1
    ):
        return f"{rule.code}:user_{user_id}:{timezone.localdate().isoformat()}"

    if reference_id:
        return f"{rule.code}:ref_{reference_id}"

    return None