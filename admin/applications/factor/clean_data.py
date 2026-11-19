# Path: applications/factor/clean_data.py

# applications/factor/clean_data.py

import re

from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone

from applications.core.forms import coerce_datetime

from .models import Factor

_PHONE_RE = re.compile(r"^(09\d{9}|0\d{2,3}\d{7,8})$")
_ALLOWED_EXT = ("jpg", "jpeg", "png", "webp", "pdf")


# ═══════════════════════════════════════════════════════════
# FACTOR
# ═══════════════════════════════════════════════════════════
def factor__clean__data(post, files=None, current_factor=None):
    """اعتبارسنجی فرم فاکتور."""
    errors = []

    # ─── شماره فاکتور (اختیاری، یکتا) ────────────────────
    invoice_number = (post.get("invoice_number") or "").strip() or None
    if invoice_number:
        if len(invoice_number) > 64:
            errors.append("شماره فاکتور حداکثر ۶۴ کاراکتر است")
        else:
            qs = Factor.objects.filter(invoice_number=invoice_number)
            if current_factor is not None:
                qs = qs.exclude(pk=current_factor.pk)
            if qs.exists():
                errors.append("این شماره فاکتور قبلاً ثبت شده است")

    # ─── مبلغ ─────────────────────────────────────────────
    amount = None
    raw_amount = (post.get("amount") or "").strip()
    if raw_amount:
        if not raw_amount.isdigit():
            errors.append("مبلغ فاکتور باید عدد صحیح باشد")
        else:
            amount = int(raw_amount)
            if amount <= 0:
                errors.append("مبلغ فاکتور باید بزرگ‌تر از صفر باشد")

    # ─── تاریخ صدور ──────────────────────────────────────
    invoice_issue_at = None
    raw_issue = (post.get("invoice_issue_at") or "").strip()
    if raw_issue:
        invoice_issue_at = coerce_datetime(raw_issue)
        if invoice_issue_at is None:
            errors.append("تاریخ صدور فاکتور نامعتبر است")
        elif invoice_issue_at > timezone.now():
            errors.append("تاریخ صدور فاکتور نمی‌تواند در آینده باشد")

    # ─── متره ─────────────────────────────────────────────
    def _opt_int(key, label):
        raw = (post.get(key) or "").strip()
        if not raw:
            return None
        if not raw.isdigit():
            errors.append(f"{label} باید عدد نامنفی باشد")
            return None
        return int(raw)

    number_water_taps = _opt_int("number_water_taps", "تعداد شیر")
    number_connections = _opt_int("number_connections", "تعداد اتصالات")
    pipe_length = _opt_int("pipe_length", "متراژ لوله")

    # ─── اطلاعات فروشگاه ─────────────────────────────────
    shop_name = (post.get("shop_name") or "").strip() or None
    seller_phone = (post.get("seller_phone") or "").strip() or None
    if seller_phone and not _PHONE_RE.match(seller_phone):
        errors.append("فرمت تلفن فروشنده نامعتبر است (موبایل 09xxxxxxxxx یا تلفن ثابت 0xxxxxxxxx)")
    seller_address = (post.get("seller_address") or "").strip() or None

    # ─── فایل تصویر/PDF ───────────────────────────────────
    photo = files.get("photo") if files else None
    if not photo and current_factor is None:
        errors.append("فایل فاکتور الزامی است")
    elif photo:
        if not isinstance(photo, UploadedFile):
            errors.append("فایل نامعتبر است")
        else:
            ext = (photo.name.rsplit(".", 1)[-1] if "." in photo.name else "").lower()
            if ext not in _ALLOWED_EXT:
                errors.append("فرمت فایل باید یکی از: jpg، jpeg، png، webp، pdf باشد")
            if photo.size > 10 * 1024 * 1024:
                errors.append("حجم فایل حداکثر ۱۰ مگابایت است")

    if errors:
        return {}, errors

    return {
        "invoice_number": invoice_number,
        "amount": amount,
        "invoice_issue_at": invoice_issue_at,
        "number_water_taps": number_water_taps,
        "number_connections": number_connections,
        "pipe_length": pipe_length,
        "shop_name": shop_name,
        "seller_phone": seller_phone,
        "seller_address": seller_address,
        "photo": photo,
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