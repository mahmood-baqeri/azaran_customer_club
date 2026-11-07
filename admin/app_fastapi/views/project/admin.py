# app_fastapi/views/project/admin.py

import logging

from asgiref.sync import sync_to_async
from fastapi import APIRouter, Depends

from applications.project.models import Project
from applications.project.services import (
    ProjectError,
    approve_project,
    reject_project,
)
from applications.user.models import User
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.response import error_response, success_response
from app_fastapi.views.user.user_helper import get_current_user
from app_fastapi.views.project.project import _serialize_project

logger = logging.getLogger(__name__)
router = APIRouter()


def _require_admin(user: User):
    if not (user.is_staff or user.is_superuser):
        raise PermissionError("دسترسی ادمین لازم است")


# ═══════════════════════════════════════════════════════════
# لیست پروژه‌ها برای ادمین
# ═══════════════════════════════════════════════════════════
@router.get("/list/")
async def admin_list_projects(
    status: str = None,
    admin: User = Depends(get_current_user),
):
    try:
        _require_admin(admin)
        data = await sync_to_async(_list_projects)(status)
        return success_response("همه پروژه‌ها", data)
    except PermissionError as e:
        return error_response(str(e), status_code=403)


@sync_to_async
def _list_projects(status):
    qs = (
        Project.objects
        .select_related("user")
        .prefetch_related("colleagues", "attachments")
        .order_by("-created_at")
    )
    if status and status in Project.Status.values:
        qs = qs.filter(status=status)
    return [_serialize_project(p, full=True) for p in qs]


# ═══════════════════════════════════════════════════════════
# تأیید پروژه (→ امتیازدهی خودکار)
# ═══════════════════════════════════════════════════════════
@router.post("/{project_id}/approve/")
async def admin_approve_project(
    project_id: int,
    admin: User = Depends(get_current_user),
):
    try:
        _require_admin(admin)
        project = await sync_to_async(approve_project)(project_id, admin)
        return success_response(
            "پروژه تأیید شد و امتیازها واریز شدند",
            _serialize_project(project, full=True),
        )
    except PermissionError as e:
        return error_response(str(e), status_code=403)
    except ProjectError as e:
        return error_response(str(e), status_code=400)
    except Exception:
        logger.exception("approve_project failed")
        return error_response("خطا در تأیید پروژه")


# ═══════════════════════════════════════════════════════════
# رد پروژه
# ═══════════════════════════════════════════════════════════
@router.post("/{project_id}/reject/")
async def admin_reject_project(
    project_id: int,
    form: dict = Depends(DependencyDataRequest),
    admin: User = Depends(get_current_user),
):
    try:
        _require_admin(admin)
        project = await sync_to_async(reject_project)(
            project_id, admin, reason=form.get("reason", ""),
        )
        return success_response("پروژه رد شد", _serialize_project(project))
    except PermissionError as e:
        return error_response(str(e), status_code=403)
    except ProjectError as e:
        return error_response(str(e), status_code=400)
    except Exception:
        logger.exception("reject_project failed")
        return error_response("خطا در رد پروژه")