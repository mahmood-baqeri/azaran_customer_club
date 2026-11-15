# applications/score/repositories.py

import logging

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import ScoreRule, UserScore, UserScoreLog

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SCORE RULE
# ═══════════════════════════════════════════════════════════
def score_rule__store(cleaned, item=None):
    if not cleaned:
        raise ValueError("cleaned data is required")

    if item is None:
        item = ScoreRule.objects.create(**cleaned)
    else:
        for k, v in cleaned.items():
            setattr(item, k, v)
        item.save()
    return item


def score_rule__delete(item):
    """حذف قاعده — فقط اگر در قواعد استفاده نشده باشد (خودپاداش)."""
    item.delete()


def score_rule__toggle_active(item):
    item.is_active = not item.is_active
    item.save(update_fields=["is_active", "updated_at"])
    return item.is_active


def seed_default_rules():
    """ایجاد قواعد پیش‌فرض برای کدهایی که قاعده ندارند. Idempotent."""
    defaults = {
        UserScoreLog.TransactionCode.SIGNUP: {
            "calc_type": ScoreRule.CalcType.FIXED,
            "default_amount": 100,
            "cap_period": ScoreRule.CapPeriod.ONCE,
        },
        UserScoreLog.TransactionCode.PROFILE_PERSONAL_INFO: {
            "calc_type": ScoreRule.CalcType.FIXED,
            "default_amount": 50,
            "cap_period": ScoreRule.CapPeriod.ONCE,
        },
        UserScoreLog.TransactionCode.PROFILE_BIRTH_DATE: {
            "calc_type": ScoreRule.CalcType.FIXED,
            "default_amount": 30,
            "cap_period": ScoreRule.CapPeriod.ONCE,
        },
        UserScoreLog.TransactionCode.PROFILE_JOB_DOCUMENTS: {
            "calc_type": ScoreRule.CalcType.FIXED,
            "default_amount": 100,
            "cap_period": ScoreRule.CapPeriod.ONCE,
            "requires_approval": True,
        },
        UserScoreLog.TransactionCode.PROFILE_INTERESTS: {
            "calc_type": ScoreRule.CalcType.FIXED,
            "default_amount": 50,
            "cap_period": ScoreRule.CapPeriod.ONCE,
        },
        UserScoreLog.TransactionCode.INVOICE: {
            "calc_type": ScoreRule.CalcType.PERCENT,
            "default_amount": 5,
            "requires_reference": True,
        },
        UserScoreLog.TransactionCode.REFERRAL: {
            "calc_type": ScoreRule.CalcType.FIXED,
            "default_amount": 450,
            "requires_reference": True,
        },
        UserScoreLog.TransactionCode.DAILY_QUIZ: {
            "calc_type": ScoreRule.CalcType.FIXED,
            "default_amount": 10,
            "cap_period": ScoreRule.CapPeriod.DAILY,
            "cap_count": 1,
        },
        UserScoreLog.TransactionCode.TREASURE_HUNT: {
            "calc_type": ScoreRule.CalcType.FIXED,
            "default_amount": 5,
            "cap_period": ScoreRule.CapPeriod.DAILY,
            "cap_count": 3,
        },
        UserScoreLog.TransactionCode.FORTUNE_WHEEL: {
            "calc_type": ScoreRule.CalcType.RANDOM,
            "default_amount": 5,
            "cap_period": ScoreRule.CapPeriod.DAILY,
            "cap_count": 1,
            "metadata": {
                "options": [0, 5, 10, 20, 50, 100],
                "weights": [30, 25, 20, 15, 8, 2],
            },
        },
        UserScoreLog.TransactionCode.SURVEY: {
            "calc_type": ScoreRule.CalcType.FIXED,
            "default_amount": 30,
            "cap_period": ScoreRule.CapPeriod.MONTHLY,
            "cap_count": 5,
        },
        UserScoreLog.TransactionCode.GIFT_REDEEM: {
            "calc_type": ScoreRule.CalcType.FIXED,
            "default_amount": 0,
            "requires_reference": True,
        },
    }

    created = 0
    for code, opts in defaults.items():
        _, was_created = ScoreRule.objects.get_or_create(code=code, defaults=opts)
        if was_created:
            created += 1
    return created


# ═══════════════════════════════════════════════════════════
# MANUAL ADJUST
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def score__adjust(user, direction, amount, reason, changed_by):
    """تنظیم دستی امتیاز با قفل روی UserScore — اتمیک و idempotent-safe.

    Raises:
        ValueError: در صورت کافی نبودن موجودی برای SPENT
    """
    score, _ = UserScore.objects.select_for_update().get_or_create(user=user)

    balance_before = score.current_balance

    if direction == UserScoreLog.Direction.EARNED:
        balance_after = balance_before + amount
        UserScore.objects.filter(pk=score.pk).update(
            current_balance=F("current_balance") + amount,
            total_earned=F("total_earned") + amount,
        )
    else:
        if balance_before < amount:
            raise ValueError(
                f"موجودی کاربر کافی نیست (موجودی فعلی: {balance_before})"
            )
        balance_after = balance_before - amount
        UserScore.objects.filter(pk=score.pk).update(
            current_balance=F("current_balance") - amount,
            total_spent=F("total_spent") + amount,
        )

    log = UserScoreLog.objects.create(
        user=user,
        transaction_code=UserScoreLog.TransactionCode.ADMIN_ADJUST,
        direction=direction,
        amount=amount,
        balance_before=balance_before,
        balance_after=balance_after,
        source=UserScoreLog.Source.ADMIN,
        created_by=changed_by,
        reason=reason,
    )
    return log