# applications/gift/views/order.py

import json
import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from applications.core.utils import response_msg
from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess
from applications.core.validators import is_valid_date

from ..clean_data import (
    order__clean__assign,
    order__clean__note,
    order__clean__status,
)
from ..forms import OrderAssignForm
from ..models import Gift, GiftOrder
from ..repositories import (
    order__assign,
    order__available_transitions,
    order__change_status,
    order__save_note,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def order_index(request):
    RequiredAccess(request, "GiftOrderRead")

    qs = GiftOrder.objects.select_related("user", "gift", "assigned_to")

    q = (request.GET.get("q") or "").strip()
    if q:
        cond = (
            Q(user__mobile__icontains=q)
            | Q(receiver_name__icontains=q)
            | Q(receiver_phone__icontains=q)
            | Q(tracking_code__icontains=q)
            | Q(gift__title__icontains=q)
        )
        if q.isdigit():
            cond |= Q(id=int(q))
        qs = qs.filter(cond)

    filter_val = (request.GET.get("filter") or "").strip()
    if filter_val in dict(GiftOrder.Status.choices):
        qs = qs.filter(status=filter_val)

    filter2_val = (request.GET.get("filter2") or "").strip()
    if filter2_val.isdigit():
        qs = qs.filter(gift_id=int(filter2_val))

    df = request.GET.get("filterDateStart")
    dt = request.GET.get("filterDateEnd")
    if df and is_valid_date(df):
        qs = qs.filter(created_at__date__gte=df)
    if dt and is_valid_date(dt):
        qs = qs.filter(created_at__date__lte=dt)

    sort = request.GET.get("sort", "desc")
    qs = qs.order_by("id") if sort == "asc" else qs.order_by("-id")

    try:
        count = int(request.GET.get("count", "20"))
    except ValueError:
        count = 20

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": "لیست سفارشات هدایا",
        "searchUrl": reverse("app_gift:order_index"),
        "searchText": q,
        "searchSort": sort,
        "searchCount": count,

        "filterDate": 1,
        "filterDateStart": df or "",
        "filterDateEnd": dt or "",

        "theFilterItems": list(GiftOrder.Status.choices),
        "filter": filter_val,

        "theFilterItems2": [
            (str(g.id), g.title)
            for g in Gift.objects.filter(is_active=True).only("id", "title")
        ],
        "filter2": filter2_val,

        "all": page,
        "total": qs.count(),
    }
    return render(request, "pages/gift/all_gift_orders.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# DETAIL
# ═══════════════════════════════════════════════════════════
@is_admin_required
def order_detail(request, id):
    RequiredAccess(request, "GiftOrderRead")
    order = get_object_or_404(
        GiftOrder.objects.select_related("user", "gift", "assigned_to"),
        id=id,
    )
    logs = order.logs.select_related("changed_by").all()

    return render(request, "pages/gift/gift_order_detail.html", {
        "order": order,
        "logs": logs,
        "transitions": order__available_transitions(order),
        "assign_form": OrderAssignForm(initial={"assigned_to": order.assigned_to_id}),
    })


# ═══════════════════════════════════════════════════════════
# CHANGE STATUS
# ═══════════════════════════════════════════════════════════
@is_admin_required
def order_update_status(request, id):
    RequiredAccess(request, "GiftOrderUpdate")
    if request.method != "POST":
        return redirect("app_gift:order_detail", id=id)

    order = get_object_or_404(GiftOrder, id=id)
    cleaned, errors = order__clean__status(request.POST)
    if errors:
        for err in errors:
            response_msg(request, messages.ERROR, err)
        return redirect("app_gift:order_detail", id=id)

    try:
        order__change_status(order, cleaned, changed_by=request.user)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_gift:order_detail", id=id)
    except Exception:
        logger.exception("order_update_status failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در تغییر وضعیت")
        return redirect("app_gift:order_detail", id=id)

    response_msg(
        request,
        messages.SUCCESS,
        f"وضعیت سفارش #{order.id} به «{order.get_status_display()}» تغییر کرد",
    )
    return redirect("app_gift:order_detail", id=id)


# ═══════════════════════════════════════════════════════════
# ASSIGN
# ═══════════════════════════════════════════════════════════
@is_admin_required
def order_assign(request, id):
    RequiredAccess(request, "GiftOrderUpdate")
    if request.method != "POST":
        return redirect("app_gift:order_detail", id=id)

    order = get_object_or_404(GiftOrder, id=id)
    cleaned, errors = order__clean__assign(request.POST)
    if errors:
        for err in errors:
            response_msg(request, messages.ERROR, err)
        return redirect("app_gift:order_detail", id=id)

    try:
        order__assign(order, cleaned["assigned_to"], changed_by=request.user)
    except Exception:
        logger.exception("order_assign failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در واگذاری")
        return redirect("app_gift:order_detail", id=id)

    response_msg(request, messages.SUCCESS, "مسئول پیگیری به‌روزرسانی شد")
    return redirect("app_gift:order_detail", id=id)


# ═══════════════════════════════════════════════════════════
# NOTE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def order_note(request, id):
    RequiredAccess(request, "GiftOrderUpdate")
    if request.method != "POST":
        return redirect("app_gift:order_detail", id=id)

    order = get_object_or_404(GiftOrder, id=id)
    cleaned, errors = order__clean__note(request.POST)
    if errors:
        for err in errors:
            response_msg(request, messages.ERROR, err)
        return redirect("app_gift:order_detail", id=id)

    try:
        order__save_note(order, cleaned["internal_note"])
    except Exception:
        logger.exception("order_note failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در ذخیره یادداشت")
        return redirect("app_gift:order_detail", id=id)

    response_msg(request, messages.SUCCESS, "یادداشت ذخیره شد")
    return redirect("app_gift:order_detail", id=id)