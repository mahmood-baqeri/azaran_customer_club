# applications/gift/views.py
import json
import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from applications.core.fileManager import deleteFile
from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess
from applications.core.utils import redirect_back
from applications.core.validators import is_valid_date

from ..forms import OrderAssignForm, OrderStatusForm, gift_form_items
from ..models import Gift, GiftOrder, GiftOrderLog

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# ORDER LIST
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

    # فیلتر اول: وضعیت
    filter_val = (request.GET.get("filter") or "").strip()
    if filter_val in dict(GiftOrder.Status.choices):
        qs = qs.filter(status=filter_val)

    # فیلتر دوم: هدیه
    filter2_val = (request.GET.get("filter2") or "").strip()
    if filter2_val.isdigit():
        qs = qs.filter(gift_id=int(filter2_val))

    # بازه تاریخ
    df = request.GET.get("filterDateStart")
    dt = request.GET.get("filterDateEnd")
    if df and is_valid_date(df):
        qs = qs.filter(created_at__date__gte=df)
    if dt and is_valid_date(dt):
        qs = qs.filter(created_at__date__lte=dt)

    # مرتب‌سازی
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

        # فیلتر تاریخ
        "filterDate": 1,
        "filterDateStart": df or "",
        "filterDateEnd": dt or "",

        # فیلتر اول (وضعیت)
        "theFilterItems": list(GiftOrder.Status.choices),
        "filter": filter_val,

        # فیلتر دوم (هدیه)
        "theFilterItems2": [(str(g.id), g.title) for g in Gift.objects.filter(is_active=True).only("id", "title")],
        "filter2": filter2_val,

        "all": page,
        "total": qs.count(),
    }
    return render(request, "pages/gift/all_gift_orders.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# ORDER DETAIL / ACTIONS (بدون تغییر ساختار قبلی)
# ═══════════════════════════════════════════════════════════
@is_admin_required
def order_detail(request, id):
    RequiredAccess(request, "GiftOrderRead")
    order = get_object_or_404(
        GiftOrder.objects.select_related("user", "gift", "assigned_to"), id=id
    )
    logs = order.logs.select_related("changed_by").all()

    return render(request, "pages/gift/gift_order_detail.html", {
        "order": order,
        "logs": logs,
        "transitions": _available_transitions(order),
        "assign_form": OrderAssignForm(initial={"assigned_to": order.assigned_to_id}),
    })


@is_admin_required
def order_update_status(request, id):
    RequiredAccess(request, "GiftOrderUpdate")
    if request.method != "POST":
        return redirect("app_gift:order_detail", id=id)

    order = get_object_or_404(GiftOrder, id=id)
    form = OrderStatusForm(request.POST)
    if not form.is_valid():
        messages.error(request, "اطلاعات نامعتبر")
        return redirect("app_gift:order_detail", id=id)

    new_status = form.cleaned_data["new_status"]
    tracking_code = (form.cleaned_data.get("tracking_code") or "").strip()
    note = (form.cleaned_data.get("note") or "").strip()

    if not _is_valid_transition(order.status, new_status):
        messages.error(request, "تغییر وضعیت نامعتبر است")
        return redirect("app_gift:order_detail", id=id)

    if new_status == GiftOrder.Status.SHIPPED and not tracking_code:
        messages.error(request, "برای ارسال، کد رهگیری الزامی است")
        return redirect("app_gift:order_detail", id=id)

    try:
        with transaction.atomic():
            old_status = order.status
            order.status = new_status
            update_fields = ["status", "updated_at"]
            if tracking_code:
                order.tracking_code = tracking_code
                update_fields.append("tracking_code")

            _apply_status_side_effects(order, old_status, new_status)

            order.save(update_fields=update_fields)
            GiftOrderLog.objects.create(
                order=order, from_status=old_status, to_status=new_status,
                changed_by=request.user, action="status_change", note=note or None,
            )
    except ValueError as e:
        messages.error(request, str(e))
        return redirect("app_gift:order_detail", id=id)
    except Exception:
        logger.exception("order_update_status failed order=%s", order.id)
        messages.error(request, "خطا در تغییر وضعیت")
        return redirect("app_gift:order_detail", id=id)

    messages.success(request, f"وضعیت سفارش #{order.id} به «{order.get_status_display()}» تغییر کرد")
    return redirect("app_gift:order_detail", id=id)


@is_admin_required
def order_assign(request, id):
    RequiredAccess(request, "GiftOrderUpdate")
    if request.method != "POST":
        return redirect("app_gift:order_detail", id=id)

    order = get_object_or_404(GiftOrder, id=id)
    form = OrderAssignForm(request.POST)
    if not form.is_valid():
        messages.error(request, "اطلاعات نامعتبر")
        return redirect("app_gift:order_detail", id=id)

    order.assigned_to = form.cleaned_data.get("assigned_to")
    order.save(update_fields=["assigned_to", "updated_at"])
    GiftOrderLog.objects.create(
        order=order, from_status=order.status, to_status=order.status,
        changed_by=request.user, action="assign",
        note=f"واگذار به {order.assigned_to.get_full_name() if order.assigned_to else 'هیچ‌کس'}",
    )
    messages.success(request, "مسئول پیگیری به‌روزرسانی شد")
    return redirect("app_gift:order_detail", id=id)


@is_admin_required
def order_note(request, id):
    RequiredAccess(request, "GiftOrderUpdate")
    if request.method != "POST":
        return redirect("app_gift:order_detail", id=id)

    order = get_object_or_404(GiftOrder, id=id)
    order.internal_note = (request.POST.get("internal_note") or "").strip() or None
    order.save(update_fields=["internal_note", "updated_at"])
    messages.success(request, "یادداشت ذخیره شد")
    return redirect("app_gift:order_detail", id=id)


# ═══════════════════════════════════════════════════════════
# Workflow helpers (بدون تغییر)
# ═══════════════════════════════════════════════════════════
VALID_TRANSITIONS = {
    GiftOrder.Status.PENDING: {GiftOrder.Status.APPROVED, GiftOrder.Status.REJECTED, GiftOrder.Status.CANCELLED},
    GiftOrder.Status.APPROVED: {GiftOrder.Status.SHIPPED, GiftOrder.Status.REJECTED, GiftOrder.Status.CANCELLED},
    GiftOrder.Status.SHIPPED: {GiftOrder.Status.DELIVERED, GiftOrder.Status.RETURNED},
    GiftOrder.Status.DELIVERED: {GiftOrder.Status.RETURNED},
    GiftOrder.Status.REJECTED: set(),
    GiftOrder.Status.CANCELLED: set(),
    GiftOrder.Status.RETURNED: set(),
}


def _available_transitions(order):
    return [
        {"value": s, "label": dict(GiftOrder.Status.choices)[s]}
        for s in VALID_TRANSITIONS.get(order.status, set())
    ]


def _is_valid_transition(current, new):
    return new in VALID_TRANSITIONS.get(current, set())


def _apply_status_side_effects(order, old_status, new_status):
    if new_status == GiftOrder.Status.APPROVED and old_status == GiftOrder.Status.PENDING:
        updated = Gift.objects.filter(
            pk=order.gift_id, stock__gte=order.quantity
        ).update(stock=F("stock") - order.quantity)
        if not updated:
            raise ValueError("موجودی هدیه کافی نیست")
    elif new_status in (GiftOrder.Status.REJECTED, GiftOrder.Status.CANCELLED):
        if old_status in (GiftOrder.Status.APPROVED, GiftOrder.Status.SHIPPED, GiftOrder.Status.DELIVERED):
            Gift.objects.filter(pk=order.gift_id).update(stock=F("stock") + order.quantity)
    elif new_status == GiftOrder.Status.RETURNED:
        if old_status in (GiftOrder.Status.SHIPPED, GiftOrder.Status.DELIVERED):
            Gift.objects.filter(pk=order.gift_id).update(stock=F("stock") + order.quantity)

    if new_status in (GiftOrder.Status.REJECTED, GiftOrder.Status.CANCELLED, GiftOrder.Status.RETURNED):
        _refund_points_for_order(order)


def _refund_points_for_order(order):
    from applications.score import api as score_api
    try:
        score_api.award(
            order.user, "GIFT_REFUND",
            reference_type="gift_order_refund",
            reference_id=str(order.id),
            reason=f"استرداد امتیاز سفارش #{order.id}",
        )
        logger.info("Refunded points for order #%s", order.id)
    except Exception:
        logger.exception("Refund failed for order #%s", order.id)