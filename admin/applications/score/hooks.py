"""
Hookهای خودکار امتیاز برای رویدادهای User/UserProfile/JobCertificate/FavoriteAnswer.
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from applications.score import api as score_api
# ✅ import مستقیم — نه lazy reference
from applications.user.models import (
    FavoriteAnswer,
    FavoriteQuestion,
    JobCertificate,
    User,
    UserProfile,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SIGNUP
# ═══════════════════════════════════════════════════════════
@receiver(post_save, sender=User)
def on_user_created(sender, instance, created, **kwargs):
    if not created:
        return
    try:
        score_api.award(instance, "SIGNUP", reason="ثبت‌نام کاربر")
    except Exception:
        logger.exception("SIGNUP award failed user=%s", instance.id)


# ═══════════════════════════════════════════════════════════
# PROFILE_PERSONAL_INFO + PROFILE_BIRTH_DATE
# ═══════════════════════════════════════════════════════════
@receiver(post_save, sender=UserProfile)
def on_profile_saved(sender, instance, created, **kwargs):
    user = instance.user

    if user.first_name and user.last_name and instance.national_code:
        try:
            score_api.award(
                user, "PROFILE_PERSONAL_INFO",
                reason="تکمیل مشخصات فردی",
            )
        except Exception:
            logger.exception("PROFILE_PERSONAL_INFO failed user=%s", user.id)

    if instance.birth_date:
        try:
            score_api.award(
                user, "PROFILE_BIRTH_DATE",
                reason="ثبت تاریخ تولد",
            )
        except Exception:
            logger.exception("PROFILE_BIRTH_DATE failed user=%s", user.id)


# ═══════════════════════════════════════════════════════════
# PROFILE_JOB_DOCUMENTS
# ═══════════════════════════════════════════════════════════
@receiver(post_save, sender=JobCertificate)
def on_job_certificate_saved(sender, instance, created, **kwargs):
    if not instance.is_verified:
        return
    try:
        score_api.award(
            instance.user, "PROFILE_JOB_DOCUMENTS",
            reference_type="job_certificate",
            reference_id=str(instance.id),
            reason="تأیید مدارک شغلی",
        )
    except Exception:
        logger.exception("PROFILE_JOB_DOCUMENTS failed cert=%s", instance.id)


# ═══════════════════════════════════════════════════════════
# PROFILE_INTERESTS — فقط یک نسخه (تکراری حذف شد)
# ═══════════════════════════════════════════════════════════
@receiver(post_save, sender=FavoriteAnswer)
def on_favorite_answer_saved(sender, instance, created, **kwargs):
    total_active = FavoriteQuestion.objects.filter(is_active=True).count()
    if total_active == 0:
        return
    answered = instance.user.relation_favorite_answers.filter(
        question__is_active=True,
    ).count()
    if answered >= total_active:
        try:
            score_api.award(
                instance.user, "PROFILE_INTERESTS",
                reason="تکمیل علایق و سلایق",
            )
        except Exception:
            logger.exception("PROFILE_INTERESTS failed user=%s", instance.user_id)