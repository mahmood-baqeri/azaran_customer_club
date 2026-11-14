# applications/gift/repositories.py

import logging

from django.db import transaction
from django.db.models import F

from applications.core.fileManager import uploadFile
from applications.core.utils import handle_get_file
from applications.score import api as score_api

from .models import Gift, GiftOrder, GiftOrderLog

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# GIFT — Store (create / update)
# ═══════════════════════════════════════════════════════════
def gift__store(request, cleaned, item=None):
    """ذخیره/به‌روزرسانی هدیه بر اساس داده‌های معتبرشده.

    Args:
        request: HttpRequest (برای فایل‌ها)
        cleaned: dict خروجی gift__clean__data (تضمین‌شده معتبر)
        item: نمونه‌ی موجود برای update؛ None برای create
    """
    if not cleaned:
        raise ValueError("cleaned data is required")

    fields = {
        "title": cleaned["title"],
        "for_user": cleaned["for_user"],
        "description": cleaned["description"],
        "azar_value": cleaned["azar_value"],
        "stock": cleaned["stock"],
        "is_active": cleaned["is_active"],
    }

    new_photo = handle_get_file(request, "photo")

    if item is None:
        item = Gift.objects.create(**fields, photo=new_photo or None)
    else:
        for key, value in fields.items():
            setattr(item, key, value)
        if new_photo:
            item.photo = new_photo
        item.save()

    # گالری — فایل‌های جدید اضافه می‌شوند
    new_gallery_files = request.FILES.getlist("gallery") or []
    if new_gallery_files:
        gallery = list(item.gallery or [])
        gallery += [uploadFile(img) for img in new_gallery_files]
        item.gallery = gallery
        item.save(update_fields=["gallery", "updated_at"])

    return item


# ═══════════════════════════════════════════════════════════
# ORDER — Workflow constants
# ═══════════════════════════════════════════════════════════
VALID_TRANSITIONS = {
    GiftOrder.Status.PENDING: {
        GiftOrder.Status.APPROVED,
        GiftOrder.Status.REJECTED,
        GiftOrder.Status.CANCELLED,
    },
    GiftOrder.Status.APPROVED: {
        GiftOrder.Status.SHIPPED,
        GiftOrder.Status.REJECTED,
        GiftOrder.Status.CANCELLED,
    },
    GiftOrder.Status.SHIPPED: {
        GiftOrder.Status.DELIVERED,
        GiftOrder.Status.RETURNED,
    },
    GiftOrder.Status.DELIVERED: {GiftOrder.Status.RETURNED},
    GiftOrder.Status.REJECTED: set(),
    GiftOrder.Status.CANCELLED: set(),
    GiftOrder.Status.RETURNED: set(),
}


def order__available_transitions(order):
    """لیست گذارهای مجاز — برای رندر در قالب."""
    return [
        {"value": s, "label": dict(GiftOrder.Status.choices)[s]}
        for s in VALID_TRANSITIONS.get(order.status, set())
    ]


def _is_valid_transition(current, new):
    return new in VALID_TRANSITIONS.get(current, set())


# ═══════════════════════════════════════════════════════════
# ORDER — Change status
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def order__change_status(order, cleaned, changed_by):
    """تغییر وضعیت با اعتبارسنجی گذار + اثرات جانبی (موجودی/استرداد)."""
    new_status = cleaned["new_status"]
    tracking_code = cleaned["tracking_code"]
    note = cleaned["note"]

    if not _is_valid_transition(order.status, new_status):
        raise ValueError("تغییر وضعیت نامعتبر است")

    if new_status == GiftOrder.Status.SHIPPED and not tracking_code:
        raise ValueError("برای ارسال، کد رهگیری الزامی است")

    old_status = order.status
    order.status = new_status
    update_fields = ["status", "updated_at"]
    if tracking_code:
        order.tracking_code = tracking_code
        update_fields.append("tracking_code")

    # موجودی و استرداد (قبل از save چون ممکن است خطا بدهد → rollback)
    _apply_status_side_effects(order, old_status, new_status)

    order.save(update_fields=update_fields)
    GiftOrderLog.objects.create(
        order=order,
        from_status=old_status,
        to_status=new_status,
        changed_by=changed_by,
        action="status_change",
        note=note or None,
    )
    return order


# ═══════════════════════════════════════════════════════════
# ORDER — Assign
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def order__assign(order, assigned_to, changed_by):
    order.assigned_to = assigned_to
    order.save(update_fields=["assigned_to", "updated_at"])
    GiftOrderLog.objects.create(
        order=order,
        from_status=order.status,
        to_status=order.status,
        changed_by=changed_by,
        action="assign",
        note=f"واگذاری به {assigned_to.get_full_name() if assigned_to else 'هیچ‌کس'}",
    )
    return order


# ═══════════════════════════════════════════════════════════
# ORDER — Save note
# ═══════════════════════════════════════════════════════════
def order__save_note(order, note):
    order.internal_note = note
    order.save(update_fields=["internal_note", "updated_at"])
    return order


# ═══════════════════════════════════════════════════════════
# Side effects (private)
# ═══════════════════════════════════════════════════════════
def _apply_status_side_effects(order, old_status, new_status):
    """کاهش/افزایش موجودی + استرداد امتیاز. داخل transaction اجرا می‌شود."""
    # ── کاهش موجودی هنگام APPROVED از PENDING ──
    if new_status == GiftOrder.Status.APPROVED and old_status == GiftOrder.Status.PENDING:
        updated = Gift.objects.filter(
            pk=order.gift_id, stock__gte=order.quantity
        ).update(stock=F("stock") - order.quantity)
        if not updated:
            raise ValueError("موجودی هدیه کافی نیست")

    # ── بازگشت موجودی ──
    elif new_status in (GiftOrder.Status.REJECTED, GiftOrder.Status.CANCELLED):
        if old_status in (
            GiftOrder.Status.APPROVED,
            GiftOrder.Status.SHIPPED,
            GiftOrder.Status.DELIVERED,
        ):
            Gift.objects.filter(pk=order.gift_id).update(
                stock=F("stock") + order.quantity
            )
    elif new_status == GiftOrder.Status.RETURNED:
        if old_status in (GiftOrder.Status.SHIPPED, GiftOrder.Status.DELIVERED):
            Gift.objects.filter(pk=order.gift_id).update(
                stock=F("stock") + order.quantity
            )

    # ── استرداد امتیاز ──
    if new_status in (
        GiftOrder.Status.REJECTED,
        GiftOrder.Status.CANCELLED,
        GiftOrder.Status.RETURNED,
    ):
        _refund_points_for_order(order)


def _refund_points_for_order(order):
    """استرداد امتیاز — idempotent بر اساس GiftOrderLog(action='refund')."""
    already = GiftOrderLog.objects.filter(order=order, action="refund").exists()
    if already:
        logger.info("Refund already exists for order #%s — skipping", order.id)
        return

    try:
        score_api.award(
            order.user,
            "GIFT_REFUND",
            reference_type="gift_order_refund",
            reference_id=str(order.id),
            reason=f"استرداد امتیاز سفارش #{order.id}",
        )
        GiftOrderLog.objects.create(
            order=order,
            from_status=order.status,
            to_status=order.status,
            action="refund",
            note=f"استرداد امتیاز سفارش #{order.id}",
        )
        logger.info("Refunded points for order #%s", order.id)
    except Exception:
        logger.exception("Refund failed for order #%s", order.id)
        raise