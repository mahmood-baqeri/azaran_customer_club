# app_fastapi/views/factor/admin.py

import logging

from asgiref.sync import sync_to_async
from fastapi import APIRouter, Depends

from applications.factor.models import Factor
from applications.factor.services import (
    FactorError,
    approve_factor,
    reject_factor,
)
from applications.user.models import User
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.response import error_response, success_response
from app_fastapi.views.user.helper import get_current_user
from app_fastapi.views.factor.factor import _serialize_factor

logger = logging.getLogger(__name__)
router = APIRouter()


def _require_admin(user: User):
    if not (user.is_staff or user.is_superuser):
        raise PermissionError("دسترسی ادمین لازم است")


@router.get("/list/")
async def admin_list_factors(status: str = None, admin: User = Depends(get_current_user)):
    try:
        _require_admin(admin)
        data = await sync_to_async(_list)(status)
        return success_response("همه فاکتورها", data)
    except PermissionError as e:
        return error_response(str(e), status_code=403)


@sync_to_async
def _list(status):
    qs = (
        Factor.objects
        .select_related("user")
        .order_by("-created_at")
    )
    if status and status in Factor.Status.values:
        qs = qs.filter(status=status)
    return [_serialize_factor(f, full=True) for f in qs]


@router.post("/{factor_id}/approve/")
async def admin_approve_factor(factor_id: int, admin: User = Depends(get_current_user)):
    try:
        _require_admin(admin)
        factor = await sync_to_async(approve_factor)(factor_id, admin)
        return success_response(
            "فاکتور تأیید شد و امتیاز واریز شد",
            _serialize_factor(factor, full=True),
        )
    except PermissionError as e:
        return error_response(str(e), status_code=403)
    except FactorError as e:
        return error_response(str(e), status_code=400)
    except Exception:
        logger.exception("approve_factor failed")
        return error_response("خطا در تأیید فاکتور")


@router.post("/{factor_id}/reject/")
async def admin_reject_factor(
    factor_id: int,
    form: dict = Depends(DependencyDataRequest),
    admin: User = Depends(get_current_user),
):
    try:
        _require_admin(admin)
        factor = await sync_to_async(reject_factor)(
            factor_id, admin, reason=form.get("reason", ""),
        )
        return success_response("فاکتور رد شد", _serialize_factor(factor))
    except PermissionError as e:
        return error_response(str(e), status_code=403)
    except FactorError as e:
        return error_response(str(e), status_code=400)
    except Exception:
        logger.exception("reject_factor failed")
        return error_response("خطا در رد فاکتور")