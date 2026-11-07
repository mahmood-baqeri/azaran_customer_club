# app_fastapi/views/factor/factor.py

import logging
from datetime import datetime

from asgiref.sync import sync_to_async
from fastapi import APIRouter, Depends, File, UploadFile

from applications.factor.models import Factor
from applications.factor.services import FactorError, create_factor
from applications.user.models import User
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.fileManager import get_file_url, handle_save_file
from app_fastapi.conf.response import error_response, success_response
from app_fastapi.views.user.user_helper import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


def _serialize_factor(f: Factor, *, full: bool = False) -> dict:
    data = {
        "id": f.id,
        "invoice_number": f.invoice_number,
        "status": f.status,
        "status_display": f.get_status_display(),
        "photo": get_file_url(f.photo),
        "amount": f.amount,
        "invoice_issue_at": f.invoice_issue_at.isoformat() if f.invoice_issue_at else None,
        "shop_name": f.shop_name,
        "created_at": f.created_at.isoformat() if f.created_at else None,
        "approved_at": f.approved_at.isoformat() if f.approved_at else None,
        "rejection_reason": f.rejection_reason,
    }
    if full:
        data["seller"] = {
            "phone": f.seller_phone,
            "address": f.seller_address,
        }
        data["meterage"] = {
            "number_water_taps": f.number_water_taps,
            "number_connections": f.number_connections,
            "pipe_length": f.pipe_length,
        }
        data["owner"] = {
            "uuid": str(f.user.uuid),
            "name": f.user.full_name,
            "mobile": f.user.mobile,
        }
    return data


# ═══════════════════════════════════════════════════════════
# ایجاد فاکتور
# ═══════════════════════════════════════════════════════════
@router.post("/create/")
async def create_factor_endpoint(
    photo: UploadFile = File(...),
    form: dict = Depends(DependencyDataRequest),
    user: User = Depends(get_current_user),
):
    if not photo:
        return error_response("تصویر فاکتور الزامی است")

    try:
        saved_name = handle_save_file(photo)
    except Exception:
        logger.exception("photo save failed")
        return error_response("خطا در ذخیره تصویر")

    try:
        factor = await sync_to_async(create_factor)(
            user,
            photo_file_name=saved_name,
            amount=_to_int(form.get("amount")),
            invoice_number=form.get("invoice_number"),
            invoice_issue_at=_to_datetime(form.get("invoice_issue_at")),
            number_water_taps=_to_int(form.get("number_water_taps")),
            number_connections=_to_int(form.get("number_connections")),
            pipe_length=_to_int(form.get("pipe_length")),
            shop_name=form.get("shop_name"),
            seller_phone=form.get("seller_phone"),
            seller_address=form.get("seller_address"),
        )
        return success_response(
            "فاکتور ثبت شد و در انتظار تأیید است",
            _serialize_factor(factor, full=True),
        )
    except FactorError as e:
        return error_response(str(e), status_code=400)
    except Exception:
        logger.exception("create_factor failed")
        return error_response("خطا در ثبت فاکتور")


def _to_int(val):
    if val is None or val == "":
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def _to_datetime(val):
    if not val:
        return None
    try:
        return datetime.fromisoformat(str(val))
    except (ValueError, TypeError):
        return None


# ═══════════════════════════════════════════════════════════
# لیست و جزئیات
# ═══════════════════════════════════════════════════════════
@router.get("/list/")
async def list_my_factors(user: User = Depends(get_current_user)):
    data = await sync_to_async(_list_my)(user.id)
    return success_response("فاکتورهای من", data)


@sync_to_async
def _list_my(user_id):
    qs = (
        Factor.objects
        .select_related("user")
        .filter(user_id=user_id)
        .order_by("-created_at")
    )
    return [_serialize_factor(f, full=False) for f in qs]


@router.get("/{factor_id}/")
async def get_factor(factor_id: int, user: User = Depends(get_current_user)):
    data = await sync_to_async(_get_one)(factor_id, user.id)
    if not data:
        return error_response("فاکتور یافت نشد", status_code=404)
    return success_response("جزئیات فاکتور", data)


@sync_to_async
def _get_one(factor_id, user_id):
    f = (
        Factor.objects
        .select_related("user")
        .filter(id=factor_id, user_id=user_id)
        .first()
    )
    return _serialize_factor(f, full=True) if f else None