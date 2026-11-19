# Path: applications/learn/clean_data.py

# applications/review/clean_data.py

from django.core.files.uploadedfile import UploadedFile

from .models import Learn

_ALLOWED_EXT = ("jpg", "jpeg", "png", "webp")
_MAX_SIZE = 5 * 1024 * 1024  # 5 MB


# ═══════════════════════════════════════════════════════════
# LEARN
# ═══════════════════════════════════════════════════════════
def learn__clean__data(post, files=None, current_learn=None):
    """اعتبارسنجی فرم آموزش."""
    errors = []

    # ─── عنوان ────────────────────────────────────────
    title = (post.get("title") or "").strip()
    if not title:
        errors.append("عنوان الزامی است")
    elif len(title) > 255:
        errors.append("عنوان حداکثر ۲۵۵ کاراکتر است")

    # ─── متن کامل ────────────────────────────────────
    full_text = (post.get("full_text") or "").strip()
    if not full_text:
        errors.append("متن کامل الزامی است")

    # ─── عرض صفحه ────────────────────────────────────
    size = (post.get("size") or "").strip()
    if size not in dict(Learn.Size.choices):
        errors.append("عرض صفحه نامعتبر است")

    # ─── زمان مطالعه (اختیاری) ────────────────────────
    time_val = None
    raw_time = (post.get("time") or "").strip()
    if raw_time:
        if not raw_time.isdigit():
            errors.append("زمان مطالعه باید عدد باشد")
        else:
            time_val = int(raw_time)
            if time_val > 10000:
                errors.append("زمان مطالعه نامعتبر است")

    # ─── زیرمتن و کپشن (اختیاری) ──────────────────────
    sub_text = (post.get("sub_text") or "").strip() or None
    caption = (post.get("caption") or "").strip() or None

    # ─── تصویر ───────────────────────────────────────
    photo = files.get("photo") if files else None
    if not photo and current_learn is None:
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
        "title": title,
        "sub_text": sub_text,
        "caption": caption,
        "full_text": full_text,
        "is_active": str(post.get("is_active", "")).lower() in ("on", "true", "1"),
        "size": size,
        "time": time_val,
        "photo": photo,
    }, []