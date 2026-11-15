# applications/gallery/clean_data.py

from django.core.files.uploadedfile import UploadedFile

from applications.user.models import User

from .models import Gallery

_ALLOWED_EXT = ("jpg", "jpeg", "png", "webp")
_MAX_SIZE = 5 * 1024 * 1024  # 5 MB


# ═══════════════════════════════════════════════════════════
# GALLERY
# ═══════════════════════════════════════════════════════════
def gallery__clean__data(post, files=None, current_gallery=None):
    """اعتبارسنجی فرم پست گالری."""
    errors = []

    # ─── کاربر (فقط در create) ─────────────────────────
    user = None
    if current_gallery is None:
        user_id = (post.get("user") or "").strip()
        user = User.objects.filter(pk=user_id, is_active=True).first() if user_id.isdigit() else None
        if not user:
            errors.append("کاربر انتخاب‌شده معتبر نیست")

    # ─── کپشن و لوکیشن ──────────────────────────────
    caption = (post.get("caption") or "").strip() or None
    if caption and len(caption) > 255:
        errors.append("کپشن حداکثر ۲۵۵ کاراکتر است")

    location = (post.get("location") or "").strip() or None
    if location and len(location) > 255:
        errors.append("لوکیشن حداکثر ۲۵۵ کاراکتر است")

    # ─── تصویر ───────────────────────────────────────
    photo = files.get("photo") if files else None
    if not photo and current_gallery is None:
        errors.append("تصویر الزامی است")
    elif photo:
        if not isinstance(photo, UploadedFile):
            errors.append("فایل نامعتبر است")
        else:
            ext = (photo.name.rsplit(".", 1)[-1] if "." in photo.name else "").lower()
            if ext not in _ALLOWED_EXT:
                errors.append("فرمت تصویر باید یکی از: jpg، jpeg، png، webp باشد")
            if photo.size > _MAX_SIZE:
                errors.append("حجم تصویر حداکثر ۵ مگابایت است")

    if errors:
        return {}, errors

    return {
        "user": user,
        "caption": caption,
        "location": location,
        "photo": photo,
    }, []