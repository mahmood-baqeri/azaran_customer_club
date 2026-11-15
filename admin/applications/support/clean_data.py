# applications/support/clean_data.py

from django.core.files.uploadedfile import UploadedFile

from applications.user.models import User

from .models import Support

_ALLOWED_EXT = ("jpg", "jpeg", "png", "webp", "pdf", "zip", "rar")
_MAX_SIZE = 10 * 1024 * 1024  # 10 MB


def _validate_file(upload):
    """اعتبارسنجی فایل پیوست — خروجی: error یا None."""
    if not upload:
        return None
    if not isinstance(upload, UploadedFile):
        return "فایل نامعتبر است"
    ext = (upload.name.rsplit(".", 1)[-1] if "." in upload.name else "").lower()
    if ext not in _ALLOWED_EXT:
        return "فرمت فایل مجاز نیست (jpg، png، webp، pdf، zip، rar)"
    if upload.size > _MAX_SIZE:
        return "حجم فایل حداکثر ۱۰ مگابایت است"
    return None


# ═══════════════════════════════════════════════════════════
# SUPPORT (create)
# ═══════════════════════════════════════════════════════════
def support__clean__data(post, files=None):
    """اعتبارسنجی فرم ایجاد تیکت. کاربر + پیام اول هم بررسی می‌شود."""
    errors = []

    # ─── کاربر ────────────────────────────────────────
    user_id = (post.get("user") or "").strip()
    user = User.objects.filter(pk=user_id, is_active=True).first() if user_id.isdigit() else None
    if not user:
        errors.append("کاربر انتخاب‌شده معتبر نیست")

    # ─── دسته ─────────────────────────────────────────
    category = (post.get("category") or "").strip()
    if category not in dict(Support.Category.choices):
        errors.append("دسته‌بندی نامعتبر است")

    # ─── اولویت ───────────────────────────────────────
    priority = (post.get("priority") or "").strip()
    if priority not in dict(Support.Priority.choices):
        errors.append("اولویت نامعتبر است")

    # ─── موضوع ────────────────────────────────────────
    subject = (post.get("subject") or "").strip()
    if not subject:
        errors.append("موضوع تیکت الزامی است")
    elif len(subject) > 255:
        errors.append("موضوع حداکثر ۲۵۵ کاراکتر است")

    # ─── پیام اول ─────────────────────────────────────
    first_message_text = (post.get("first_message_text") or "").strip()
    first_message_file = files.get("first_message_file") if files else None

    if not first_message_text and not first_message_file:
        errors.append("متن پیام اول یا فایل پیوست الزامی است")

    file_err = _validate_file(first_message_file)
    if file_err:
        errors.append(file_err)

    if errors:
        return {}, errors

    return {
        "user": user,
        "category": category,
        "priority": priority,
        "subject": subject,
        "first_message_text": first_message_text,
        "first_message_file": first_message_file,
    }, []


# ═══════════════════════════════════════════════════════════
# SUPPORT (update — فقط category، priority، subject)
# ═══════════════════════════════════════════════════════════
def support__clean__update__data(post):
    errors = []

    category = (post.get("category") or "").strip()
    if category not in dict(Support.Category.choices):
        errors.append("دسته‌بندی نامعتبر است")

    priority = (post.get("priority") or "").strip()
    if priority not in dict(Support.Priority.choices):
        errors.append("اولویت نامعتبر است")

    subject = (post.get("subject") or "").strip()
    if not subject:
        errors.append("موضوع تیکت الزامی است")
    elif len(subject) > 255:
        errors.append("موضوع حداکثر ۲۵۵ کاراکتر است")

    if errors:
        return {}, errors

    return {
        "category": category,
        "priority": priority,
        "subject": subject,
    }, []


# ═══════════════════════════════════════════════════════════
# SUPPORT MESSAGE
# ═══════════════════════════════════════════════════════════
def message__clean__data(post, files=None):
    errors = []

    text = (post.get("text") or "").strip()
    upload = files.get("file") if files else None

    if not text and not upload:
        errors.append("متن پیام یا فایل پیوست الزامی است")

    if len(text) > 5000:
        errors.append("متن پیام حداکثر ۵۰۰۰ کاراکتر است")

    file_err = _validate_file(upload)
    if file_err:
        errors.append(file_err)

    if errors:
        return {}, errors

    return {"text": text, "file": upload}, []


# ═══════════════════════════════════════════════════════════
# CLOSE
# ═══════════════════════════════════════════════════════════
def close__clean__data(post):
    reason = (post.get("reason") or "").strip()
    if len(reason) > 2000:
        return {}, ["دلیل بستن حداکثر ۲۰۰۰ کاراکتر است"]
    return {"reason": reason or None}, []