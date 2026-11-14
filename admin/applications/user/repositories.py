# applications/user/repositories.py

import logging

from django.db import transaction
from django.utils import timezone

from applications.core.utils import handle_get_file

from .models import JobCertificate, User, UserProfile

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# USER — Store (create / update)
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def user__store(request, cleaned_user, cleaned_profile, item=None):
    """ذخیره/به‌روزرسانی کاربر + پروفایل در یک تراکنش.

    Args:
        request: HttpRequest (برای آواتار)
        cleaned_user: dict خروجی user__clean__data[0]
        cleaned_profile: dict خروجی user__clean__data[1]
        item: نمونه‌ی موجود برای update؛ None برای create

    Returns:
        (user, generated_password)
    """
    if not cleaned_user:
        raise ValueError("cleaned_user is required")

    user_fields = dict(cleaned_user)
    password = user_fields.pop("password", None)
    generated_password = user_fields.pop("generated_password", None)

    new_avatar = handle_get_file(request, "avatar")

    if item is None:
        item = User(**user_fields)
        if password:
            item.set_password(password)
        else:
            item.set_unusable_password()
        if new_avatar:
            item.avatar = new_avatar
        item.save()
    else:
        for k, v in user_fields.items():
            setattr(item, k, v)
        if password:
            item.set_password(password)
        if new_avatar:
            item.avatar = new_avatar
        item.save()

    # ── پروفایل ──
    profile, _created = UserProfile.objects.get_or_create(user=item)

    for k, v in cleaned_profile.items():
        if k == "birth_date" and v:
            import datetime
            try:
                v = datetime.datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                v = None
        setattr(profile, k, v)
    profile.save()

    return item, generated_password


# ═══════════════════════════════════════════════════════════
# USER — Delete
# ═══════════════════════════════════════════════════════════
def user__delete(user):
    """حذف کاربر — روی SoftDeleteModel، soft delete انجام می‌شود."""
    user.delete()


# ═══════════════════════════════════════════════════════════
# USER — Verify mobile (action)
# ═══════════════════════════════════════════════════════════
def user__verify_mobile(user):
    """تایید دستی موبایل — idempotent"""
    if user.is_mobile_verified:
        return False
    user.is_mobile_verified = True
    user.save(update_fields=["is_mobile_verified", "updated_at"])
    return True


# ═══════════════════════════════════════════════════════════
# USER — Toggle active
# ═══════════════════════════════════════════════════════════
def user__toggle_active(user):
    """فعال/غیرفعال — idempotent"""
    user.is_active = not user.is_active
    user.save(update_fields=["is_active", "updated_at"])
    return user.is_active


# ═══════════════════════════════════════════════════════════
# CERTIFICATE — Approve / Reject
# ═══════════════════════════════════════════════════════════
def certificate__approve(cert: JobCertificate):
    """تایید مدرک — سیگنال post_save امتیاز می‌دهد (idempotent بر اساس reference)."""
    if cert.is_verified:
        return False
    cert.is_verified = True
    cert.verified_at = timezone.now()
    cert.save(update_fields=["is_verified", "verified_at", "updated_at"])
    return True


def certificate__reject(cert: JobCertificate):
    """رد مدرک — امتیاز قبلی استرداد نمی‌شود (طبق طراحی)."""
    if not cert.is_verified:
        return False
    cert.is_verified = False
    cert.verified_at = None
    cert.save(update_fields=["is_verified", "verified_at", "updated_at"])
    return True