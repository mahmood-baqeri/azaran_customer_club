# applications/user/clean_data.py

import re

from applications.core.validators import is_valid_iranian_national_code
from .models import User


MOBILE_RE = re.compile(r"^09\d{9}$")


# ═══════════════════════════════════════════════════════════
# USER (پایه + پروفایل)
# ═══════════════════════════════════════════════════════════
def user__clean__data(post, files=None, current_user=None):
    """اعتبارسنجی و پاک‌سازی فرم کاربر.

    خروجی: (cleaned_user, cleaned_profile, errors, generated_password)
    """
    errors = []

    # ── mobile (اجباری، یکتا، فرمت ایرانی) ──
    mobile = (post.get("mobile") or "").strip()
    if not mobile:
        errors.append("شماره موبایل الزامی است")
    elif not MOBILE_RE.match(mobile):
        errors.append("شماره موبایل نامعتبر است")
    else:
        qs = User.objects.filter(mobile=mobile)
        if current_user is not None:
            qs = qs.exclude(pk=current_user.pk)
        if qs.exists():
            errors.append("این شماره موبایل قبلاً ثبت شده است")

    # ── نام و نام‌خانوادگی ──
    first_name = (post.get("first_name") or "").strip()
    last_name = (post.get("last_name") or "").strip()
    if not first_name:
        errors.append("نام الزامی است")
    if not last_name:
        errors.append("نام خانوادگی الزامی است")

    # ── ایمیل (اختیاری) ──
    email = (post.get("email") or "").strip() or None

    # ── nature ──
    nature = (post.get("nature") or User.UserNature.USER).strip()
    if nature not in dict(User.UserNature.choices):
        errors.append("نوع کاربری نامعتبر است")

    # ── role_ids (JSON list) ──
    role_ids_raw = (
        post.getlist("role_ids[]")
        or post.getlist("role_ids")
        or []
    )
    role_ids = [int(r) for r in role_ids_raw if str(r).isdigit()]

    # ── booleans ──
    is_mobile_verified = str(post.get("is_mobile_verified", "")).lower() in ("on", "true", "1")
    is_active = str(post.get("is_active", "")).lower() in ("on", "true", "1")

    # ── password ──
    password = (post.get("password") or "").strip()
    generated_password = None
    if password and len(password) < 6:
        errors.append("رمز عبور باید حداقل ۶ کاراکتر باشد")

    if not password and current_user is None:
        # کاربر جدید بدون رمز → تولید خودکار
        import secrets
        generated_password = secrets.token_urlsafe(10)
        password = generated_password

    # ── پروفایل ──
    national_code = (post.get("national_code") or "").strip() or None
    if national_code and not is_valid_iranian_national_code(national_code):
        errors.append("کد ملی نامعتبر است")

    birth_date = (post.get("birth_date") or "").strip() or None
    if birth_date:
        import datetime
        try:
            datetime.datetime.strptime(birth_date, "%Y-%m-%d")
        except ValueError:
            errors.append("تاریخ تولد باید به فرمت YYYY-MM-DD باشد")

    gender = (post.get("gender") or "").strip() or None
    if gender and gender not in ("male", "female"):
        errors.append("جنسیت نامعتبر است")

    province_id = post.get("province") or post.get("province_id")
    province_id = int(province_id) if province_id and str(province_id).isdigit() else None

    city_id = post.get("city") or post.get("city_id")
    city_id = int(city_id) if city_id and str(city_id).isdigit() else None

    if errors:
        return {}, {}, errors, None

    cleaned_user = {
        "mobile": mobile,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "nature": nature,
        "role_ids": role_ids,
        "is_mobile_verified": is_mobile_verified,
        "is_active": is_active,
        "password": password,  # ممکن است None باشد (update بدون تغییر)
        "generated_password": generated_password,
    }

    cleaned_profile = {
        "national_code": national_code,
        "birth_date": birth_date,
        "gender": gender,
        "address": (post.get("address") or "").strip() or None,
        "post_code": (post.get("post_code") or "").strip() or None,
        "province_id": province_id,
        "city_id": city_id,
        "job_title": (post.get("job_title") or "").strip() or None,
        "company_name": (post.get("company_name") or "").strip() or None,
    }

    return cleaned_user, cleaned_profile, [], generated_password