# admin/app_fastapi/views/gift/order.py

import os
from typing import Optional
from fastapi import APIRouter, Depends
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.db import transaction, IntegrityError
from django.db.models import F

from applications.score.models import UserScore, UserScoreLog
from applications.gift.models import Gift, GiftOrder, GiftOrderLog
from applications.user.models import User
from app_fastapi.views.user.helper import get_current_user
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.response import success_response, error_response

router = APIRouter()


# =========================================================
# Serialize
# =========================================================
def order_serialize(o: GiftOrder, include_logs: bool = False) -> dict:
    data = {
        "id": o.id,
        "status": o.status,
        "status_display": o.get_status_display(),
        "quantity": o.quantity,
        "total_azar_value": o.total_azar_value,
        "tracking_code": o.tracking_code,
        "internal_note": o.internal_note,
        "created_at": o.created_at.isoformat() if o.created_at else None,
        "updated_at": o.updated_at.isoformat() if o.updated_at else None,
        "receiver_name": o.receiver_name,
        "receiver_phone": o.receiver_phone,
        "address": o.address,
        "postal_code": o.postal_code,
        "gift": {
            "id": o.gift_id,
            "title": o.gift.title,
            "photo": o.gift.photo.url if o.gift.photo else None,
            "azar_value": o.gift.azar_value,
        },
        "user": {
            "id": o.user_id,
            "name": o.user.full_name,
            "mobile": o.user.mobile,
        },
        "assigned_to": (
            {"id": o.assigned_to.id, "name": o.assigned_to.full_name}
            if o.assigned_to
            else None
        ),
    }
    if include_logs:
        data["logs"] = [
            {
                "id": lg.id,
                "action": lg.action,
                "from_status": lg.from_status,
                "to_status": lg.to_status,
                "note": lg.note,
                "created_at": lg.created_at.isoformat() if lg.created_at else None,
                "changed_by": (
                    {"id": lg.changed_by.id, "name": lg.changed_by.full_name}
                    if lg.changed_by
                    else None
                ),
            }
            for lg in o.logs.all().order_by("-created_at")
        ]
    return data


# =========================================================
# CREATE ORDER  (با قفل کامل و تضمین موجودی)
# =========================================================
@router.post("/")
async def create_order(
    form: dict = Depends(DependencyDataRequest),
    user: User = Depends(get_current_user),
):
    """
    ثبت سفارش:
    - idempotency: دو بار زدن با یک کلید، یک سفارش می‌سازد
    - قفل هم‌زمانی: select_for_update روی Gift و UserScore
    - تضمین قطعی: هیچ سفارشی بدون موجودی کافی آذر ثبت نمی‌شود
    """
    gift_id = form.get("gift_id")
    if not gift_id:
        return error_response("هدیه الزامی است")

    idem = (form.get("idempotency_key") or "").strip() or None
    if idem and len(idem) > 64:
        return error_response("کلید یکتایی درخواست نامعتبر است")

    try:
        result = await async_create_order(user.id, form, idem)
        if result.get("error"):
            return error_response(result["error"])
        return success_response("سفارش با موفقیت ثبت شد", result["order"])
    except Exception as e:
        return error_response(str(e))


@sync_to_async
def async_create_order(user_id: int, form: dict, idem: Optional[str]):
    # مرحله ۱: چک idempotency خارج از تراکنش اصلی
    if idem:
        existing = (
            GiftOrder.objects
            .select_related("gift", "user", "assigned_to")
            .prefetch_related("logs__changed_by")
            .filter(user_id=user_id, idempotency_key=idem)
            .first()
        )
        if existing:
            return {"order": order_serialize(existing, include_logs=True), "idempotent": True}

    # مرحله ۲: کاربر
    user = User.objects.filter(id=user_id).first()
    if not user:
        return {"error": "کاربر یافت نشد"}

    # مرحله ۳: اطمینان از وجود UserScore (خارج از atomic تا race روی ساخت نداشته باشیم)
    try:
        UserScore.objects.get_or_create(user_id=user_id)
    except IntegrityError:
        # یک درخواست موازی همین الان ساختش
        pass

    try:
        with transaction.atomic():
            # ----------------------------------------------------
            # 🔒 قفل اول: Gift
            # ----------------------------------------------------
            gift = (
                Gift.objects
                .select_for_update()
                .filter(id=form["gift_id"], is_active=True)
                .first()
            )
            if not gift:
                return {"error": "هدیه یافت نشد یا غیرفعال است"}

            # ----------------------------------------------------
            # پارس و اعتبارسنجی quantity
            # ----------------------------------------------------
            try:
                qty = int(form.get("quantity") or 1)
            except (ValueError, TypeError):
                return {"error": "تعداد نامعتبر است"}
            if qty < 1:
                return {"error": "تعداد نامعتبر است"}

            if gift.stock < qty:
                return {"error": "موجودی هدیه کافی نیست"}

            # ----------------------------------------------------
            # ✅ محاسبه مبلغ با اعمال تخفیف
            # ----------------------------------------------------
            original_total = gift.azar_value * qty
            
            # ✅ خواندن درصد تخفیف از مدل
            discount_percent = user.gift_discount_percent
            discount_amount = int(original_total * discount_percent / 100)
            total = original_total - discount_amount

            # ----------------------------------------------------
            # 🔒 قفل دوم: UserScore
            # ----------------------------------------------------
            score = (
                UserScore.objects
                .select_for_update()
                .filter(user_id=user_id)
                .first()
            )
            if not score:
                return {"error": "حساب امتیاز یافت نشد"}

            # ----------------------------------------------------
            # ✅ بررسی موجودی (داخل قفل)
            # ----------------------------------------------------
            if score.current_balance < total:
                return {"error": "موجودی آذر شما کافی نیست"}

            # ----------------------------------------------------
            # ✅✅ کسر اتمیک با conditional UPDATE
            # (حتی اگر select_for_update کار نکند — مثلاً روی SQLite — 
            # این UPDATE اتمیک است و اجازه نمی‌دهد balance منفی شود)
            # ----------------------------------------------------
            affected = (
                UserScore.objects
                .filter(user_id=user_id, current_balance__gte=total)
                .update(
                    current_balance=F("current_balance") - total,
                    total_spent=F("total_spent") + total,
                )
            )
            if affected != 1:
                # یک درخواست موازی امتیاز را کسر کرده، حالا کافی نیست
                raise ValueError("موجودی آذر شما کافی نیست (درخواست هم‌زمان)")

            # Refresh برای balance_after
            score.refresh_from_db(fields=["current_balance", "total_spent"])

            # ----------------------------------------------------
            # کسر stock (داخل قفل Gift)
            # ----------------------------------------------------
            gift.stock -= qty
            gift.save(update_fields=["stock"])

            # ----------------------------------------------------
            # ساخت سفارش
            # ----------------------------------------------------
            order = GiftOrder.objects.create(
                user=user,
                gift=gift,
                quantity=qty,
                total_azar_value=total,
                receiver_name=(form.get("receiver_name") or user.full_name),
                receiver_phone=(form.get("receiver_phone") or user.mobile or ""),
                address=(form.get("address") or ""),
                postal_code=(form.get("postal_code") or ""),
                status=GiftOrder.Status.PENDING,
                idempotency_key=idem,
            )

            # ----------------------------------------------------
            # لاگ سفارش
            # ----------------------------------------------------
            GiftOrderLog.objects.create(
                order=order,
                from_status=None,
                to_status=GiftOrder.Status.PENDING,
                action="create",
                changed_by=user,
                note="سفارش توسط کاربر ثبت شد",
            )

            # ----------------------------------------------------
            # لاگ تراکنش امتیاز
            # ----------------------------------------------------
            UserScoreLog.objects.create(
                user=user,
                transaction_type=UserScoreLog.TransactionType.SPENT,
                amount=total,
                reason=f"سفارش هدیه #{order.id}",
                reference_id=str(order.id),
                balance_after=score.current_balance,
            )

            return {"order": order_serialize(order, include_logs=True)}

    except IntegrityError:
        # idempotency unique conflict → درخواست موازی با همین کلید
        if idem:
            existing = (
                GiftOrder.objects
                .select_related("gift", "user", "assigned_to")
                .prefetch_related("logs__changed_by")
                .filter(user_id=user_id, idempotency_key=idem)
                .first()
            )
            if existing:
                return {
                    "order": order_serialize(existing, include_logs=True),
                    "idempotent": True,
                }
        return {"error": "درخواست هم‌زمان شناسایی شد، لطفاً دوباره تلاش کنید"}


# =========================================================
# CANCEL ORDER  (با قفل کامل)
# =========================================================
@router.post("/{order_id}/cancel/")
async def cancel_order(
    order_id: int,
    form: dict = Depends(DependencyDataRequest),
    user: User = Depends(get_current_user),
):
    try:
        result = await async_cancel_order(order_id, user.id, form)
        if result.get("error"):
            return error_response(result["error"])
        return success_response("سفارش با موفقیت لغو شد", result["order"])
    except Exception as e:
        return error_response(str(e))


@sync_to_async
def async_cancel_order(order_id: int, user_id: int, form: dict):
    try:
        with transaction.atomic():
            # 🔒 قفل روی order
            o = (
                GiftOrder.objects
                .select_for_update()
                .select_related("gift", "user", "assigned_to")
                .filter(id=order_id, user_id=user_id)
                .first()
            )
            if not o:
                return {"error": "سفارش یافت نشد"}

            cancellable = (GiftOrder.Status.PENDING, GiftOrder.Status.APPROVED)
            if o.status not in cancellable:
                return {"error": "این سفارش در وضعیت فعلی قابل لغو نیست"}

            old_status = o.status
            o.status = GiftOrder.Status.CANCELLED
            o.save(update_fields=["status"])

            # 🔒 قفل روی Gift + برگشت stock
            Gift.objects.select_for_update().filter(id=o.gift_id).exists()
            Gift.objects.filter(id=o.gift_id).update(stock=F("stock") + o.quantity)

            # 🔒 قفل روی UserScore + برگشت امتیاز
            score = (
                UserScore.objects
                .select_for_update()
                .filter(user_id=user_id)
                .first()
            )
            if score:
                refund = o.total_azar_value
                UserScore.objects.filter(user_id=user_id).update(
                    current_balance=F("current_balance") + refund,
                    total_spent=F("total_spent") - refund,
                )
                score.refresh_from_db(fields=["current_balance", "total_spent"])

                UserScoreLog.objects.create(
                    user_id=user_id,
                    transaction_type=UserScoreLog.TransactionType.EARNED,
                    amount=refund,
                    reason=f"برگشت وجه سفارش #{o.id}",
                    reference_id=str(o.id),
                    balance_after=score.current_balance,
                )

            # لاگ
            GiftOrderLog.objects.create(
                order=o,
                from_status=old_status,
                to_status=GiftOrder.Status.CANCELLED,
                action="status_change",
                changed_by_id=user_id,
                note=(form.get("note") or "").strip() or "سفارش توسط کاربر لغو شد",
            )

            return {"order": order_serialize(o, include_logs=True)}

    except IntegrityError:
        return {"error": "درخواست هم‌زمان شناسایی شد، لطفاً دوباره تلاش کنید"}


# =========================================================
# LIST ORDERS (own only)
# =========================================================
@router.get("/")
async def list_orders(
    status: Optional[str] = None,
    user: User = Depends(get_current_user),
):
    try:
        items = await async_list_orders(user.id, status)
        return success_response("سفارشات من", items)
    except Exception as e:
        return error_response(str(e))


@database_sync_to_async
def async_list_orders(user_id, status):
    qs = (
        GiftOrder.objects
        .select_related("gift", "user", "assigned_to")
        .filter(user_id=user_id)
    )
    if status and status in dict(GiftOrder.Status.choices):
        qs = qs.filter(status=status)
    return [order_serialize(o) for o in qs.order_by("-created_at")]


# =========================================================
# DETAIL (own only)
# =========================================================
@router.get("/{order_id}/")
async def get_order(order_id: int, user: User = Depends(get_current_user)):
    try:
        item = await async_get_order(order_id, user.id)
        if not item:
            return error_response("سفارش یافت نشد", 404)
        return success_response("جزئیات سفارش", item)
    except Exception as e:
        return error_response(str(e))


@database_sync_to_async
def async_get_order(order_id, user_id):
    o = (
        GiftOrder.objects
        .select_related("gift", "user", "assigned_to")
        .prefetch_related("logs__changed_by")
        .filter(id=order_id, user_id=user_id)
        .first()
    )
    if not o:
        return None
    return order_serialize(o, include_logs=True)


# =========================================================
# LOGS (own only)
# =========================================================
@router.get("/{order_id}/logs/")
async def get_logs(order_id: int, user: User = Depends(get_current_user)):
    try:
        items = await async_get_logs(order_id, user.id)
        if items is None:
            return error_response("سفارش یافت نشد", 404)
        return success_response("تاریخچه سفارش", items)
    except Exception as e:
        return error_response(str(e))


@database_sync_to_async
def async_get_logs(order_id, user_id):
    o = GiftOrder.objects.filter(id=order_id, user_id=user_id).first()
    if not o:
        return None

    logs = (
        GiftOrderLog.objects
        .select_related("changed_by")
        .filter(order_id=order_id)
        .order_by("-created_at")
    )
    return [
        {
            "id": lg.id,
            "action": lg.action,
            "from_status": lg.from_status,
            "to_status": lg.to_status,
            "note": lg.note,
            "created_at": lg.created_at.isoformat() if lg.created_at else None,
            "changed_by": (
                {"id": lg.changed_by.id, "name": lg.changed_by.full_name}
                if lg.changed_by
                else None
            ),
        }
        for lg in logs
    ]