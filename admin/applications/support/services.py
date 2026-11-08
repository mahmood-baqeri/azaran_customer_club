# applications/support/services.py

import logging
from typing import Optional

from django.db import transaction
from django.utils import timezone

from applications.support.models import Support, SupportMessage
from applications.user.models import User

logger = logging.getLogger(__name__)


class SupportError(Exception):
    """خطای منطقی پشتیبانی (پیام فارسی برای کاربر)."""


# ═══════════════════════════════════════════════════════════
# ۱. ایجاد تیکت (کاربر) + پیام اولیه
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def create_ticket(
    user: User,
    *,
    category: str,
    subject: str,
    text: str,
    file_name: Optional[str] = None,
    priority: str = Support.Priority.NORMAL,
) -> Support:
    """
    ساخت تیکت پشتیبانی جدید به همراه اولین پیام کاربر.
    """
    if category not in Support.Category.values:
        raise SupportError(f"دسته‌بندی نامعتبر است: {category}")

    if not subject or not subject.strip():
        raise SupportError("موضوع تیکت الزامی است")

    if not text or not text.strip():
        if not file_name:
            raise SupportError("متن پیام یا فایل الزامی است")

    if priority not in Support.Priority.values:
        raise SupportError("اولویت نامعتبر است")

    # ۱. ساخت بدنه تیکت
    ticket = Support.objects.create(
        user=user,
        category=category,
        subject=subject.strip(),
        priority=priority,
        status=Support.Status.OPEN,
    )

    # ۲. ساخت اولین پیام (چت)
    SupportMessage.objects.create(
        ticket=ticket,
        sender=user,
        text=text.strip() if text else "",
        file=file_name,
        is_admin_reply=False,
    )

    logger.info("Support ticket #%s created by user=%s", ticket.id, user.id)
    return ticket


# ═══════════════════════════════════════════════════════════
# ۲. ارسال پیام جدید توسط کاربر
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def send_user_message(
    ticket_id: int,
    user_id: int,
    *,
    text: str,
    file_name: Optional[str] = None,
) -> SupportMessage:
    """ارسال پیام جدید توسط کاربر در یک تیکت باز"""
    if not text or not text.strip():
        if not file_name:
            raise SupportError("متن پیام یا فایل الزامی است")

    ticket = (
        Support.objects
        .select_for_update()
        .filter(id=ticket_id, user_id=user_id)
        .first()
    )
    if not ticket:
        raise SupportError("تیکت یافت نشد")
    if ticket.status == Support.Status.CLOSED:
        raise SupportError("این تیکت بسته شده است و امکان ارسال پیام وجود ندارد")

    # ساخت پیام
    msg = SupportMessage.objects.create(
        ticket=ticket,
        sender_id=user_id,
        text=text.strip() if text else "",
        file=file_name,
        is_admin_reply=False,
    )

    # اگر تیکت در وضعیت حل شده بود، با ارسال پیام جدید مجدداً باز می‌شود
    if ticket.status == Support.Status.RESOLVED:
        ticket.status = Support.Status.OPEN
        ticket.save(update_fields=["status"])

    logger.info("Support ticket #%s new message from user=%s", ticket.id, user_id)
    return msg


# ═══════════════════════════════════════════════════════════
# ۳. پاسخ ادمین
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def reply_ticket(
    ticket_id: int,
    admin: User,
    *,
    reply_text: str,
    file_name: Optional[str] = None,
    new_status: Optional[str] = None,
) -> Support:
    if not reply_text or not reply_text.strip():
        if not file_name:
            raise SupportError("متن پاسخ یا فایل الزامی است")

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

    # ۱. ثبت پاسخ به عنوان یک پیام جدید در چت
    SupportMessage.objects.create(
        ticket=ticket,
        sender=admin,
        text=reply_text.strip() if reply_text else "",
        file=file_name,
        is_admin_reply=True,
    )

    # ۲. آپدیت وضعیت تیکت
    ticket.status = new_status or Support.Status.IN_PROGRESS
    ticket.save(update_fields=["status"])
    
    logger.info("Support ticket #%s replied by admin=%s", ticket.id, admin.id)
    return ticket


# ═══════════════════════════════════════════════════════════
# ۴. تغییر وضعیت (ادمین)
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
# ۵. بستن توسط کاربر
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