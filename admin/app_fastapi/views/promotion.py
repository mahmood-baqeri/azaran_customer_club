# app_fastapi/views/promotion.py

from typing import Optional
from fastapi import APIRouter, Depends
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.db import transaction, IntegrityError
from django.db.models import Prefetch

from applications.promotion.models import (
    Promotion,
    PromotionItem,
    PromotionOrder,
    PromotionalOrderLog,
)
from applications.user.models import User
from app_fastapi.views.user.user_helper import get_current_user
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.response import success_response, error_response

router = APIRouter()


# =========================================================
# Prefetch helpers (طبق مدل: promotion_items_relation + promotion_logs_relation)
# =========================================================
def _promotion_items_prefetch() -> Prefetch:
    """فقط آیتم‌های فعال را روی Promotion پرفچ می‌کند."""
    return Prefetch(
        "promotion_items_relation",
        queryset=PromotionItem.objects.filter(is_active=True).order_by("id"),
        to_attr="active_items",
    )


def _order_promotion_items_prefetch() -> Prefetch:
    """آیتم‌های فعال روی Promotion تودرتوی سفارش."""
    return Prefetch(
        "promotion__promotion_items_relation",
        queryset=PromotionItem.objects.filter(is_active=True).order_by("id"),
        to_attr="active_items",
    )


def _order_logs_prefetch() -> Prefetch:
    """لاگ‌های سفارش (related_name=promotion_logs_relation)."""
    return Prefetch(
        "promotion_logs_relation",
        queryset=PromotionalOrderLog.objects.order_by("-created_at"),
    )


def _get_active_items(promotion: Promotion):
    """اگر prefetch شده بود از cache، وگرنه fallback به queryset."""
    cached = getattr(promotion, "active_items", None)
    if cached is not None:
        return cached
    return promotion.promotion_items_relation.filter(is_active=True).order_by("id")


# =========================================================
# Serialize
# =========================================================
def promotion_serialize(p: Promotion) -> dict:
    return {
        "id": p.id,
        "title": p.title,
        "is_active": p.is_active,
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "badge": item.badge,
                "photo": item.photo.url if item.photo else None,
            }
            for item in _get_active_items(p)
        ],
    }


def _log_serialize(lg: PromotionalOrderLog) -> dict:
    return {
        "id": lg.id,
        "action": lg.action,
        "from_status": lg.from_status,
        "to_status": lg.to_status,
        "note": lg.note,
        "changed_by_id": lg.changed_by_id,
        "created_at": lg.created_at.isoformat() if lg.created_at else None,
    }


def promotion_order_serialize(o: PromotionOrder, include_logs: bool = False) -> dict:
    promo = o.promotion
    data = {
        "id": o.id,
        "status": o.status,
        "status_display": o.status_display,
        "tracking_code": o.tracking_code,
        "created_at": o.created_at.isoformat() if o.created_at else None,
        "receiver_name": o.receiver_name,
        "receiver_phone": o.receiver_phone,
        "address": o.address,
        "postal_code": o.postal_code,
        "promotion": {
            "id": o.promotion_id,
            "title": promo.title,
            "items": [
                {
                    "id": i.id,
                    "title": i.title,
                    "photo": i.photo.url if i.photo else None,
                }
                for i in _get_active_items(promo)
            ],
        },
    }
    if include_logs:
        # ✅ related_name صحیح: promotion_logs_relation
        data["logs"] = [_log_serialize(lg) for lg in o.promotion_logs_relation.all()]
    return data


# =========================================================
# LIST PROMOTIONS
# =========================================================
@router.get("/")
async def list_promotions(user: User = Depends(get_current_user)):
    try:
        items = await async_list_promotions()
        return success_response("لیست اقلام تبلیغاتی", items)
    except Exception as e:
        return error_response(str(e))


@database_sync_to_async
def async_list_promotions():
    qs = (
        Promotion.objects
        .filter(is_active=True)
        .prefetch_related(_promotion_items_prefetch())
        .order_by("-created_at")
    )
    return [promotion_serialize(p) for p in qs]


# =========================================================
# CREATE ORDER
# =========================================================
@router.post("/orders/")
async def create_promotion_order(
    form: dict = Depends(DependencyDataRequest),
    user: User = Depends(get_current_user),
):
    promo_id = form.get("promotion_id")
    if not promo_id:
        return error_response("پک تبلیغاتی الزامی است")

    idem = (form.get("idempotency_key") or "").strip() or None
    if idem and len(idem) > 64:
        return error_response("کلید یکتایی درخواست نامعتبر است")

    try:
        result = await async_create_promotion_order(user.id, form, idem)
        if result.get("error"):
            return error_response(result["error"])
        return success_response("سفارش با موفقیت ثبت شد", result["order"])
    except Exception as e:
        return error_response(str(e))



@sync_to_async
def async_create_promotion_order(user_id: int, form: dict, idem: Optional[str]):
    # ── idempotency fast-path (بدون تغییر) ──────────────────
    if idem:
        existing = (
            PromotionOrder.objects
            .select_related("promotion", "user")
            .prefetch_related(
                _order_promotion_items_prefetch(),
                _order_logs_prefetch(),
            )
            .filter(user_id=user_id, idempotency_key=idem)
            .first()
        )
        if existing:
            return {
                "order": promotion_order_serialize(existing, include_logs=True),
                "idempotent": True,
            }

    try:
        with transaction.atomic():
            # ✅ قفل ردیف کاربر → درخواست‌های هم‌زمان سریالایز می‌شن
            user = (
                User.objects
                .select_for_update()
                .filter(id=user_id)
                .first()
            )
            if not user:
                return {"error": "کاربر یافت نشد"}

            promotion = (
                Promotion.objects
                .filter(id=form["promotion_id"], is_active=True)
                .first()
            )
            if not promotion:
                return {"error": "پک تبلیغاتی یافت نشد یا غیرفعال است"}

            # ✅ چک اتمیک: چون ردیف کاربر قفل شده، هیچ درخواست دیگه‌ای
            #    نمی‌تونه بین این چک و create قرار بگیره
            existing_order = (
                PromotionOrder.objects
                .filter(user_id=user_id, promotion_id=promotion.id)
                .first()
            )
            if existing_order:
                return {
                    "error": "شما قبلاً این پک تبلیغاتی را دریافت کرده‌اید و امکان دریافت مجدد وجود ندارد",
                    "code": "ALREADY_ORDERED",
                }

            order = PromotionOrder.objects.create(
                user=user,
                promotion=promotion,
                receiver_name=(form.get("receiver_name") or user.full_name),
                receiver_phone=(form.get("receiver_phone") or user.mobile or ""),
                address=(form.get("address") or ""),
                postal_code=(form.get("postal_code") or ""),
                status=PromotionOrder.Status.PENDING,
                idempotency_key=idem,
            )

            PromotionalOrderLog.objects.create(
                order=order,
                from_status=None,
                to_status=PromotionOrder.Status.PENDING,
                action="create",
                changed_by=user,
                note="سفارش رایگان پک تبلیغاتی توسط کاربر ثبت شد",
            )

        # ── reload با prefetch (بیرون از تراکنش) ──────────
        order = (
            PromotionOrder.objects
            .select_related("promotion", "user")
            .prefetch_related(
                _order_promotion_items_prefetch(),
                _order_logs_prefetch(),
            )
            .get(pk=order.pk)
        )
        return {"order": promotion_order_serialize(order, include_logs=True)}

    except IntegrityError:
        # ── fallback: قید DB جلوی ما رو گرفت (بهترین حالت امنیتی) ──
        # ۱) شاید idempotency
        if idem:
            existing = (
                PromotionOrder.objects
                .select_related("promotion", "user")
                .prefetch_related(
                    _order_promotion_items_prefetch(),
                    _order_logs_prefetch(),
                )
                .filter(user_id=user_id, idempotency_key=idem)
                .first()
            )
            if existing:
                return {
                    "order": promotion_order_serialize(existing, include_logs=True),
                    "idempotent": True,
                }

        # ۲) یا شاید (user, promotion) — تلاش دوم
        if PromotionOrder.objects.filter(
            user_id=user_id,
            promotion_id=form.get("promotion_id"),
        ).exists():
            return {
                "error": "شما قبلاً این پک تبلیغاتی را دریافت کرده‌اید و امکان دریافت مجدد وجود ندارد",
                "code": "ALREADY_ORDERED",
            }

        # ۳) خطای غیرمنتظره
        return {"error": "خطا در ثبت سفارش، لطفاً دوباره تلاش کنید"}
    

# =========================================================
# CANCEL ORDER
# =========================================================
@router.post("/orders/{order_id}/cancel/")
async def cancel_promotion_order(
    order_id: int,
    form: dict = Depends(DependencyDataRequest),
    user: User = Depends(get_current_user),
):
    try:
        result = await async_cancel_promotion_order(order_id, user.id, form)
        if result.get("error"):
            return error_response(result["error"])
        return success_response("سفارش با موفقیت لغو شد", result["order"])
    except Exception as e:
        return error_response(str(e))


@sync_to_async
def async_cancel_promotion_order(order_id: int, user_id: int, form: dict):
    try:
        with transaction.atomic():
            # ⚠️ select_for_update با prefetch سازگار نیست → فقط ردیف اصلی
            o = (
                PromotionOrder.objects
                .select_for_update()
                .filter(id=order_id, user_id=user_id)
                .first()
            )
            if not o:
                return {"error": "سفارش یافت نشد"}

            cancellable = (
                PromotionOrder.Status.PENDING,
                PromotionOrder.Status.APPROVED,
            )
            if o.status not in cancellable:
                return {"error": "این سفارش در وضعیت فعلی قابل لغو نیست"}

            old_status = o.status
            o.status = PromotionOrder.Status.CANCELLED
            o.save(update_fields=["status"])

            PromotionalOrderLog.objects.create(
                order=o,
                from_status=old_status,
                to_status=PromotionOrder.Status.CANCELLED,
                action="status_change",
                changed_by_id=user_id,
                note=(form.get("note") or "").strip() or "سفارش توسط کاربر لغو شد",
            )

        # ── reload بیرون از تراکنش برای prefetch ──────────
        o = (
            PromotionOrder.objects
            .select_related("promotion", "user")
            .prefetch_related(
                _order_promotion_items_prefetch(),
                _order_logs_prefetch(),
            )
            .get(pk=order_id)
        )
        return {"order": promotion_order_serialize(o, include_logs=True)}

    except IntegrityError:
        return {"error": "درخواست هم‌زمان شناسایی شد، لطفاً دوباره تلاش کنید"}


# =========================================================
# LIST & DETAIL ORDERS
# =========================================================
@router.get("/orders/")
async def list_promotion_orders(
    status: Optional[str] = None,
    user: User = Depends(get_current_user),
):
    try:
        items = await async_list_promotion_orders(user.id, status)
        return success_response("سفارشات من", items)
    except Exception as e:
        return error_response(str(e))


@database_sync_to_async
def async_list_promotion_orders(user_id: int, status: Optional[str]):
    qs = (
        PromotionOrder.objects
        .select_related("promotion")
        .prefetch_related(_order_promotion_items_prefetch())
        .filter(user_id=user_id)
    )
    if status and status in dict(PromotionOrder.Status.choices):
        qs = qs.filter(status=status)
    return [promotion_order_serialize(o) for o in qs.order_by("-created_at")]


@router.get("/orders/{order_id}/")
async def get_promotion_order(
    order_id: int,
    user: User = Depends(get_current_user),
):
    try:
        item = await async_get_promotion_order(order_id, user.id)
        if not item:
            return error_response("سفارش یافت نشد", 404)
        return success_response("جزئیات سفارش", item)
    except Exception as e:
        return error_response(str(e))


@database_sync_to_async
def async_get_promotion_order(order_id: int, user_id: int):
    o = (
        PromotionOrder.objects
        .select_related("promotion")
        .prefetch_related(
            _order_promotion_items_prefetch(),
            _order_logs_prefetch(),
        )
        .filter(id=order_id, user_id=user_id)
        .first()
    )
    if not o:
        return None
    return promotion_order_serialize(o, include_logs=True)