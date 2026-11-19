# Path: applications/visit/clean_data.py

# applications/visit/clean_data.py

import re

from django.utils import timezone

from applications.core.forms import coerce_datetime
from applications.user.models import User

from .models import RequestVisit, Visit

_MOBILE_RE = re.compile(r"^09\d{9}$")


# ═══════════════════════════════════════════════════════════
# VISIT
# ═══════════════════════════════════════════════════════════
def visit__clean__data(post, current_visit=None):
    errors = []

    # ─── تاریخ (اجباری) ──────────────────────────────
    date = None
    raw_date = (post.get("date") or "").strip()
    if not raw_date:
        errors.append("تاریخ بازدید الزامی است")
    else:
        date = coerce_datetime(raw_date)
        if date is None:
            errors.append("تاریخ بازدید نامعتبر است")
        elif current_visit is None and date < timezone.now():
            errors.append("تاریخ بازدید نمی‌تواند در گذشته باشد")

    # ─── ظرفیت (اختیاری) ──────────────────────────────
    capacity = None
    raw_capacity = (post.get("capacity") or "").strip()
    if raw_capacity:
        if not raw_capacity.isdigit():
            errors.append("ظرفیت باید عدد باشد")
        else:
            capacity = int(raw_capacity)
            if capacity <= 0:
                errors.append("ظرفیت باید بزرگ‌تر از صفر باشد")

    # ─── فعال ─────────────────────────────────────────
    is_active = str(post.get("is_active", "")).lower() in ("on", "true", "1")

    if errors:
        return {}, errors

    return {
        "date": date,
        "capacity": capacity,
        "is_active": is_active,
    }, []


# ═══════════════════════════════════════════════════════════
# REQUEST VISIT
# ═══════════════════════════════════════════════════════════
def request__clean__data(post, current_request=None):
    errors = []

    # ─── کاربر ────────────────────────────────────────
    user_id = (post.get("user") or "").strip()
    user = User.objects.filter(pk=user_id, is_active=True).first() if user_id.isdigit() else None
    if not user:
        errors.append("کاربر انتخاب‌شده معتبر نیست")

    # ─── بازدید ───────────────────────────────────────
    visit_id = (post.get("visit") or "").strip()
    visit = Visit.objects.filter(pk=visit_id).first() if visit_id.isdigit() else None
    if not visit:
        errors.append("بازدید انتخاب‌شده معتبر نیست")

    # ─── یکتایی (user, visit) ────────────────────────
    if user and visit:
        qs = RequestVisit.objects.filter(user=user, visit=visit)
        if current_request is not None:
            qs = qs.exclude(pk=current_request.pk)
        if qs.exists():
            errors.append("این کاربر قبلاً برای این بازدید درخواست داده است")

    # ─── همراه ───────────────────────────────────────
    have_companion = str(post.get("have_companion", "")).lower() in ("on", "true", "1")
    companion_name = (post.get("companion_name") or "").strip() or None
    companion_family = (post.get("companion_family") or "").strip() or None
    companion_mobile = (post.get("companion_mobile") or "").strip() or None

    if have_companion:
        if not companion_name:
            errors.append("نام همراه الزامی است")
        if not companion_family:
            errors.append("نام خانوادگی همراه الزامی است")
        if not companion_mobile:
            errors.append("موبایل همراه الزامی است")
        elif not _MOBILE_RE.match(companion_mobile):
            errors.append("فرمت موبایل همراه نامعتبر است (مثال: 09121234567)")
    else:
        # اگر همراه ندارد، فیلدهای همراه پاک می‌شوند
        companion_name = companion_family = companion_mobile = None

    if errors:
        return {}, errors

    return {
        "user": user,
        "visit": visit,
        "have_companion": have_companion,
        "companion_name": companion_name,
        "companion_family": companion_family,
        "companion_mobile": companion_mobile,
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