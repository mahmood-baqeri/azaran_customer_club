# admin/applications/gift/clean_data.py

from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Gift


def gift__clean__data(post):
    """اعتبارسنجی و پاک‌سازی داده‌های فرم هدیه."""
    errors = []

    title = (post.get("title") or "").strip()
    if not title:
        errors.append("عنوان الزامی است")

    # select2Multi ممکن است آرایه یا رشته بفرستد
    for_user_raw = (
        post.getlist("for_user[]")
        or post.getlist("for_user")
        or [post.get("for_user") or ""]
    )
    for_user = (for_user_raw[0] or "").strip() if for_user_raw else ""
    if for_user not in dict(Gift.ForUser.choices):
        errors.append("نوع کاربر نامعتبر است")

    azar_value = (post.get("azar_value") or "0").strip()
    if not azar_value.isdigit():
        errors.append("ارزش آذر نامعتبر است")
        azar_value = "0"

    stock = (post.get("stock") or "0").strip()
    if not stock.lstrip("-").isdigit():
        errors.append("موجودی نامعتبر است")
        stock = "0"

    if errors:
        return {}, errors

    return {
        "title": title,
        "for_user": for_user,
        "description": (post.get("description") or "").strip() or None,
        "azar_value": int(azar_value),
        "stock": int(stock),
        "is_active": str(post.get("is_active", "")).lower() in ("on", "true", "1"),
    }, []