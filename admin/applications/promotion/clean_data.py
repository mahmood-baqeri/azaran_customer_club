# applications/promotion/clean_data.py

from .forms import OrderAssignForm, OrderStatusForm


# ═══════════════════════════════════════════════════════════
# PROMOTION (پک)
# ═══════════════════════════════════════════════════════════
def promotion__clean__data(post):
    """اعتبارسنجی فرم پک تبلیغاتی. خروجی: (cleaned, errors)"""
    errors = []

    title = (post.get("title") or "").strip()
    if not title:
        errors.append("عنوان پک الزامی است")

    if errors:
        return {}, errors

    return {
        "title": title,
        "is_active": str(post.get("is_active", "")).lower() in ("on", "true", "1"),
    }, []


# ═══════════════════════════════════════════════════════════
# PROMOTION ITEM (آیتم داخل پک)
# ═══════════════════════════════════════════════════════════
def promotion_item__clean__data(post):
    """اعتبارسنجی فرم آیتم پک. خروجی: (cleaned, errors)"""
    errors = []

    title = (post.get("title") or "").strip()
    if not title:
        errors.append("عنوان آیتم الزامی است")

    if errors:
        return {}, errors

    return {
        "title": title,
        "badge": (post.get("badge") or "").strip() or None,
        "is_active": str(post.get("is_active", "")).lower() in ("on", "true", "1"),
    }, []


# ═══════════════════════════════════════════════════════════
# ORDER — Status
# ═══════════════════════════════════════════════════════════
def order__clean__status(post):
    form = OrderStatusForm(post)
    if not form.is_valid():
        errs = []
        for field, msgs in form.errors.items():
            for m in msgs:
                errs.append(f"{field}: {m}")
        return {}, errs or ["اطلاعات نامعتبر"]

    return {
        "new_status": form.cleaned_data["new_status"],
        "tracking_code": (form.cleaned_data.get("tracking_code") or "").strip(),
        "note": (form.cleaned_data.get("note") or "").strip(),
    }, []


# ═══════════════════════════════════════════════════════════
# ORDER — Assign
# ═══════════════════════════════════════════════════════════
def order__clean__assign(post):
    form = OrderAssignForm(post)
    if not form.is_valid():
        return {}, ["اطلاعات واگذاری نامعتبر است"]
    return {"assigned_to": form.cleaned_data.get("assigned_to")}, []