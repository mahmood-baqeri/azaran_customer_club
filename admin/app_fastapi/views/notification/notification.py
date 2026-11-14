# app_fastapi/views/notification/notification.py
import logging
from typing import Optional

from channels.db import database_sync_to_async
from fastapi import APIRouter, Depends, HTTPException, Query

from applications.notification import services as notification_service
from applications.notification.models import Notification
from applications.user.models import User
from app_fastapi.conf.fileManager import get_file_url
from app_fastapi.conf.response import success_response, error_response
from app_fastapi.views.user.helper import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Serializer
# ═══════════════════════════════════════════════════════════
def _serialize(n: Notification) -> dict:
    return {
        "id": n.id,
        "title": n.title,
        "body": n.body,
        "image": get_file_url(n.image) if n.image else None,
        "image_size": n.image_size,
        "image_type": n.image_type,
        "type": n.notification_type,
        "type_display": n.get_notification_type_display(),
        "priority": n.priority,
        "priority_display": n.get_priority_display(),
        "action_type": n.action_type,
        "action_url": n.action_url,
        "action_data": n.action_data or {},
        "is_read": bool(getattr(n, "is_read", False)),
        "sent_at": n.sent_at.isoformat() if n.sent_at else None,
        "created_at": n.created_at.isoformat() if n.created_at else None,
        "expires_at": n.expires_at.isoformat() if n.expires_at else None,
    }


# ═══════════════════════════════════════════════════════════
# List
# ═══════════════════════════════════════════════════════════
@router.get("/")
async def list_notifications(
    user: User = Depends(get_current_user),
    unread_only: bool = Query(False, description="فقط نخوانده‌ها"),
    type: Optional[str] = Query(
        None,
        description="system|promotion|gift|project|factor|support|account|review|visit|other",
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """لیست نوتیفیکیشن‌های کاربر با صفحه‌بندی"""
    try:
        qs = (
            Notification.objects.unread_for_user(user)
            if unread_only
            else Notification.objects.visible_for_user(user)
        )
        if type:
            qs = qs.filter(notification_type=type)

        total = await database_sync_to_async(qs.count)()

        offset = (page - 1) * page_size
        items = await database_sync_to_async(
            lambda: list(qs.order_by("-sent_at", "-id")[offset : offset + page_size])
        )()

        return success_response(
            "لیست نوتیفیکیشن‌ها",
            {
                "items": [_serialize(n) for n in items],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
            },
        )
    except Exception:
        logger.exception("list_notifications failed user=%s", user.id)
        return error_response("خطا در دریافت نوتیفیکیشن‌ها")


# ═══════════════════════════════════════════════════════════
# Unread count (برای badge هدر)
# ═══════════════════════════════════════════════════════════
@router.get("/unread-count/")
async def unread_count(user: User = Depends(get_current_user)):
    try:
        count = await database_sync_to_async(
            lambda: Notification.objects.unread_for_user(user).count()
        )()
        return success_response("تعداد نخوانده‌ها", {"count": count})
    except Exception:
        logger.exception("unread_count failed user=%s", user.id)
        return error_response("خطا در دریافت تعداد نخوانده‌ها")


# ═══════════════════════════════════════════════════════════
# Detail (+ auto mark as read)
# ═══════════════════════════════════════════════════════════
@router.get("/{notification_id}/")
async def detail(notification_id: int, user: User = Depends(get_current_user)):
    try:
        n = await database_sync_to_async(
            lambda: Notification.objects
                .visible_for_user(user)
                .filter(pk=notification_id)
                .first()
        )()
        if not n:
            raise HTTPException(status_code=404, detail="نوتیفیکیشن یافت نشد")

        if not n.is_read:
            await database_sync_to_async(notification_service.mark_as_read)(user, n)
            n.is_read = True  # annotation قدیمی را برای پاسخ اصلاح کن

        return success_response("جزئیات نوتیفیکیشن", _serialize(n))
    except HTTPException:
        raise
    except Exception:
        logger.exception("detail failed user=%s notif=%s", user.id, notification_id)
        return error_response("خطا در دریافت نوتیفیکیشن")


# ═══════════════════════════════════════════════════════════
# Mark as read
# ═══════════════════════════════════════════════════════════
@router.post("/{notification_id}/read/")
async def mark_read(notification_id: int, user: User = Depends(get_current_user)):
    try:
        n = await database_sync_to_async(
            lambda: Notification.objects
                .for_user(user)
                .filter(pk=notification_id)
                .first()
        )()
        if not n:
            raise HTTPException(status_code=404, detail="نوتیفیکیشن یافت نشد")

        changed = await database_sync_to_async(notification_service.mark_as_read)(user, n)
        return success_response(
            "نوتیفیکیشن خوانده شد" if changed else "قبلاً خوانده شده بود",
            {"changed": changed},
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("mark_read failed user=%s notif=%s", user.id, notification_id)
        return error_response("خطا در به‌روزرسانی")


# ═══════════════════════════════════════════════════════════
# Mark all as read
# ═══════════════════════════════════════════════════════════
@router.post("/read-all/")
async def mark_all_read(user: User = Depends(get_current_user)):
    try:
        count = await database_sync_to_async(notification_service.mark_all_as_read)(user)
        return success_response(
            f"{count} نوتیفیکیشن خوانده شد",
            {"count": count},
        )
    except Exception:
        logger.exception("mark_all_read failed user=%s", user.id)
        return error_response("خطا در به‌روزرسانی")


# ═══════════════════════════════════════════════════════════
# Dismiss
# ═══════════════════════════════════════════════════════════
@router.post("/{notification_id}/dismiss/")
async def dismiss(notification_id: int, user: User = Depends(get_current_user)):
    try:
        n = await database_sync_to_async(
            lambda: Notification.objects
                .for_user(user)
                .filter(pk=notification_id)
                .first()
        )()
        if not n:
            raise HTTPException(status_code=404, detail="نوتیفیکیشن یافت نشد")

        changed = await database_sync_to_async(notification_service.dismiss)(user, n)
        return success_response(
            "از لیست حذف شد" if changed else "قبلاً حذف شده بود",
            {"changed": changed},
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("dismiss failed user=%s notif=%s", user.id, notification_id)
        return error_response("خطا در حذف نوتیفیکیشن")
   
   
   
   
   
#

# Method	URL	توضیح
# GET	/user/notifications/	لیست با صفحه‌بندی
# GET	/user/notifications/?unread_only=true	فقط نخوانده‌ها
# GET	/user/notifications/?type=gift	فیلتر دسته
# GET	/user/notifications/unread-count/	تعداد badge
# GET	/user/notifications/{id}/	جزئیات (+ auto read)
# POST	/user/notifications/{id}/read/	خوانده‌شده
# POST	/user/notifications/read-all/	همه را خوانده کن
# POST	/user/notifications/{id}/dismiss/	حذف از لیست

#