# applications/support/services.py

import logging
from typing import Optional

from django.db import transaction
from django.utils import timezone

from applications.support.models import Support
from applications.user.models import User

logger = logging.getLogger(__name__)


class SupportError(Exception):
    """خطای منطقی پشتیبانی (پیام فارسی برای کاربر)."""


# ═══════════════════════════════════════════════════════════
# ایجاد تیکت (کاربر)
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def create_ticket(
    user: User,
    *,
    category: str,
    subject: str,
    text: str,
    file_name: Optional[str] = None,
    reference_type: Optional[str] = None,
    reference_id: Optional[str] = None,
    priority: str = Support.Priority.NORMAL,
) -> Support:
    """
    ساخت تیکت پشتیبانی جدید.

    اعتبارسنجی:
    - category معتبر
    - subject, text الزامی
    - اگه reference_type داده شد، reference_id هم باید باشه
    - اگه reference_id داده شد، reference_type هم باید باشه
    """
    if category not in Support.Category.values:
        raise SupportError(f"دسته‌بندی نامعتبر است: {category}")

    if not subject or not subject.strip():
        raise SupportError("موضوع تیکت الزامی است")

    if not text or not text.strip():
        raise SupportError("متن پیام الزامی است")

    if priority not in Support.Priority.values:
        raise SupportError("اولویت نامعتبر است")

    if (reference_type and not reference_id) or (reference_id and not reference_type):
        raise SupportError("نوع مرجع و شناسه مرجع باید هر دو داده شوند یا هیچ‌کدام")

    ticket = Support.objects.create(
        user=user,
        category=category,
        subject=subject.strip(),
        text=text.strip(),
        file=file_name,
        reference_type=reference_type,
        reference_id=str(reference_id) if reference_id else None,
        priority=priority,
        status=Support.Status.OPEN,
    )
    logger.info("Support ticket #%s created by user=%s", ticket.id, user.id)
    return ticket


# ═══════════════════════════════════════════════════════════
# پاسخ ادمین
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def reply_ticket(
    ticket_id: int,
    admin: User,
    *,
    reply_text: str,
    new_status: Optional[str] = None,
) -> Support:
    if not reply_text or not reply_text.strip():
        raise SupportError("متن پاسخ الزامی است")

    ticket = (
        Support.objects
        .select_for_update()
        .filter(id=ticket_id)
        .first()
    )
    if not ticket:
        raise SupportError("تیکت یافت نشد")
    if ticket.status in (Support.Status.RESOLVED, Support.Status.CLOSED):
        raise SupportError("این تیکت بسته شده و قابل پاسخ نیست")

    if new_status and new_status not in Support.Status.values:
        raise SupportError("وضعیت نامعتبر است")

    ticket.admin_reply = reply_text.strip()
    ticket.replied_by = admin
    ticket.replied_at = timezone.now()
    ticket.status = new_status or Support.Status.IN_PROGRESS
    ticket.save(update_fields=[
        "admin_reply", "replied_by", "replied_at", "status",
    ])
    logger.info("Support ticket #%s replied by admin=%s", ticket.id, admin.id)
    return ticket


# ═══════════════════════════════════════════════════════════
# تغییر وضعیت (ادمین)
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def change_status(
    ticket_id: int,
    admin: User,
    *,
    new_status: str,
    reason: Optional[str] = None,
) -> Support:
    if new_status not in Support.Status.values:
        raise SupportError("وضعیت نامعتبر است")

    ticket = (
        Support.objects
        .select_for_update()
        .filter(id=ticket_id)
        .first()
    )
    if not ticket:
        raise SupportError("تیکت یافت نشد")

    ticket.status = new_status
    if new_status == Support.Status.CLOSED:
        ticket.closed_by = admin
        ticket.closed_at = timezone.now()
        ticket.close_reason = (reason or "").strip() or None
        ticket.save(update_fields=[
            "status", "closed_by", "closed_at", "close_reason",
        ])
    else:
        ticket.save(update_fields=["status"])

    logger.info(
        "Support ticket #%s status → %s by admin=%s",
        ticket.id, new_status, admin.id,
    )
    return ticket


# ═══════════════════════════════════════════════════════════
# بستن توسط کاربر
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def close_by_user(ticket_id: int, user_id: int) -> Support:
    ticket = (
        Support.objects
        .select_for_update()
        .filter(id=ticket_id, user_id=user_id)
        .first()
    )
    if not ticket:
        raise SupportError("تیکت یافت نشد")
    if not ticket.can_user_close():
        raise SupportError("این تیکت در وضعیت فعلی قابل بستن نیست")

    ticket.status = Support.Status.CLOSED
    ticket.closed_by_id = user_id
    ticket.closed_at = timezone.now()
    ticket.close_reason = "بسته‌شده توسط کاربر"
    ticket.save(update_fields=[
        "status", "closed_by", "closed_at", "close_reason",
    ])
    return ticket