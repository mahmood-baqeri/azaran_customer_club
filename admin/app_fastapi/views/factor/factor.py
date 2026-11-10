# app_fastapi/views/factor/factor.py

import logging
from datetime import datetime

from asgiref.sync import sync_to_async
from fastapi import APIRouter, Depends, File, UploadFile
from django.db import transaction

from applications.factor.models import Factor
from applications.factor.services import FactorError, create_factor
from applications.user.models import User
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.fileManager import get_file_url, handle_save_file
from app_fastapi.conf.response import error_response, success_response
from app_fastapi.views.user.helper import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

_EDIT_LOCKED_MSG = "تنها تا قبل از تایید فاکتور امکان ویرایش یا حذف وجود دارد"


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
# ۱. ایجاد فاکتور
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
        saved_name = await sync_to_async(handle_save_file)(photo)
    except Exception:
        logger.exception("photo save failed")
        return error_response("خطا در ذخیره تصویر")

    try:
        # اجرای create_factor + serialize هر دو در thread pool
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
        factor_data = await sync_to_async(_serialize_factor)(factor, full=True)
        return success_response(
            "فاکتور ثبت شد و در انتظار تأیید است",
            factor_data,
        )
    except FactorError as e:
        return error_response(str(e), status_code=400)
    except Exception:
        logger.exception("create_factor failed")
        return error_response("خطا در ثبت فاکتور")


# ═══════════════════════════════════════════════════════════
# ۲. ویرایش فاکتور (فقط PENDING)
# ═══════════════════════════════════════════════════════════
@router.post("/{factor_id}/update/")
async def update_factor_endpoint(
    factor_id: int,
    photo: UploadFile | None = File(None),
    form: dict = Depends(DependencyDataRequest),
    user: User = Depends(get_current_user),
):
    try:
        saved_name = None
        if photo:
            saved_name = await sync_to_async(handle_save_file)(photo)

        # _update_factor_db از قبل @sync_to_async است → مستقیم await
        result = await _update_factor_db(factor_id, user.id, form, saved_name)
        if result.get("error"):
            return error_response(result["error"], status_code=400)

        return success_response("فاکتور با موفقیت ویرایش شد", result["data"])
    except Exception:
        logger.exception("update_factor failed")
        return error_response("خطا در ویرایش فاکتور")


@sync_to_async
def _update_factor_db(factor_id, user_id, form, saved_name):
    with transaction.atomic():
        f = (
            Factor.objects
            .select_for_update()
            .select_related("user")   # جلوگیری از lazy-load در serialize
            .filter(id=factor_id, user_id=user_id)
            .first()
        )
        if not f:
            return {"error": "فاکتور یافت نشد"}
        if f.status != Factor.Status.PENDING:
            return {"error": _EDIT_LOCKED_MSG}

        update_fields = []

        if saved_name:
            f.photo = saved_name
            update_fields.append("photo")

        if "amount" in form:
            f.amount = _to_int(form.get("amount"))
            update_fields.append("amount")

        if "invoice_number" in form:
            f.invoice_number = form.get("invoice_number")
            update_fields.append("invoice_number")

        if "invoice_issue_at" in form:
            f.invoice_issue_at = _to_datetime(form.get("invoice_issue_at"))
            update_fields.append("invoice_issue_at")

        if "number_water_taps" in form:
            f.number_water_taps = _to_int(form.get("number_water_taps"))
            update_fields.append("number_water_taps")

        if "number_connections" in form:
            f.number_connections = _to_int(form.get("number_connections"))
            update_fields.append("number_connections")

        if "pipe_length" in form:
            f.pipe_length = _to_int(form.get("pipe_length"))
            update_fields.append("pipe_length")

        if "shop_name" in form:
            f.shop_name = form.get("shop_name")
            update_fields.append("shop_name")

        if "seller_phone" in form:
            f.seller_phone = form.get("seller_phone")
            update_fields.append("seller_phone")

        if "seller_address" in form:
            f.seller_address = form.get("seller_address")
            update_fields.append("seller_address")

        if update_fields:
            f.save(update_fields=update_fields)

        f.refresh_from_db()

        # serialize داخل کانتکست sync انجام می‌شود
        return {"data": _serialize_factor(f, full=True)}


# ═══════════════════════════════════════════════════════════
# ۳. حذف فاکتور (فقط PENDING)
# ═══════════════════════════════════════════════════════════
@router.delete("/{factor_id}/")
async def delete_factor_endpoint(
    factor_id: int,
    user: User = Depends(get_current_user),
):
    try:
        result = await _delete_factor_db(factor_id, user.id)
        if result.get("error"):
            return error_response(result["error"], status_code=400)
        return success_response("فاکتور با موفقیت حذف شد", {})
    except Exception:
        logger.exception("delete_factor failed")
        return error_response("خطا در حذف فاکتور")


@sync_to_async
def _delete_factor_db(factor_id, user_id):
    with transaction.atomic():
        f = (
            Factor.objects
            .select_for_update()
            .filter(id=factor_id, user_id=user_id)
            .first()
        )
        if not f:
            return {"error": "فاکتور یافت نشد"}
        if f.status != Factor.Status.PENDING:
            return {"error": _EDIT_LOCKED_MSG}

        f.delete()
        return {"success": True}


# ═══════════════════════════════════════════════════════════
# ۴. لیست و جزئیات
# ═══════════════════════════════════════════════════════════
@router.get("/list/")
async def list_my_factors(user: User = Depends(get_current_user)):
    # ✅ اصلاح: _list_my از قبل @sync_to_async است → مستقیم await
    data = await _list_my(user.id)
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
    # ✅ اصلاح: _get_one از قبل @sync_to_async است → مستقیم await
    data = await _get_one(factor_id, user.id)
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


# ═══════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════
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