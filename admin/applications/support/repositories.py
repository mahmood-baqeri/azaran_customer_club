# Path: applications/support/repositories.py

# applications/support/repositories.py

import logging

from django.db import transaction
from django.utils import timezone

from .models import Support, SupportMessage

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Workflow constants
# ═══════════════════════════════════════════════════════════
VALID_TRANSITIONS = {
    Support.Status.OPEN: {
        Support.Status.IN_PROGRESS,
        Support.Status.RESOLVED,
        Support.Status.CLOSED,
    },
    Support.Status.IN_PROGRESS: {
        Support.Status.RESOLVED,
        Support.Status.CLOSED,
    },
    Support.Status.RESOLVED: {
        Support.Status.IN_PROGRESS,
        Support.Status.CLOSED,
    },
    Support.Status.CLOSED: set(),  # final
}


def support__available_transitions(support):
    """لیست گذارهای مجاز — برای رندر در قالب."""
    return [
        {"value": s, "label": dict(Support.Status.choices)[s]}
        for s in VALID_TRANSITIONS.get(support.status, set())
        if s != Support.Status.CLOSED  # بستن با دکمه‌ی جدا انجام می‌شود
    ]


def _is_valid_transition(current, new):
    return new in VALID_TRANSITIONS.get(current, set())


# ═══════════════════════════════════════════════════════════
# SUPPORT — Store (create / update)
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def support__store(cleaned, item=None):
    """ایجاد/به‌روزرسانی تیکت. اگر item=None → پیام اول هم ساخته می‌شود."""
    if not cleaned:
        raise ValueError("cleaned data required")

    is_new = item is None

    if is_new:
        item = Support(
            user=cleaned["user"],
            category=cleaned["category"],
            priority=cleaned["priority"],
            subject=cleaned["subject"],
            status=Support.Status.OPEN,
        )
    else:
        if item.status == Support.Status.CLOSED:
            raise ValueError("تیکت بسته‌شده قابل ویرایش نیست")
        item.category = cleaned["category"]
        item.priority = cleaned["priority"]
        item.subject = cleaned["subject"]

    item.save()

    # ─── پیام اول (فقط در ایجاد) ────────────────────────
    if is_new:
        message = SupportMessage.objects.create(
            ticket=item,
            sender=cleaned["user"],
            text=cleaned["first_message_text"],
            file=cleaned.get("first_message_file"),
            is_admin_reply=False,
        )
        # زمان پیام در مدل خودکار تنظیم می‌شود

    return item


# ═══════════════════════════════════════════════════════════
# SUPPORT — Delete
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def support__delete(support_id):
    item = Support.objects.select_for_update().filter(id=support_id).first()
    if not item:
        raise ValueError("تیکت یافت نشد")
    if item.status == Support.Status.CLOSED:
        raise ValueError("تیکت بسته‌شده قابل حذف نیست — ابتدا باز کنید")
    item.delete()


# ═══════════════════════════════════════════════════════════
# SUPPORT — Change status (بدون CLOSED)
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def support__change_status(support_id, new_status):
    item = Support.objects.select_for_update().filter(id=support_id).first()
    if not item:
        raise ValueError("تیکت یافت نشد")

    if new_status == Support.Status.CLOSED:
        raise ValueError("برای بستن تیکت از دکمه‌ی «بستن تیکت» استفاده کنید")

    if not _is_valid_transition(item.status, new_status):
        raise ValueError(
            f"تغییر وضعیت از «{item.get_status_display()}» به "
            f"«{dict(Support.Status.choices)[new_status]}» مجاز نیست"
        )

    item.status = new_status
    item.save(update_fields=["status", "updated_at"])
    return item


# ═══════════════════════════════════════════════════════════
# SUPPORT — Close
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def support__close(support_id, closed_by, reason=None):
    item = Support.objects.select_for_update().filter(id=support_id).first()
    if not item:
        raise ValueError("تیکت یافت نشد")

    if item.status == Support.Status.CLOSED:
        raise ValueError("تیکت از قبل بسته شده است")

    if not _is_valid_transition(item.status, Support.Status.CLOSED):
        raise ValueError("این تیکت قابل بستن نیست")

    item.status = Support.Status.CLOSED
    item.closed_by = closed_by
    item.closed_at = timezone.now()
    item.close_reason = reason or None
    item.save(update_fields=["status", "closed_by", "closed_at", "close_reason", "updated_at"])
    return item


# ═══════════════════════════════════════════════════════════
# SUPPORT — Send message (پاسخ ادمین)
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def support__send_admin_message(support_id, sender, text, upload=None):
    ticket = Support.objects.select_for_update().filter(id=support_id).first()
    if not ticket:
        raise ValueError("تیکت یافت نشد")

    if ticket.status == Support.Status.CLOSED:
        raise ValueError("تیکت بسته‌شده — ابتدا باز کنید")

    # ساخت پیام — خود مدل زمان `last_message_at` و انتقال به IN_PROGRESS را مدیریت می‌کند
    message = SupportMessage.objects.create(
        ticket=ticket,
        sender=sender,
        text=text,
        file=upload,
        is_admin_reply=True,
    )
    return message


# ═══════════════════════════════════════════════════════════
# SUPPORT — Mark user messages as read
# ═══════════════════════════════════════════════════════════
def support__mark_user_messages_as_read(support_id):
    """
    وقتی ادمین تیکت را باز می‌کند، تمام پیام‌های کاربر که تا الان
    خوانده نشده‌اند را `is_read=True` می‌کند.
    """
    count = SupportMessage.objects.filter(
        ticket_id=support_id,
        is_admin_reply=False,
        is_read=False,
    ).update(is_read=True)
    return count