# applications/project/clean_data.py

import re

from django.core.files.uploadedfile import UploadedFile

from applications.core.forms import coerce_datetime

from .models import Attachment, Project

_MOBILE_RE = re.compile(r"^09\d{9}$")


def _posint(post, key):
    raw = (post.get(key) or "").strip()
    if not raw:
        return None, None
    if not raw.isdigit():
        return None, "باید عدد نامنفی باشد"
    return int(raw), None


# ═══════════════════════════════════════════════════════════
# PROJECT
# ═══════════════════════════════════════════════════════════
def project__clean__data(post, files=None, current_project=None):
    """اعتبارسنجی فرم پروژه."""
    errors = []

    type_val = (post.get("type") or "").strip()
    if type_val not in dict(Project.Type.choices):
        errors.append("نوع پروژه نامعتبر است")

    title = (post.get("title") or "").strip()
    if not title:
        errors.append("عنوان پروژه الزامی است")
    elif len(title) > 255:
        errors.append("عنوان حداکثر ۲۵۵ کاراکتر است")

    owner_mobile = (post.get("owner_mobile") or "").strip()
    if owner_mobile and not _MOBILE_RE.match(owner_mobile):
        errors.append("فرمت موبایل مالک نامعتبر است (مثال: 09121234567)")

    numeric = {}
    for key, label in (
        ("unit_count", "تعداد واحد"),
        ("number_water_taps", "تعداد شیرآبی"),
        ("number_gas_taps", "تعداد شیرگازی"),
        ("number_connections", "تعداد اتصالات"),
        ("pipe_length", "متراژ لوله"),
    ):
        val, err = _posint(post, key)
        numeric[key] = val
        if err:
            errors.append(f"{label} {err}")

    completion_at = None
    raw_completion = (post.get("completion_at") or "").strip()
    if raw_completion:
        completion_at = coerce_datetime(raw_completion)
        if completion_at is None:
            errors.append("تاریخ اتمام پروژه نامعتبر است")

    if errors:
        return {}, errors

    return {
        "type": type_val,
        "title": title,
        "address": (post.get("address") or "").strip() or None,
        "owner_mobile": owner_mobile or None,
        "unit_count": numeric["unit_count"],
        "number_water_taps": numeric["number_water_taps"],
        "number_gas_taps": numeric["number_gas_taps"],
        "number_connections": numeric["number_connections"],
        "pipe_length": numeric["pipe_length"],
        "completion_at": completion_at,
    }, []


# ═══════════════════════════════════════════════════════════
# COLLEAGUE
# ═══════════════════════════════════════════════════════════
def colleague__clean__data(post):
    errors = []

    mobile = (post.get("user_mobile") or "").strip()
    if not mobile or not _MOBILE_RE.match(mobile):
        errors.append("شماره موبایل همکار معتبر نیست (مثال: 09121234567)")

    raw = (post.get("percent") or "").strip()
    percent = 0
    if not raw.isdigit():
        errors.append("درصد باید عدد باشد")
    else:
        percent = int(raw)
        if not (1 <= percent <= 100):
            errors.append("درصد باید بین ۱ تا ۱۰۰ باشد")

    if errors:
        return {}, errors
    return {"user_mobile": mobile, "percent": percent}, []


# ═══════════════════════════════════════════════════════════
# ATTACHMENT
# ═══════════════════════════════════════════════════════════
def attachment__clean__data(post, files):
    errors = []

    file_type = (post.get("type") or "").strip()
    if file_type not in dict(Attachment.FileType.choices):
        errors.append("نوع فایل نامعتبر است")

    upload = files.get("file") if files else None
    if not upload:
        errors.append("فایل الزامی است")
    elif not isinstance(upload, UploadedFile):
        errors.append("فایل نامعتبر است")
    elif upload.size > 20 * 1024 * 1024:
        errors.append("حجم فایل حداکثر ۲۰ مگابایت است")

    if errors:
        return {}, errors

    return {
        "file_type": file_type,
        "file": upload,
        "file_size": upload.size,
        "mime_type": getattr(upload, "content_type", "") or "",
    }, []


# ═══════════════════════════════════════════════════════════
# REJECT
# ═══════════════════════════════════════════════════════════
def reject__clean__data(post):
    reason = (post.get("reason") or "").strip()
    if not reason:
        return {}, ["دلیل رد الزامی است"]
    if len(reason) > 2000:
        return {}, ["دلیل رد حداکثر ۲۰۰۰ کاراکتر است"]
    return {"reason": reason}, []