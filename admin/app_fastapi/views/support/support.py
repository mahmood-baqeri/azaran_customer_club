# app_fastapi/views/support/support.py

import logging

from asgiref.sync import sync_to_async
from fastapi import APIRouter, Depends, File, UploadFile
from django.db import transaction

from applications.support.models import Support, SupportMessage
from applications.support.services import (
    SupportError,
    close_by_user,
    create_ticket,
)
from applications.user.models import User
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.fileManager import get_file_url, handle_save_file
from app_fastapi.conf.response import error_response, success_response
from app_fastapi.views.user.user_helper import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


# ═══════════════════════════════════════════════════════════
# Serializers
# ═══════════════════════════════════════════════════════════
def _serialize_message(m: SupportMessage) -> dict:
    return {
        "id": m.id,
        "text": m.text,
        "file": get_file_url(m.file) if m.file else None,
        "is_admin_reply": m.is_admin_reply,
        "is_read": m.is_read,
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "sender": {
            "id": m.sender.id,
            "name": m.sender.full_name,
            "mobile": m.sender.mobile,
        }
    }


def _serialize_ticket(t: Support, *, full: bool = False) -> dict:
    data = {
        "id": t.id,
        "category": t.category,
        "category_display": t.get_category_display(),
        "status": t.status,
        "status_display": t.get_status_display(),
        "priority": t.priority,
        "subject": t.subject,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "last_message_at": t.last_message_at.isoformat() if t.last_message_at else None,
        "closed_at": t.closed_at.isoformat() if t.closed_at else None,
        "close_reason": t.close_reason,
    }
    if full:
        # واکشی تمام پیام‌های این تیکت
        data["messages"] = [_serialize_message(m) for m in t.messages.all()]
    return data


# ═══════════════════════════════════════════════════════════
# ۱. ایجاد تیکت (همراه با پیام اول)
# ═══════════════════════════════════════════════════════════
@router.post("/create/")
async def create_ticket_endpoint(
    form: dict = Depends(DependencyDataRequest),
    file: UploadFile = File(None),
    user: User = Depends(get_current_user),
):
    saved_name = None
    if file:
        try:
            saved_name = await sync_to_async(handle_save_file)(file)
        except Exception:
            logger.exception("file save failed")
            return error_response("خطا در ذخیره فایل")

    try:
        # سرویس create_ticket باید به‌روزرسانی شده باشد تا اولین پیام را هم بسازد
        ticket = await sync_to_async(create_ticket)(
            user,
            category=form.get("category", "other"),
            subject=form.get("subject"),
            text=form.get("text"),
            file_name=saved_name,
            priority=form.get("priority", "normal"),
        )
        
        # برای برگرداندن اطلاعات کامل همراه با پیام‌ها
        full_ticket = await _get_one(ticket.id, user.id)
        return success_response(
            "تیکت ثبت شد و در انتظار بررسی است",
            full_ticket,
        )
    except SupportError as e:
        return error_response(str(e), status_code=400)
    except Exception:
        logger.exception("create_ticket failed")
        return error_response("خطا در ثبت تیکت")


# ═══════════════════════════════════════════════════════════
# ۲. لیست تیکت‌ها
# ═══════════════════════════════════════════════════════════
@router.get("/list/")
async def list_my_tickets(
    status: str = None,
    user: User = Depends(get_current_user),
):
    data = await sync_to_async(_list)(user.id, status)
    return success_response("تیکت‌های من", data)


@sync_to_async
def _list(user_id, status):
    qs = (
        Support.objects
        .filter(user_id=user_id)
        .order_by("-last_message_at") # مرتب‌سازی بر اساس آخرین پیام
    )
    if status and status in Support.Status.values:
        qs = qs.filter(status=status)
    return [_serialize_ticket(t) for t in qs]


# ═══════════════════════════════════════════════════════════
# ۳. جزئیات تیکت (همراه با تمام چت‌ها)
# ═══════════════════════════════════════════════════════════
@router.get("/{ticket_id}/")
async def get_ticket(ticket_id: int, user: User = Depends(get_current_user)):
    data = await _get_one(ticket_id, user.id)
    if not data:
        return error_response("تیکت یافت نشد", status_code=404)
        
    # آپدیت وضعیت خوانده شدن پیام‌های ادمین (اختیاری)
    await _mark_messages_as_read(ticket_id)
    
    return success_response("جزئیات تیکت", data)


@sync_to_async
def _get_one(ticket_id, user_id):
    t = (
        Support.objects
        .prefetch_related("messages__sender") # جلوگیری از خطای Lazy Load
        .filter(id=ticket_id, user_id=user_id)
        .first()
    )
    return _serialize_ticket(t, full=True) if t else None


@sync_to_async
def _mark_messages_as_read(ticket_id):
    # وقتی کاربر وارد صفحه تیکت می‌شود، پیام‌های ادمین را خوانده شده علامت می‌زنیم
    SupportMessage.objects.filter(ticket_id=ticket_id, is_admin_reply=True, is_read=False).update(is_read=True)


# ═══════════════════════════════════════════════════════════
# ۴. ارسال پیام جدید در تیکت
# ═══════════════════════════════════════════════════════════
@router.post("/{ticket_id}/messages/")
async def send_message_endpoint(
    ticket_id: int,
    form: dict = Depends(DependencyDataRequest),
    file: UploadFile = File(None),
    user: User = Depends(get_current_user),
):
    saved_name = None
    if file:
        try:
            saved_name = await sync_to_async(handle_save_file)(file)
        except Exception:
            logger.exception("file save failed")
            return error_response("خطا در ذخیره فایل")

    try:
        msg = await _send_message_db(ticket_id, user.id, form.get("text"), saved_name)
        if msg.get("error"):
            return error_response(msg["error"], status_code=400)
            
        return success_response("پیام ارسال شد", msg["data"])
    except Exception:
        logger.exception("send_message failed")
        return error_response("خطا در ارسال پیام")


@sync_to_async
def _send_message_db(ticket_id, user_id, text, file_name):
    if not text and not file_name:
        return {"error": "متن پیام یا فایل الزامی است"}

    with transaction.atomic():
        t = Support.objects.select_for_update().filter(id=ticket_id, user_id=user_id).first()
        if not t:
            return {"error": "تیکت یافت نشد"}
        if t.status == Support.Status.CLOSED:
            return {"error": "این تیکت بسته شده است و امکان ارسال پیام وجود ندارد"}

        m = SupportMessage.objects.create(
            ticket=t,
            sender_id=user_id,
            text=text,
            file=file_name,
            is_admin_reply=False
        )
        
        # اگر تیکت در وضعیت RESOLVED بود، با ارسال پیام جدید کاربر، مجدد OPEN می‌شود
        if t.status == Support.Status.RESOLVED:
            t.status = Support.Status.OPEN
            t.save(update_fields=["status"])

        m.refresh_from_db()
        return {"data": _serialize_message(m)}


# ═══════════════════════════════════════════════════════════
# ۵. بستن توسط کاربر
# ═══════════════════════════════════════════════════════════
@router.post("/{ticket_id}/close/")
async def close_ticket(ticket_id: int, user: User = Depends(get_current_user)):
    try:
        # فرض بر این است که سرویس close_by_user آپدیت شده است
        ticket = await sync_to_async(close_by_user)(ticket_id, user.id)
        return success_response("تیکت بسته شد", _serialize_ticket(ticket))
    except SupportError as e:
        return error_response(str(e), status_code=400)