# app_fastapi/views/gift.py

import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, Request
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.core.files.storage import default_storage

from app_fastapi.views.user.user_helper import get_current_user
from app_fastapi.conf.fileManager import handle_save_file
from applications.gift.models import Gift
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.response import success_response, error_response
from applications.user.models import User
from django.utils.translation import gettext_lazy as _

router = APIRouter()


def gift_serialize(g: Gift) -> dict:
    return {
        "id": g.id,
        "title": g.title,
        "description": g.description,
        "photo": str(g.photo) if g.photo else None,
        "gallery": g.gallery or [],
        "azar_value": g.azar_value,
        "stock": g.stock,
        "is_active": g.is_active,
        "created_at": g.created_at.isoformat() if g.created_at else None,
    }


# -------------------------------------------------
# List
# -------------------------------------------------
@router.get("/")
async def list_gifts(
    request: Request,
    is_active: Optional[str] = None,
    search: Optional[str] = None,
    user: User = Depends(get_current_user),
):
    try:
        items = await async_list_gifts(is_active, search, user.nature)
        return success_response("All Gifts", items)
    except Exception as e:
        return error_response(str(e))


@database_sync_to_async
def async_list_gifts(is_active, search, nature):
    qs = Gift.objects.filter(is_active=True)

    if nature not in ("manager", "executive"):
        qs = qs.filter(is_active=True)

    qs = qs.filter(for_user=nature)

    if is_active in ("true", "1"):
        qs = qs.filter(is_active=True)
    elif is_active in ("false", "0"):
        qs = qs.filter(is_active=False)

    if search:
        qs = qs.filter(title__icontains=search)

    return [gift_serialize(g) for g in qs.order_by("-created_at")]


# -------------------------------------------------
# Detail
# -------------------------------------------------
@router.get("/{gift_id}/")
async def get_gift(gift_id: int, user: User = Depends(get_current_user)):
    try:
        item = await async_get_gift(gift_id,  user.nature)
        if not item:
            return error_response("هدیه یافت نشد", 404)
        return success_response("Gift Detail", item)
    except Exception as e:
        return error_response(str(e))


@database_sync_to_async
def async_get_gift(gift_id, nature):
    g = Gift.objects.filter(id=gift_id, for_user=nature).first()
    return gift_serialize(g) if g else None

