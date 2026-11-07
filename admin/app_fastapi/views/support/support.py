# app_fastapi/views/support/support.py

import logging

from asgiref.sync import sync_to_async
from fastapi import APIRouter, Depends, File, UploadFile

from applications.support.models import Support
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
        "replied_at": t.replied_at.isoformat() if t.replied_at else None,
    }
    if full:
        data["text"] = t.text
        data["file"] = get_file_url(t.file) if t.file else None
        data["reference_type"] = t.reference_type
        data["reference_id"] = t.reference_id
        data["admin_reply"] = t.admin_reply
        data["closed_at"] = t.closed_at.isoformat() if t.closed_at else None
        data["close_reason"] = t.close_reason
    return data


# ═══════════════════════════════════════════════════════════
# ایجاد تیکت
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
            saved_name = handle_save_file(file)
        except Exception:
            logger.exception("file save failed")
            return error_response("خطا در ذخیره فایل")

    try:
        ticket = await sync_to_async(create_ticket)(
            user,
            category=form.get("category", "other"),
            subject=form.get("subject"),
            text=form.get("text"),
            file_name=saved_name,
            reference_type=form.get("reference_type"),
            reference_id=form.get("reference_id"),
            priority=form.get("priority", "normal"),
        )
        return success_response(
            "تیکت ثبت شد و در انتظار بررسی است",
            _serialize_ticket(ticket, full=True),
        )
    except SupportError as e:
        return error_response(str(e), status_code=400)
    except Exception:
        logger.exception("create_ticket failed")
        return error_response("خطا در ثبت تیکت")


# ═══════════════════════════════════════════════════════════
# لیست و جزئیات
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
        .order_by("-created_at")
    )
    if status and status in Support.Status.values:
        qs = qs.filter(status=status)
    return [_serialize_ticket(t) for t in qs]


@router.get("/{ticket_id}/")
async def get_ticket(ticket_id: int, user: User = Depends(get_current_user)):
    data = await sync_to_async(_get_one)(ticket_id, user.id)
    if not data:
        return error_response("تیکت یافت نشد", status_code=404)
    return success_response("جزئیات تیکت", data)


@sync_to_async
def _get_one(ticket_id, user_id):
    t = Support.objects.filter(id=ticket_id, user_id=user_id).first()
    return _serialize_ticket(t, full=True) if t else None


# ═══════════════════════════════════════════════════════════
# بستن توسط کاربر
# ═══════════════════════════════════════════════════════════
@router.post("/{ticket_id}/close/")
async def close_ticket(ticket_id: int, user: User = Depends(get_current_user)):
    try:
        ticket = await sync_to_async(close_by_user)(ticket_id, user.id)
        return success_response("تیکت بسته شد", _serialize_ticket(ticket))
    except SupportError as e:
        return error_response(str(e), status_code=400)