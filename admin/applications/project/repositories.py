# applications/project/repositories.py

import logging
import re

from django.db import transaction
from django.db.models import Sum

from applications.user.models import User

from .models import Attachment, Colleague, Project
from .services import (
    ProjectError,
    add_attachment,
    approve_project,
    create_project,
    delete_project,
    reject_project,
)

logger = logging.getLogger(__name__)

_MOBILE_RE = re.compile(r"^09\d{9}$")


# ═══════════════════════════════════════════════════════════
# PROJECT — Store
# ═══════════════════════════════════════════════════════════
def project__store(cleaned, user, item=None):
    """Create از services، Update مستقیم (فقط فیلدهای editable)."""
    if item is None:
        return create_project(
            user=user,
            type=cleaned["type"],
            title=cleaned["title"],
            address=cleaned.get("address"),
            owner_mobile=cleaned.get("owner_mobile"),
            unit_count=cleaned.get("unit_count"),
            number_water_taps=cleaned.get("number_water_taps"),
            number_gas_taps=cleaned.get("number_gas_taps"),
            number_connections=cleaned.get("number_connections"),
            pipe_length=cleaned.get("pipe_length"),
            completion_at=cleaned.get("completion_at"),
            colleagues=None,  # از detail اضافه می‌شوند
        )

    if item.status != Project.Status.PENDING:
        raise ProjectError("فقط پروژه‌های در انتظار قابل ویرایش هستند")

    item.type = cleaned["type"]
    item.title = cleaned["title"]
    item.address = cleaned.get("address")
    item.owner_mobile = cleaned.get("owner_mobile")
    item.unit_count = cleaned.get("unit_count")
    item.number_water_taps = cleaned.get("number_water_taps")
    item.number_gas_taps = cleaned.get("number_gas_taps")
    item.number_connections = cleaned.get("number_connections")
    item.pipe_length = cleaned.get("pipe_length")
    item.completion_at = cleaned.get("completion_at")
    item.save()
    return item


# ═══════════════════════════════════════════════════════════
# PROJECT — Admin actions
# ═══════════════════════════════════════════════════════════
def project__approve(project_id, admin):
    return approve_project(project_id, admin)


def project__reject(project_id, admin, reason):
    return reject_project(project_id, admin, reason=reason)


def project__delete(project_id, user=None, as_admin=False):
    if as_admin:
        project = Project.objects.filter(id=project_id).first()
        if not project:
            raise ProjectError("پروژه یافت نشد")
        if project.status == Project.Status.APPROVED:
            raise ProjectError("پروژه‌های تأیید شده قابل حذف نیستند")
        project.delete()
        return
    return delete_project(project_id, user)


# ═══════════════════════════════════════════════════════════
# COLLEAGUE — Add / Remove
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def project__add_colleague(project_id, mobile, percent, as_admin=False):
    project = (
        Project.objects.select_for_update()
        .select_related("user")
        .filter(id=project_id).first()
    )
    if not project:
        raise ProjectError("پروژه یافت نشد")
    if project.status != Project.Status.PENDING:
        raise ProjectError("فقط پروژه‌های در انتظار قابل ویرایش هستند")

    mobile = (mobile or "").strip()
    if not _MOBILE_RE.match(mobile):
        raise ProjectError("شماره موبایل همکار معتبر نیست")
    if not (1 <= int(percent) <= 100):
        raise ProjectError("درصد باید بین ۱ تا ۱۰۰ باشد")

    if project.user.mobile == mobile:
        raise ProjectError("صاحب پروژه نمی‌تواند همکار خودش باشد")

    user = User.objects.filter(mobile=mobile, is_active=True).first()
    if not user:
        raise ProjectError(f"کاربر با موبایل {mobile} در باشگاه ثبت‌نام نکرده یا غیرفعال است")

    if Colleague.objects.filter(project=project, user=user).exists():
        raise ProjectError("این کاربر قبلاً به‌عنوان همکار ثبت شده است")

    total = project.colleagues.aggregate(t=Sum("percent"))["t"] or 0
    if total + int(percent) > 100:
        raise ProjectError(
            f"مجموع درصد بیش از ۱۰۰ می‌شود (فعلی: {total}% + جدید: {percent}%)"
        )

    return Colleague.objects.create(project=project, user=user, percent=int(percent))


@transaction.atomic
def project__remove_colleague(project_id, colleague_id, as_admin=False):
    project = Project.objects.select_for_update().filter(id=project_id).first()
    if not project:
        raise ProjectError("پروژه یافت نشد")
    if project.status != Project.Status.PENDING:
        raise ProjectError("فقط پروژه‌های در انتظار قابل ویرایش هستند")

    colleague = Colleague.objects.filter(id=colleague_id, project=project).first()
    if not colleague:
        raise ProjectError("همکار یافت نشد")
    colleague.delete()


# ═══════════════════════════════════════════════════════════
# ATTACHMENT — Upload / Delete
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def project__upload_attachment(
    project_id, user, *,
    file_type, upload, file_size=0, mime_type="", as_admin=False,
):
    query = Project.objects.select_for_update()
    if not as_admin:
        query = query.filter(user=user)
    project = query.filter(id=project_id).first()
    if not project:
        raise ProjectError("پروژه یافت نشد")
    if project.status != Project.Status.PENDING:
        raise ProjectError("فقط پروژه‌های در انتظار قابل ویرایش هستند")
    if file_type not in Attachment.FileType.values:
        raise ProjectError("نوع فایل نامعتبر است")

    attachment, _ = Attachment.objects.update_or_create(
        project=project,
        type=file_type,
        defaults={
            "file": upload,
            "file_size": file_size,
            "file_type": mime_type,
        },
    )
    return attachment


@transaction.atomic
def project__remove_attachment(project_id, attachment_id, user=None, as_admin=False):
    query = Project.objects.select_for_update()
    if not as_admin:
        query = query.filter(user=user)
    project = query.filter(id=project_id).first()
    if not project:
        raise ProjectError("پروژه یافت نشد")
    if project.status != Project.Status.PENDING:
        raise ProjectError("فقط پروژه‌های در انتظار قابل ویرایش هستند")

    attachment = Attachment.objects.filter(id=attachment_id, project=project).first()
    if not attachment:
        raise ProjectError("پیوست یافت نشد")
    attachment.delete()