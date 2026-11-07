# app_fastapi/views/support/admin.py

import logging

from asgiref.sync import sync_to_async
from fastapi import APIRouter, Depends

from applications.support.models import Support
from applications.support.services import (
    SupportError,
    change_status,
    reply_ticket,
)
from applications.user.models import User
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.response import error_response, success_response
from app_fastapi.views.user.user_helper import get_current_user
from app_fastapi.views.support.support import _serialize_ticket

logger = logging.getLogger(__name__)
router = APIRouter()


def _require_admin(user: User):
    if not (user.is_staff or user.is_superuser):
        raise PermissionError("دسترسی ادمین لازم است")


@router.get("/list/")
async def admin_list_tickets(
    status: str = None,
    category: str = None,
    admin: User = Depends(get_current_user),
):
    try:
        _require_admin(admin)
        data = await sync_to_async(_list)(status, category)
        return success_response("همه تیکت‌ها", data)
    except PermissionError as e:
        return error_response(str(e), status_code=403)


@sync_to_async
def _list(status, category):
    qs = Support.objects.select_related("user").order_by("-created_at")
    if status and status in Support.Status.values:
        qs = qs.filter(status=status)
    if category and category in Support.Category.values:
        qs = qs.filter(category=category)
    return [_serialize_ticket(t, full=True) for t in qs]


@router.post("/{ticket_id}/reply/")
async def admin_reply(
    ticket_id: int,
    form: dict = Depends(DependencyDataRequest),
    admin: User = Depends(get_current_user),
):
    try:
        _require_admin(admin)
        ticket = await sync_to_async(reply_ticket)(
            ticket_id, admin,
            reply_text=form.get("reply_text", ""),
            new_status=form.get("new_status"),
        )
        return success_response("پاسخ ثبت شد", _serialize_ticket(ticket, full=True))
    except PermissionError as e:
        return error_response(str(e), status_code=403)
    except SupportError as e:
        return error_response(str(e), status_code=400)
    except Exception:
        logger.exception("reply_ticket failed")
        return error_response("خطا در ثبت پاسخ")


@router.post("/{ticket_id}/status/")
async def admin_change_status(
    ticket_id: int,
    form: dict = Depends(DependencyDataRequest),
    admin: User = Depends(get_current_user),
):
    try:
        _require_admin(admin)
        ticket = await sync_to_async(change_status)(
            ticket_id, admin,
            new_status=form.get("new_status"),
            reason=form.get("reason"),
        )
        return success_response("وضعیت تغییر کرد", _serialize_ticket(ticket))
    except PermissionError as e:
        return error_response(str(e), status_code=403)
    except SupportError as e:
        return error_response(str(e), status_code=400)
    except Exception:
        logger.exception("change_status failed")
        return error_response("خطا در تغییر وضعیت")