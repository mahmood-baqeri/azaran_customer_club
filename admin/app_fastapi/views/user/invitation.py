# admin/app_fastapi/views/user/invitation.py

import logging

from asgiref.sync import sync_to_async
from fastapi import APIRouter, Depends

from applications.user.models import User, UserInvitation
from app_fastapi.conf.fileManager import get_file_url
from app_fastapi.conf.response import success_response, error_response
from app_fastapi.views.user.user_helper import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


# ═══════════════════════════════════════════════════════════
# Serializer
# ═══════════════════════════════════════════════════════════
def _serialize_invitation(inv: UserInvitation) -> dict:
    """سریالایزر برای اطلاعات دعوت‌ها"""
    
    # اطلاعات پایه دعوت
    data = {
        "id": inv.id,
        "invited_mobile": inv.invited_mobile,
        "is_registered": inv.invited_user is not None, # آیا شخص ثبت‌نام کرده است؟
        "is_rewarded": inv.is_rewarded,                # آیا پاداش داده شده است؟
        "invited_at": inv.created_at.isoformat() if inv.created_at else None,
        "rewarded_at": inv.rewarded_at.isoformat() if inv.rewarded_at else None,
        "user": None
    }

    # اگر کاربر ثبت‌نام کرده باشد، اطلاعات پروفایل او را هم برمی‌گردانیم
    if inv.invited_user:
        data["user"] = {
            "uuid": str(inv.invited_user.uuid),
            "name": inv.invited_user.full_name,
            "avatar": get_file_url(inv.invited_user.avatar),
            "joined_at": inv.invited_user.date_joined.isoformat() if inv.invited_user.date_joined else None,
        }
        
    return data


# ═══════════════════════════════════════════════════════════
# لیست افرادی که با کد دعوت کاربر وارد شده‌اند
# ═══════════════════════════════════════════════════════════
@router.get("/list/")
async def list_my_invitations(user: User = Depends(get_current_user)):
    """
    دریافت لیست تمام افرادی که با کد دعوت این کاربر ثبت‌نام کرده‌اند 
    (یا شماره آن‌ها توسط این کاربر دعوت شده است)
    """
    try:
        data = await _get_invitations_db(user.id)
        return success_response("لیست افراد دعوت‌شده", data)
    except Exception:
        logger.exception("list_my_invitations failed")
        return error_response("خطا در دریافت لیست دعوت‌ها")


@sync_to_async
def _get_invitations_db(user_id: int):
    # واکشی دعوت‌هایی که توسط این کاربر ارسال شده است
    # از select_related برای جلوگیری از کوئری اضافی هنگام دسترسی به invited_user استفاده می‌کنیم
    invitations = (
        UserInvitation.objects
        .select_related('invited_user')
        .filter(inviter_id=user_id)
        .order_by('-created_at')
    )
    
    return [_serialize_invitation(inv) for inv in invitations]