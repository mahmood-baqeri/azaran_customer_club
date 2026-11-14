# applications/promotion/repositories.py

import logging

from django.db import transaction

from applications.core.utils import handle_get_file

from .models import (
    Promotion,
    PromotionItem,
    PromotionOrder,
    PromotionalOrderLog,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# PROMOTION
# ═══════════════════════════════════════════════════════════
def promotion__store(cleaned, item=None):
    """ذخیره/به‌روزرسانی پک تبلیغاتی"""
    if not cleaned:
        raise ValueError("cleaned data is required")

    if item is None:
        item = Promotion.objects.create(**cleaned)
    else:
        for k, v in cleaned.items():
            setattr(item, k, v)
        item.save()
    return item


# ═══════════════════════════════════════════════════════════
# PROMOTION ITEM
# ═══════════════════════════════════════════════════════════
def promotion_item__store(request, promotion, cleaned, item=None):
    """ذخیره/به‌روزرسانی آیتم پک"""
    if not cleaned:
        raise ValueError("cleaned data is required")

    new_photo = handle_get_file(request, "photo")

    if item is None:
        item = PromotionItem.objects.create(
            promotion=promotion,
            photo=new_photo or None,
            **cleaned,
        )
    else:
        for k, v in cleaned.items():
            setattr(item, k, v)
        if new_photo:
            item.photo = new_photo
        item.save()

    return item


def promotion_item__delete(item):
    """حذف آیتم — هیچ سفارشی به آن وابسته نیست"""
    item.delete()


# ═══════════════════════════════════════════════════════════
# ORDER — Workflow
# ═══════════════════════════════════════════════════════════
VALID_TRANSITIONS = {
    PromotionOrder.Status.PENDING: {
        PromotionOrder.Status.APPROVED,
        PromotionOrder.Status.REJECTED,
        PromotionOrder.Status.CANCELLED,
    },
    PromotionOrder.Status.APPROVED: {
        PromotionOrder.Status.SHIPPED,
        PromotionOrder.Status.REJECTED,
        PromotionOrder.Status.CANCELLED,
    },
    PromotionOrder.Status.SHIPPED: {
        PromotionOrder.Status.DELIVERED,
        PromotionOrder.Status.RETURNED,
    },
    PromotionOrder.Status.DELIVERED: {PromotionOrder.Status.RETURNED},
    PromotionOrder.Status.REJECTED: set(),
    PromotionOrder.Status.CANCELLED: set(),
    PromotionOrder.Status.RETURNED: set(),
}


def order__available_transitions(order):
    return [
        {"value": s, "label": dict(PromotionOrder.Status.choices)[s]}
        for s in VALID_TRANSITIONS.get(order.status, set())
    ]


def _is_valid_transition(current, new):
    return new in VALID_TRANSITIONS.get(current, set())


@transaction.atomic
def order__change_status(order, cleaned, changed_by):
    new_status = cleaned["new_status"]
    tracking_code = cleaned["tracking_code"]
    note = cleaned["note"]

    if not _is_valid_transition(order.status, new_status):
        raise ValueError("تغییر وضعیت نامعتبر است")

    if new_status == PromotionOrder.Status.SHIPPED and not tracking_code:
        raise ValueError("برای ارسال، کد رهگیری الزامی است")

    old_status = order.status
    order.status = new_status
    update_fields = ["status", "updated_at"]
    if tracking_code:
        order.tracking_code = tracking_code
        update_fields.append("tracking_code")

    order.save(update_fields=update_fields)
    PromotionalOrderLog.objects.create(
        order=order,
        from_status=old_status,
        to_status=new_status,
        changed_by=changed_by,
        action="status_change",
        note=note or None,
    )
    return order


@transaction.atomic
def order__assign(order, assigned_to, changed_by):
    order.assigned_to = assigned_to
    order.save(update_fields=["assigned_to", "updated_at"])
    PromotionalOrderLog.objects.create(
        order=order,
        from_status=order.status,
        to_status=order.status,
        changed_by=changed_by,
        action="assign",
        note=f"واگذاری به {assigned_to.get_full_name() if assigned_to else 'هیچ‌کس'}",
    )
    return order