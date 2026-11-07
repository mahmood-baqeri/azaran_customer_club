# app_fastapi/views/project/project.py

import logging
import re
from datetime import datetime

from asgiref.sync import sync_to_async
from fastapi import APIRouter, Depends, File, UploadFile
from django.db import transaction
from django.db.models import Sum
from typing import Optional
from applications.project.models import Attachment, Colleague, Project
from applications.project.services import (
    ProjectError,
    add_attachment,
    create_project,
    delete_attachment,
    delete_project,
)
from applications.user.models import User
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.fileManager import handle_save_file, get_file_url
from app_fastapi.conf.response import error_response, success_response
from app_fastapi.views.user.user_helper import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# پیام یکدست در view برای عملیات قفل‌شده
_EDIT_LOCKED_MSG = "این عملیات فقط تا قبل از تأیید پروژه امکان‌پذیر است"


# ═══════════════════════════════════════════════════════════
# Serializers (فقط از داخل sync context)
# ═══════════════════════════════════════════════════════════
def _serialize_colleague(c: Colleague) -> dict:
    return {
        "id": c.id,
        "user_uuid": str(c.user.uuid),
        "user_mobile": c.user.mobile,
        "user_name": c.user.full_name,
        "percent": c.percent,
        "is_active": c.is_active,
        "avatar": get_file_url(c.user.avatar),
    }


def _serialize_attachment(a: Attachment) -> dict:
    return {
        "id": a.id,
        "type": a.type,
        "type_display": a.get_type_display(),
        "file": get_file_url(a.file),
        "file_size": a.file_size,
        "status": a.status,
        "status_display": a.get_status_display(),
    }


def _serialize_project(p: Project, *, full: bool = False) -> dict:
    data = {
        "id": p.id,
        "type": p.type,
        "type_display": p.get_type_display(),
        "title": p.title,
        "status": p.status,
        "status_display": p.get_status_display(),
        "completion_at": p.completion_at.isoformat() if p.completion_at else None,
        "address": p.address,
        "owner_mobile": p.owner_mobile,
        "unit_count": p.unit_count,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "approved_at": p.approved_at.isoformat() if p.approved_at else None,
        "rejection_reason": p.rejection_reason,
    }
    if full:
        data["meterage"] = {
            "number_water_taps": p.number_water_taps,
            "number_gas_taps": p.number_gas_taps,
            "number_connections": p.number_connections,
            "pipe_length": p.pipe_length,
        }
        data["owner"] = {
            "uuid": str(p.user.uuid),
            "name": p.user.full_name,
            "mobile": p.user.mobile,
        }
        data["colleagues"] = [_serialize_colleague(c) for c in p.colleagues.all()]
        data["attachments"] = [_serialize_attachment(a) for a in p.attachments.all()]
    return data


# ═══════════════════════════════════════════════════════════
# ۱. ایجاد پروژه
# ═══════════════════════════════════════════════════════════
@router.post("/create/")
async def create_project_endpoint(
    form: dict = Depends(DependencyDataRequest),
    user: User = Depends(get_current_user),
):
    try:
        data = await _create_project_and_serialize(
            user_id=user.id,
            payload={
                "type": form.get("type", "water"),
                "title": form.get("title"),
                "address": form.get("address"),
                "owner_mobile": form.get("owner_mobile"),
                "unit_count": _to_int(form.get("unit_count")),
                "number_water_taps": _to_int(form.get("number_water_taps")),
                "number_gas_taps": _to_int(form.get("number_gas_taps")),
                "number_connections": _to_int(form.get("number_connections")),
                "pipe_length": _to_int(form.get("pipe_length")),
                "completion_at": _to_datetime(form.get("completion_at")),
            },
        )
        return success_response("پروژه ثبت شد", data)
    except ProjectError as e:
        return error_response(str(e), status_code=400)
    except Exception:
        logger.exception("create_project failed")
        return error_response("خطا در ثبت پروژه")


@sync_to_async
def _create_project_and_serialize(user_id: int, payload: dict) -> dict:
    with transaction.atomic():
        owner = User.objects.get(pk=user_id)
        project = create_project(owner, colleagues=[], **payload)
        project = (
            Project.objects
            .select_related("user")
            .prefetch_related("colleagues__user", "attachments")
            .get(pk=project.pk)
        )
        return _serialize_project(project, full=True)


# ═══════════════════════════════════════════════════════════
# ۲. ویرایش پروژه — فقط PENDING
# ═══════════════════════════════════════════════════════════
@router.post("/{project_id}/update/")
async def update_project_endpoint(
    project_id: int,
    form: dict = Depends(DependencyDataRequest),
    user: User = Depends(get_current_user),
):
    try:
        result = await _update_project_and_serialize(project_id, user.id, form)
        if result is None:
            return error_response("پروژه یافت نشد", 404)
        if result.get("error"):
            return error_response(result["error"], 400)
        return success_response("پروژه با موفقیت ویرایش شد", result["data"])
    except Exception:
        logger.exception("update_project failed")
        return error_response("خطا در ویرایش پروژه")


@sync_to_async
def _update_project_and_serialize(project_id: int, user_id: int, form: dict):
    with transaction.atomic():
        p = (
            Project.objects
            .select_for_update()
            .filter(id=project_id, user_id=user_id)
            .first()
        )
        if not p:
            return None
        if p.status != Project.Status.PENDING:
            return {"error": _EDIT_LOCKED_MSG}

        update_fields: list[str] = []

        if "type" in form:
            new_type = form.get("type")
            if new_type not in Project.Type.values:
                return {"error": f"نوع پروژه نامعتبر است: {new_type}"}
            p.type = new_type
            update_fields.append("type")

        if "title" in form:
            new_title = (form.get("title") or "").strip()
            if not new_title:
                return {"error": "عنوان پروژه نمی‌تواند خالی باشد"}
            p.title = new_title
            update_fields.append("title")

        if "address" in form:
            p.address = form.get("address")
            update_fields.append("address")

        if "owner_mobile" in form:
            mobile = (form.get("owner_mobile") or "").strip() or None
            if mobile and not re.match(r"^09\d{9}$", mobile):
                return {"error": "فرمت موبایل مالک نامعتبر است"}
            p.owner_mobile = mobile
            update_fields.append("owner_mobile")

        numeric_fields = {
            "unit_count": "تعداد واحد",
            "number_water_taps": "تعداد شیرآبی",
            "number_gas_taps": "تعداد شیرگازی",
            "number_connections": "تعداد اتصالات",
            "pipe_length": "متراژ لوله",
        }
        for field, label in numeric_fields.items():
            if field not in form:
                continue
            raw = form.get(field)
            if raw is None or raw == "":
                setattr(p, field, None)
            else:
                try:
                    n = int(raw)
                except (ValueError, TypeError):
                    return {"error": f"{label} باید عدد صحیح باشد"}
                if n < 0:
                    return {"error": f"{label} نمی‌تواند منفی باشد"}
                setattr(p, field, n)
            update_fields.append(field)

        if "completion_at" in form:
            p.completion_at = _to_datetime(form.get("completion_at"))
            update_fields.append("completion_at")

        if update_fields:
            p.save(update_fields=update_fields)

        p = (
            Project.objects
            .select_related("user")
            .prefetch_related("colleagues__user", "attachments")
            .get(pk=p.pk)
        )
        return {"data": _serialize_project(p, full=True)}


# ═══════════════════════════════════════════════════════════
# ۷. حذف پروژه — فقط PENDING / REJECTED (جدید)
# ═══════════════════════════════════════════════════════════
@router.delete("/{project_id}/")
async def delete_project_endpoint(
    project_id: int,
    user: User = Depends(get_current_user),
):
    try:
        await sync_to_async(delete_project)(project_id, user)
        return success_response("پروژه با موفقیت حذف شد", {})
    except ProjectError as e:
        return error_response(str(e), status_code=400)
    except Exception:
        logger.exception("delete_project failed")
        return error_response("خطا در حذف پروژه")


# ═══════════════════════════════════════════════════════════
# ۳. مدیریت همکاران — فقط PENDING
# ═══════════════════════════════════════════════════════════
@router.post("/{project_id}/colleagues/")
async def add_colleague(
    project_id: int,
    form: dict = Depends(DependencyDataRequest),
    user: User = Depends(get_current_user),
):
    mobile = form.get("mobile")
    percent = form.get("percent")

    if not mobile or not re.match(r"^09\d{9}$", mobile):
        return error_response("شماره موبایل نامعتبر است")

    try:
        percent = int(percent)
        if not (1 <= percent <= 100):
            raise ValueError
    except (ValueError, TypeError):
        return error_response("درصد باید بین ۱ تا ۱۰۰ باشد")

    result = await _add_colleague_db(project_id, user.id, mobile, percent)
    if result.get("error"):
        return error_response(result["error"])
    return success_response("همکار با موفقیت اضافه شد", result["data"])


@sync_to_async
def _add_colleague_db(project_id, owner_id, mobile, percent):
    with transaction.atomic():
        project = (
            Project.objects
            .select_for_update()
            .filter(id=project_id, user_id=owner_id)
            .first()
        )
        if not project:
            return {"error": "پروژه یافت نشد"}
        if project.status != Project.Status.PENDING:
            return {"error": _EDIT_LOCKED_MSG}

        colleague_user = User.objects.filter(mobile=mobile, is_active=True).first()
        if not colleague_user:
            return {"error": "این شماره عضو باشگاه نیست و امکان اضافه شدن ندارد"}
        if colleague_user.id == owner_id:
            return {"error": "شما نمی‌توانید خودتان را به عنوان همکار اضافه کنید"}

        if Colleague.objects.filter(project=project, user=colleague_user).exists():
            return {"error": "این کاربر قبلاً به عنوان همکار اضافه شده است"}

        current_total = (
            project.colleagues.filter(is_active=True)
            .aggregate(t=Sum("percent"))["t"] or 0
        )
        if current_total + percent > 100:
            return {
                "error": f"مجموع درصدها ({current_total + percent}%) از ۱۰۰ بیشتر می‌شود"
            }

        c = Colleague.objects.create(
            project=project, user=colleague_user, percent=percent, is_active=True,
        )
        # ✅ serialize داخل sync thread با user موجود
        return {"data": {
            "id": c.id,
            "user_uuid": str(colleague_user.uuid),
            "user_mobile": colleague_user.mobile,
            "user_name": colleague_user.full_name,
            "percent": c.percent,
            "is_active": c.is_active,
        }}


@router.post("/{project_id}/colleagues/{colleague_id}/toggle/")
async def toggle_colleague(
    project_id: int,
    colleague_id: int,
    user: User = Depends(get_current_user),
):
    result = await _toggle_colleague_db(project_id, colleague_id, user.id)
    if result.get("error"):
        return error_response(result["error"])
    return success_response("وضعیت همکار تغییر کرد", result["data"])


@sync_to_async
def _toggle_colleague_db(project_id, colleague_id, owner_id):
    with transaction.atomic():
        project = (
            Project.objects
            .select_for_update()
            .filter(id=project_id, user_id=owner_id)
            .first()
        )
        if not project:
            return {"error": "پروژه یافت نشد"}
        if project.status != Project.Status.PENDING:
            return {"error": _EDIT_LOCKED_MSG}

        c = (
            Colleague.objects
            .select_related("user")
            .filter(id=colleague_id, project=project)
            .first()
        )
        if not c:
            return {"error": "همکار یافت نشد"}

        if not c.is_active:
            current_total = (
                project.colleagues.filter(is_active=True)
                .aggregate(t=Sum("percent"))["t"] or 0
            )
            if current_total + c.percent > 100:
                return {"error": "با فعال‌سازی این همکار، مجموع درصدها از ۱۰۰ بیشتر می‌شود"}

        c.is_active = not c.is_active
        c.save(update_fields=["is_active"])
        return {"data": _serialize_colleague(c)}


@router.delete("/{project_id}/colleagues/{colleague_id}/")
async def delete_colleague(
    project_id: int,
    colleague_id: int,
    user: User = Depends(get_current_user),
):
    result = await _delete_colleague_db(project_id, colleague_id, user.id)
    if result.get("error"):
        return error_response(result["error"])
    return success_response("همکار با موفقیت حذف شد", {})


@sync_to_async
def _delete_colleague_db(project_id, colleague_id, owner_id):
    with transaction.atomic():
        project = (
            Project.objects
            .select_for_update()
            .filter(id=project_id, user_id=owner_id)
            .first()
        )
        if not project:
            return {"error": "پروژه یافت نشد"}
        if project.status != Project.Status.PENDING:
            return {"error": _EDIT_LOCKED_MSG}

        c = Colleague.objects.filter(id=colleague_id, project=project).first()
        if not c:
            return {"error": "همکار یافت نشد"}

        c.delete()
        return {"success": True}


# ═══════════════════════════════════════════════════════════
# ۴. لیست و جزئیات پروژه (فقط خواندن)
# ═══════════════════════════════════════════════════════════
@router.get("/list/")
async def list_my_projects(user: User = Depends(get_current_user)):
    data = await _list_my_projects(user.id)
    return success_response("پروژه‌های من", data)


@sync_to_async
def _list_my_projects(user_id):
    qs = (
        Project.objects
        .select_related("user")
        .prefetch_related("colleagues__user", "attachments")
        .filter(user_id=user_id)
        .order_by("-created_at")
    )
    return [_serialize_project(p, full=True) for p in qs]


@router.get("/{project_id}/")
async def get_project(project_id: int, user: User = Depends(get_current_user)):
    data = await _get_project(project_id, user.id)
    if not data:
        return error_response("پروژه یافت نشد", status_code=404)
    return success_response("جزئیات پروژه", data)


@sync_to_async
def _get_project(project_id, user_id):
    p = (
        Project.objects
        .select_related("user")
        .prefetch_related("colleagues__user", "attachments")
        .filter(id=project_id, user_id=user_id)
        .first()
    )
    return _serialize_project(p, full=True) if p else None


# ═══════════════════════════════════════════════════════════
# ۵. آپلود تصاویر — فقط PENDING
# ═══════════════════════════════════════════════════════════
@router.post("/{project_id}/attachments/")
async def upload_attachment(
    project_id: int,
    type: str,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    if type not in Attachment.FileType.values:
        return error_response("نوع فایل نامعتبر است", status_code=400)

    try:
        saved_name = handle_save_file(file)
    except Exception:
        logger.exception("file save failed")
        return error_response("خطا در ذخیره فایل")

    try:
        attachment = await sync_to_async(add_attachment)(
            project_id, user,
            file_type=type,
            saved_file_name=saved_name,
            file_size=file.size or 0,
            mime_type=file.content_type or "",
        )
        return success_response("فایل آپلود شد", _serialize_attachment(attachment))
    except ProjectError as e:
        return error_response(str(e), status_code=400)
    except Exception:
        logger.exception("add_attachment failed")
        return error_response("خطا در ثبت پیوست")



# ─────────────────────────────────────────────────────────────
# روت آپلود دسته‌ای — همه‌ی تصاویر با یک درخواست
# ─────────────────────────────────────────────────────────────
@router.post("/{project_id}/attachments/batch/")
async def upload_attachments_batch(
    project_id: int,
    exterior_view_building: Optional[UploadFile] = File(None),
    azar_products_installed: Optional[UploadFile] = File(None),
    azar_products_depot: Optional[UploadFile] = File(None),
    Invoice: Optional[UploadFile] = File(None),
    user: User = Depends(get_current_user),
):
    """
    آپلود یکجای همه‌ی تصاویر پروژه — فقط PENDING.
    فایل‌ها روی دیسک ذخیره می‌شوند و در صورت خطا rollback می‌شود.
    """
    files_map = {
        "exterior_view_building": exterior_view_building,
        "azar_products_installed": azar_products_installed,
        "azar_products_depot": azar_products_depot,
        "Invoice": Invoice,
    }

    # ۱. ابتدا فقط اعتبارسنجی اولیه (بدون ذخیره)
    if not any(f is not None for f in files_map.values()):
        return error_response("هیچ فایلی ارسال نشده است", status_code=400)

    # ۲. فایل‌ها را روی دیسک ذخیره می‌کنیم (این کار async است و از کتابخانه‌ی
    #    fileManager شما استفاده می‌کند، پس در main thread انجام می‌شود)
    saved_names: dict[str, str] = {}
    file_sizes: dict[str, int] = {}
    file_mimes: dict[str, str] = {}

    try:
        for field, upload in files_map.items():
            if upload is None:
                continue
            saved_name = handle_save_file(upload)  # همگام، از fileManager
            saved_names[field] = saved_name
            file_sizes[field] = upload.size or 0
            file_mimes[field] = upload.content_type or ""
    except Exception:
        logger.exception("batch upload: file save failed")
        return error_response("خطا در ذخیره فایل‌ها")

    # ۳. ثبت در دیتابیس — sync، پس در sync_to_async اجرا می‌شود
    try:
        result = await sync_to_async(_batch_upload_db)(
            project_id,
            user.id,
            saved_names,
            file_sizes,
            file_mimes,
        )
        return success_response("تصاویر با موفقیت ثبت شدند", result)
    except ProjectError as e:
        return error_response(str(e), status_code=400)
    except Exception:
        logger.exception("batch upload failed")
        return error_response("خطا در ثبت تصاویر")


# ─────────────────────────────────────────────────────────────
# تابع sync که داخل sync_to_async اجرا می‌شود
# ─────────────────────────────────────────────────────────────
def _batch_upload_db(
    project_id: int,
    user_id: int,
    saved_names: dict[str, str],
    file_sizes: dict[str, int],
    file_mimes: dict[str, str],
):
    """
    ثبت اتمیک پیوست‌ها در دیتابیس.
    ورودی همه از قبل روی دیسک ذخیره شده‌اند.
    """
    with transaction.atomic():
        project = (
            Project.objects
            .select_for_update()
            .filter(id=project_id, user_id=user_id)
            .first()
        )
        if not project:
            raise ProjectError("پروژه یافت نشد")
        if project.status != Project.Status.PENDING:
            raise ProjectError(_EDIT_LOCKED_MSG)

        saved: list[dict] = []
        for field, saved_name in saved_names.items():
            # جایگزینی: اگر فایلی از این نوع وجود دارد، حذف شود
            Attachment.objects.filter(project=project, type=field).delete()

            # ثبت پیوست جدید
            attachment = add_attachment(
                project_id,
                # user را از id می‌سازیم چون در sync context هستیم
                project.user,
                file_type=field,
                saved_file_name=saved_name,
                file_size=file_sizes.get(field, 0),
                mime_type=file_mimes.get(field, ""),
            )
            saved.append(_serialize_attachment(attachment))

        return {"attachments": saved}
    
    
# ═══════════════════════════════════════════════════════════
# ۶. حذف تصویر — فقط PENDING (جدید)
# ═══════════════════════════════════════════════════════════
@router.delete("/{project_id}/attachments/{attachment_id}/")
async def delete_attachment_endpoint(
    project_id: int,
    attachment_id: int,
    user: User = Depends(get_current_user),
):
    try:
        await sync_to_async(delete_attachment)(
            project_id, user,
            attachment_id=attachment_id,
        )
        return success_response("پیوست حذف شد", {})
    except ProjectError as e:
        return error_response(str(e), status_code=400)
    except Exception:
        logger.exception("delete_attachment failed")
        return error_response("خطا در حذف پیوست")


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