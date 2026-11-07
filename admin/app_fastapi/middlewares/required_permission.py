from asgiref.sync import sync_to_async
from fastapi import Depends
from fastapi.responses import JSONResponse
from app_fastapi.conf.response import error_response
from admin.app_fastapi.views.user.user_helper import get_current_user
from applications.user.models import User
from django.utils.translation import gettext_lazy as _


def RequiredPermission(nature: str):
    async def _check_permission(current_user: User = Depends(get_current_user)):
        # بررسی نوع کاربر
        if current_user.nature != nature:
            return error_response(f"{_('Access Denied')}", status_code=400)

        responsible = None
        if nature == "manager":
            # responsible = await sync_to_async(lambda: Coach.objects.filter(user_id=current_user.id).first())()
            if not responsible:
                return error_response(f"{_('Information not found')}", status_code=400)
            return responsible

        return responsible

    return _check_permission
