# app_fastapi/views/learn/learn.py

import logging
from asgiref.sync import sync_to_async
from fastapi import APIRouter, Depends

from applications.learn.models import Learn
from applications.user.models import User
from app_fastapi.conf.fileManager import get_file_url
from app_fastapi.conf.response import error_response, success_response
from app_fastapi.views.user.helper import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


# ═══════════════════════════════════════════════════════════
# Serializers
# ═══════════════════════════════════════════════════════════
def _serialize_learn(l: Learn, full: bool = False) -> dict:
    data = {
        "id": l.id,
        "title": l.title,
        "sub_text": l.sub_text,
        "photo": get_file_url(l.photo) if l.photo else None,
        "size": l.size,
        "size_display": l.get_size_display(),
        "time": l.time,
        "caption": l.caption,
        "created_at": l.created_at.isoformat() if l.created_at else None,
    }
    
    if full:
        data["full_text"] = l.full_text
        
    return data


# ═══════════════════════════════════════════════════════════
# ۱. لیست آموزش‌ها
# ═══════════════════════════════════════════════════════════
@router.get("/list/")
async def list_learns(
    size: str = None, # می‌توانید از فرانت‌اند فیلتر بفرستید (مثلا ?size=full)
    user: User = Depends(get_current_user),
):
    # ✅ فراخوانی تابع دیتابیس
    data = await _get_learns(size)
    return success_response("لیست آموزش‌ها", data)


@sync_to_async
def _get_learns(size: str = None):
    # فقط آموزش‌های فعال را واکشی می‌کنیم
    qs = Learn.objects.filter(is_active=True)
    
    # اگر کاربر فیلتر سایز را فرستاده بود، اعمال می‌کنیم
    if size and size in Learn.Size.values:
        qs = qs.filter(size=size)
        
    return [_serialize_learn(l) for l in qs]


# ═══════════════════════════════════════════════════════════
# ۲. جزئیات آموزش
# ═══════════════════════════════════════════════════════════
@router.get("/{learn_id}/")
async def get_learn_detail(
    learn_id: int,
    user: User = Depends(get_current_user),
):
    data = await _get_one(learn_id)
    if not data:
        return error_response("آموزش یافت نشد", status_code=404)
        
    return success_response("جزئیات آموزش", data)


@sync_to_async
def _get_one(learn_id: int):
    # فقط در صورتی که آموزش فعال باشد، جزئیات را برمی‌گردانیم
    l = Learn.objects.filter(id=learn_id, is_active=True).first()
    return _serialize_learn(l, full=True) if l else None