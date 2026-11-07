"""
Cron jobs: EXPIRE, WEEKLY_STREAK, GALLERY_TOP.
"""
import logging
from datetime import timedelta

from django.utils import timezone

from applications.score import api as score_api
from applications.score.models import ScoreRule, UserScore, UserScoreLog

logger = logging.getLogger(__name__)


def run_expire_job():
    """روزانه — انقضای امتیاز کاربران غیرفعال."""
    rule = ScoreRule.objects.filter(code="EXPIRE", is_active=True).first()
    if not rule:
        return
    days = rule.metadata.get("expire_after_days", 365)
    cutoff = timezone.now() - timedelta(days=days)

    recent_earners = UserScoreLog.objects.filter(
        direction=UserScoreLog.Direction.EARNED,
        created_at__gte=cutoff,
    ).values_list("user_id", flat=True)

    stale = UserScore.objects.filter(
        current_balance__gt=0,
    ).exclude(user_id__in=recent_earners)

    for score in stale.iterator():
        try:
            score_api.spend(
                score.user_id, "EXPIRE",
                amount=score.current_balance,
                reason=f"انقضای امتیاز پس از {days} روز بی‌فعالیتی",
                source=UserScoreLog.Source.SYSTEM,
            )
        except Exception:
            logger.exception("EXPIRE failed user=%s", score.user_id)


def run_weekly_streak_job():
    """شنبه‌ها — جایزه استریک هفتگی."""
    from applications.user.models import User

    now = timezone.now()
    last_week_start = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
    last_week_end = now.replace(hour=0, minute=0, second=0, microsecond=0)

    for user in User.objects.filter(is_active=True).iterator():
        days_active = (
            UserScoreLog.objects
            .filter(
                user_id=user.id,
                created_at__gte=last_week_start,
                created_at__lt=last_week_end,
            )
            .dates("created_at", "day")
            .count()
        )
        if days_active >= 7:
            try:
                score_api.award(
                    user, "WEEKLY_STREAK",
                    reason="تکمیل هفته با ۷ روز فعالیت",
                )
            except Exception:
                logger.exception("WEEKLY_STREAK failed user=%s", user.id)


def run_gallery_top_job():
    """شنبه‌ها — عکس برتر هفته."""
    try:
        from applications.gallery.models import GalleryPhoto # pyright: ignore[reportMissingImports]
    except ImportError:
        return

    last_week_start = (timezone.now() - timedelta(days=7)).replace(
        hour=0, minute=0, second=0, microsecond=0,
    )
    winner = (
        GalleryPhoto.objects
        .filter(created_at__gte=last_week_start)
        .order_by("-likes_count")
        .first()
    )
    if winner:
        try:
            score_api.award(
                winner.user, "GALLERY_TOP",
                reference_type="gallery_photo",
                reference_id=str(winner.id),
                reason="عکس برتر هفته",
            )
        except Exception:
            logger.exception("GALLERY_TOP failed")