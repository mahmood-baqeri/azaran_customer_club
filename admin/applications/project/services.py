# applications/project/services.py

import logging
import re
from datetime import datetime
from typing import Optional

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from applications.project.models import Attachment, Colleague, Project
from applications.score import api as score_api
from applications.score.models import UserScoreLog
from applications.user.models import User

logger = logging.getLogger(__name__)

# پیام یکدست برای همه‌ی عملیات تغییر روی پروژه‌ی غیر PENDING
_EDIT_LOCKED_MSG = "این عملیات فقط تا قبل از تأیید پروژه امکان‌پذیر است"


class ProjectError(Exception):
    """خطای منطقی پروژه (پیام فارسی برای کاربر)."""


# ═══════════════════════════════════════════════════════════
# ایجاد پروژه
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def create_project(
    user: User,
    *,
    type: str,
    title: str,
    address: Optional[str] = None,
    owner_mobile: Optional[str] = None,
    unit_count: Optional[int] = None,
    number_water_taps: Optional[int] = None,
    number_gas_taps: Optional[int] = None,
    number_connections: Optional[int] = None,
    pipe_length: Optional[int] = None,
    completion_at: Optional[datetime] = None,
    colleagues: Optional[list[dict]] = None,
) -> Project:
    if type not in Project.Type.values:
        raise ProjectError(f"نوع پروژه نامعتبر است: {type}")

    if not title or not title.strip():
        raise ProjectError("عنوان پروژه الزامی است")

    if owner_mobile:
        owner_mobile = str(owner_mobile).strip()
        if not re.match(r"^09\d{9}$", owner_mobile):
            raise ProjectError("فرمت موبایل مالک نامعتبر است")

    for label, val in (
        ("تعداد واحد", unit_count),
        ("تعداد شیرآبی", number_water_taps),
        ("تعداد شیرگازی", number_gas_taps),
        ("تعداد اتصالات", number_connections),
        ("متراژ لوله", pipe_length),
    ):
        if val is not None and val < 0:
            raise ProjectError(f"{label} نمی‌تواند منفی باشد")

    colleague_pairs: list[tuple[User, int]] = []
    if colleagues:
        total_percent = 0
        seen_user_ids: set[int] = set()

        for c in colleagues:
            mobile = (c.get("user_mobile") or "").strip()
            percent = int(c.get("percent", 0))

            if not mobile:
                raise ProjectError("شماره موبایل همکار الزامی است")
            if not (1 <= percent <= 100):
                raise ProjectError(
                    f"درصد هر همکار باید بین ۱ تا ۱۰۰ باشد (دریافت‌شده: {percent})"
                )

            colleague_user = User.objects.filter(mobile=mobile, is_active=True).first()
            if not colleague_user:
                raise ProjectError(
                    f"کاربر با موبایل {mobile} در باشگاه ثبت‌نام نکرده یا غیرفعال است"
                )
            if colleague_user.id == user.id:
                raise ProjectError("صاحب پروژه نمی‌تواند به‌عنوان همکار اضافه شود")
            if colleague_user.id in seen_user_ids:
                raise ProjectError(
                    f"همکار با موبایل {mobile} به‌صورت تکراری وارد شده است"
                )
            seen_user_ids.add(colleague_user.id)

            total_percent += percent
            if total_percent > 100:
                raise ProjectError(
                    f"مجموع درصد مشارکت ({total_percent}%) از ۱۰۰٪ بیشتر است"
                )
            colleague_pairs.append((colleague_user, percent))

    project = Project.objects.create(
        user=user,
        type=type,
        title=title.strip(),
        address=address,
        owner_mobile=owner_mobile,
        unit_count=unit_count,
        number_water_taps=number_water_taps,
        number_gas_taps=number_gas_taps,
        number_connections=number_connections,
        pipe_length=pipe_length,
        completion_at=completion_at,
        status=Project.Status.PENDING,
    )

    Colleague.objects.bulk_create([
        Colleague(project=project, user=cu, percent=pc)
        for cu, pc in colleague_pairs
    ])

    return project


# ═══════════════════════════════════════════════════════════
# حذف پروژه — فقط اگر تأیید نشده باشد
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def delete_project(project_id: int, user: User) -> None:
    """
    حذف کامل پروژه توسط مالک.
    - پروژه‌های APPROVED قابل حذف نیستند (امتیاز تخصیص یافته).
    - PENDING و REJECTED قابل حذف هستند.
    """
    project = (
        Project.objects
        .select_for_update()
        .filter(id=project_id, user=user)
        .first()
    )
    if not project:
        raise ProjectError("پروژه یافت نشد")
    if project.status == Project.Status.APPROVED:
        raise ProjectError("پروژه‌های تأیید شده قابل حذف نیستند")

    project.delete()

# ═══════════════════════════════════════════════════════════
# تأیید پروژه (ادمین) + امتیازدهی
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def approve_project(
    project_id: int,
    admin: User,
    *,
    auto_award: bool = True,
) -> Project:
    project = (
        Project.objects
        .select_for_update()
        .select_related("user")
        .filter(id=project_id)
        .first()
    )
    if not project:
        raise ProjectError("پروژه یافت نشد")
    if project.status == Project.Status.APPROVED:
        raise ProjectError("پروژه قبلاً تأیید شده است")
    if project.status == Project.Status.REJECTED:
        raise ProjectError("پروژه رد شده و قابل تأیید نیست")

    total = project.colleagues.filter(is_active=True).aggregate(
        t=Sum("percent")
    )["t"] or 0
    if total > 100:
        raise ProjectError(
            f"مجموع درصد مشارکت ({total}%) نامعتبر است — تأیید لغو شد"
        )

    project.status = Project.Status.APPROVED
    project.approved_by = admin
    project.approved_at = timezone.now()
    project.save(update_fields=["status", "approved_by", "approved_at"])

    if auto_award:
        _award_project_scores(project)

    return project


def _award_project_scores(project: Project) -> None:
    owner_log = score_api.award(
        project.user,
        UserScoreLog.TransactionCode.PROJECT,
        reference_type="project",
        reference_id=str(project.id),
        reason=f"تأیید پروژه «{project.title or project.id}»",
        extra={"project_id": project.id, "role": "owner"},
        strict=True,
    )

    base_points = owner_log.amount if owner_log else 0
    logger.info(
        "PROJECT award: project=%s user=%s points=%s",
        project.id, project.user_id, base_points,
    )

    if base_points <= 0:
        logger.warning("PROJECT base_points=0 — skipping colleague awards")
        return

    colleagues = project.colleagues.filter(is_active=True).select_related("user")
    for collab in colleagues:
        points = int(base_points * collab.percent / 100)
        if points <= 0:
            logger.info(
                "Colleague user=%s percent=%s → 0 points — skipping",
                collab.user_id, collab.percent,
            )
            continue

        try:
            score_api.award(
                collab.user,
                UserScoreLog.TransactionCode.PROJECT_PARTICIPATION,
                amount_override=points,
                reference_type="project_colleague",
                reference_id=f"{project.id}:{collab.id}",
                reason=f"مشارکت {collab.percent}% در پروژه #{project.id}",
                extra={
                    "percent": collab.percent,
                    "base_points": base_points,
                    "project_owner_id": project.user_id,
                },
                strict=False,
            )
            logger.info(
                "PROJECT_PARTICIPATION: project=%s user=%s percent=%s points=%s",
                project.id, collab.user_id, collab.percent, points,
            )
        except Exception:
            logger.exception(
                "PROJECT_PARTICIPATION failed project=%s colleague=%s",
                project.id, collab.id,
            )


# ═══════════════════════════════════════════════════════════
# رد پروژه (ادمین)
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def reject_project(project_id: int, admin: User, *, reason: str) -> Project:
    project = (
        Project.objects
        .select_for_update()
        .filter(id=project_id)
        .first()
    )
    if not project:
        raise ProjectError("پروژه یافت نشد")
    if project.status != Project.Status.PENDING:
        raise ProjectError("فقط پروژه‌های در انتظار قابل رد هستند")

    project.status = Project.Status.REJECTED
    project.rejection_reason = reason or "بدون دلیل"
    project.rejected_at = timezone.now()
    project.save(update_fields=["status", "rejection_reason", "rejected_at"])
    return project


# ═══════════════════════════════════════════════════════════
# افزودن / حذف پیوست — فقط قبل از تأیید
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def add_attachment(
    project_id: int,
    user: User,
    *,
    file_type: str,
    saved_file_name: str,
    file_size: int = 0,
    mime_type: str = "",
) -> Attachment:
    project = (
        Project.objects
        .select_for_update()
        .filter(id=project_id, user=user)
        .first()
    )
    if not project:
        raise ProjectError("پروژه یافت نشد")
    if project.status != Project.Status.PENDING:
        raise ProjectError(_EDIT_LOCKED_MSG)
    if file_type not in Attachment.FileType.values:
        raise ProjectError("نوع فایل نامعتبر است")

    attachment, _ = Attachment.objects.update_or_create(
        project=project,
        type=file_type,
        defaults={
            "file": saved_file_name,
            "file_size": file_size,
            "file_type": mime_type,
        },
    )
    return attachment


@transaction.atomic
def delete_attachment(
    project_id: int,
    user: User,
    *,
    attachment_id: int,
) -> None:
    project = (
        Project.objects
        .select_for_update()
        .filter(id=project_id, user=user)
        .first()
    )
    if not project:
        raise ProjectError("پروژه یافت نشد")
    if project.status != Project.Status.PENDING:
        raise ProjectError(_EDIT_LOCKED_MSG)

    attachment = Attachment.objects.filter(
        id=attachment_id, project=project,
    ).first()
    if not attachment:
        raise ProjectError("پیوست یافت نشد")

    attachment.delete()
    