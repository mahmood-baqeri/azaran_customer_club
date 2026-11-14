# applications/gift/clean_data.py

from .forms import OrderAssignForm, OrderStatusForm
from .models import Gift


# ═══════════════════════════════════════════════════════════
# GIFT
# ═══════════════════════════════════════════════════════════
def gift__clean__data(post):
    """اعتبارسنجی و پاک‌سازی فرم هدیه.

    خروجی: (cleaned_dict, errors_list)
    """
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


# ═══════════════════════════════════════════════════════════
# ORDER — Status Change
# ═══════════════════════════════════════════════════════════
def order__clean__status(post):
    """اعتبارسنجی فرم تغییر وضعیت با استفاده از OrderStatusForm."""
    form = OrderStatusForm(post)
    if not form.is_valid():
        errors = []
        for field, msgs in form.errors.items():
            for m in msgs:
                errors.append(f"{field}: {m}")
        return {}, errors or ["اطلاعات نامعتبر"]

    return {
        "new_status": form.cleaned_data["new_status"],
        "tracking_code": (form.cleaned_data.get("tracking_code") or "").strip(),
        "note": (form.cleaned_data.get("note") or "").strip(),
    }, []


# ═══════════════════════════════════════════════════════════
# ORDER — Assign
# ═══════════════════════════════════════════════════════════
def order__clean__assign(post):
    """اعتبارسنجی فرم واگذاری با استفاده از OrderAssignForm."""
    form = OrderAssignForm(post)
    if not form.is_valid():
        return {}, ["اطلاعات واگذاری نامعتبر است"]
    return {"assigned_to": form.cleaned_data.get("assigned_to")}, []


# ═══════════════════════════════════════════════════════════
# ORDER — Note
# ═══════════════════════════════════════════════════════════
def order__clean__note(post):
    """یادداشت اختیاری است — خالی مجاز است (پاک کردن)."""
    note = (post.get("internal_note") or "").strip()
    return {"internal_note": note or None}, []