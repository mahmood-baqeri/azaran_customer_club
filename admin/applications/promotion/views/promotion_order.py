# Path: applications/promotion/views/promotion_order.py

# applications/promotion/views/promotion_order.py

import json
import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from applications.core.utils import response_msg
from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess
from applications.core.validators import is_valid_date

from ..clean_data import (
    order__clean__assign,
    order__clean__status,
)
from ..forms import OrderAssignForm
from ..models import Promotion, PromotionOrder
from ..repositories import (
    order__assign,
    order__available_transitions,
    order__change_status,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Filter helper — بین لیست و اکسل مشترک
# ═══════════════════════════════════════════════════════════
def _filtered_promotion_orders_qs(request):
    qs = PromotionOrder.objects.select_related("user", "promotion", "assigned_to")

    q = (request.GET.get("q") or "").strip()
    if q:
        cond = (
            Q(user__mobile__icontains=q)
            | Q(receiver_name__icontains=q)
            | Q(receiver_phone__icontains=q)
            | Q(tracking_code__icontains=q)
            | Q(promotion__title__icontains=q)
        )
        if q.isdigit():
            cond |= Q(id=int(q))
        qs = qs.filter(cond)

    filter_val = (request.GET.get("filter") or "").strip()
    if filter_val in dict(PromotionOrder.Status.choices):
        qs = qs.filter(status=filter_val)

    filter2_val = (request.GET.get("filter2") or "").strip()
    if filter2_val.isdigit():
        qs = qs.filter(promotion_id=int(filter2_val))

    df = request.GET.get("filterDateStart")
    dt = request.GET.get("filterDateEnd")
    if df and is_valid_date(df):
        qs = qs.filter(created_at__date__gte=df)
    if dt and is_valid_date(dt):
        qs = qs.filter(created_at__date__lte=dt)

    sort = request.GET.get("sort", "desc")
    qs = qs.order_by("id") if sort == "asc" else qs.order_by("-id")

    return qs, q, filter_val, filter2_val, df, dt, sort


def _user_name(u):
    if not u:
        return ""
    return getattr(u, "full_name", None) or u.get_full_name() or ""


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def order_index(request):
    RequiredAccess(request, "PromotionOrderRead")

    qs, q, filter_val, filter2_val, df, dt, sort = _filtered_promotion_orders_qs(request)

    try:
        count = int(request.GET.get("count", "20"))
    except ValueError:
        count = 20

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": "لیست سفارشات پک تبلیغاتی",
        "searchUrl": reverse("app_promotion:order_index"),
        "exportUrl": reverse("app_promotion:order_export"),   # ← جدید
        "searchText": q,
        "searchSort": sort,
        "searchCount": count,
        "filterDate": 1,
        "filterDateStart": df or "",
        "filterDateEnd": dt or "",
        "theFilterItems": list(PromotionOrder.Status.choices),
        "filter": filter_val,
        "theFilterItems2": [
            (str(p.id), p.title)
            for p in Promotion.objects.filter(is_active=True).only("id", "title")
        ],
        "filter2": filter2_val,
        "all": page,
        "total": qs.count(),
    }
    return render(request, "pages/promotion/all_promotion_orders.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT — خروجی اکسل با تمام فیلترها
# ═══════════════════════════════════════════════════════════
@is_admin_required
def order_export(request):
    RequiredAccess(request, "PromotionOrderRead")

    qs, *_ = _filtered_promotion_orders_qs(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "سفارشات اقلام تبلیغاتی"
    ws.sheet_view.rightToLeft = True

    headers = [
        "#",
        "کاربر",
        "موبایل کاربر",
        "اقلام تبلیغاتی",
        "گیرنده",
        "تلفن گیرنده",
        "آدرس",
        "کد پستی",
        "وضعیت",
        "کد رهگیری",
        "مسئول پیگیری",
        "تاریخ ثبت",
    ]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for cell in ws[1]:
        cell.font = head_font
        cell.fill = head_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for o in qs.iterator():
        ws.append([
            o.id,
            _user_name(o.user),
            o.user.mobile if o.user else "",
            o.promotion.title if o.promotion else "",
            o.receiver_name,
            o.receiver_phone,
            o.address,
            o.postal_code,
            o.get_status_display(),
            o.tracking_code or "",
            _user_name(o.assigned_to),
            o.created_at.strftime("%Y-%m-%d %H:%M") if o.created_at else "",
        ])

    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"promotion_orders_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    resp = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(resp)
    return resp


# ═══════════════════════════════════════════════════════════
# DETAIL  (بدون تغییر)
# ═══════════════════════════════════════════════════════════
@is_admin_required
def order_detail(request, id):
    RequiredAccess(request, "PromotionOrderRead")
    order = get_object_or_404(
        PromotionOrder.objects.select_related("user", "promotion", "assigned_to"),
        id=id,
    )
    logs = order.promotion_logs_relation.select_related("changed_by").all()

    return render(request, "pages/promotion/promotion_order_detail.html", {
        "order": order,
        "logs": logs,
        "transitions": order__available_transitions(order),
        "assign_form": OrderAssignForm(initial={"assigned_to": order.assigned_to_id}),
    })


# ═══════════════════════════════════════════════════════════
# CHANGE STATUS  (بدون تغییر)
# ═══════════════════════════════════════════════════════════
@is_admin_required
def order_update_status(request, id):
    RequiredAccess(request, "PromotionOrderUpdate")
    if request.method != "POST":
        return redirect("app_promotion:order_detail", id=id)

    order = get_object_or_404(PromotionOrder, id=id)
    cleaned, errors = order__clean__status(request.POST)
    if errors:
        for err in errors:
            response_msg(request, messages.ERROR, err)
        return redirect("app_promotion:order_detail", id=id)

    try:
        order__change_status(order, cleaned, changed_by=request.user)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_promotion:order_detail", id=id)
    except Exception:
        logger.exception("promotion order_update_status failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در تغییر وضعیت")
        return redirect("app_promotion:order_detail", id=id)

    response_msg(
        request,
        messages.SUCCESS,
        f"وضعیت سفارش #{order.id} به «{order.get_status_display()}» تغییر کرد",
    )
    return redirect("app_promotion:order_detail", id=id)


# ═══════════════════════════════════════════════════════════
# ASSIGN  (بدون تغییر)
# ═══════════════════════════════════════════════════════════
@is_admin_required
def order_assign(request, id):
    RequiredAccess(request, "PromotionOrderUpdate")
    if request.method != "POST":
        return redirect("app_promotion:order_detail", id=id)

    order = get_object_or_404(PromotionOrder, id=id)
    cleaned, errors = order__clean__assign(request.POST)
    if errors:
        for err in errors:
            response_msg(request, messages.ERROR, err)
        return redirect("app_promotion:order_detail", id=id)

    try:
        order__assign(order, cleaned["assigned_to"], changed_by=request.user)
    except Exception:
        logger.exception("promotion order_assign failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در واگذاری")
        return redirect("app_promotion:order_detail", id=id)

    response_msg(request, messages.SUCCESS, "مسئول پیگیری به‌روزرسانی شد")
    return redirect("app_promotion:order_detail", id=id)