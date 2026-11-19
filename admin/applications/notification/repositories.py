# Path: applications/notification/repositories.py

# applications/notification/repositories.py

import logging

from django.db import transaction

from applications.user.models import User

from .models import Notification, NotificationState, NotificationTarget

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# NOTIFICATION — Store (create / update)
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def notification__store(request, cleaned, item=None):
    """ذخیره/به‌روزرسانی نوتیفیکیشن + همگام‌سازی گیرندگان."""
    if not cleaned:
        raise ValueError("cleaned data required")

    fields = {
        "title":             cleaned["title"],
        "body":              cleaned["body"],
        "target_type":       cleaned["target_type"],
        "notification_type": cleaned["notification_type"],
        "priority":          cleaned["priority"],
        "action_type":       cleaned["action_type"] or "",
        "action_url":        cleaned["action_url"] or "",
        "scheduled_at":      cleaned["scheduled_at"],
        "expires_at":        cleaned["expires_at"],
    }

    if item is None:
        item = Notification(**fields, status=Notification.Status.DRAFT)
    else:
        for k, v in fields.items():
            setattr(item, k, v)

    # اگر scheduled_at دارد و هنوز draft است → scheduled
    if cleaned["scheduled_at"] and item.status == Notification.Status.DRAFT:
        item.status = Notification.Status.SCHEDULED

    new_image = request.FILES.get("image")
    if new_image:
        item.image = new_image
        item.image_size = new_image.size
        item.image_type = getattr(new_image, "content_type", "") or ""

    item.save()

    _sync_targets(item, cleaned["target_type"], cleaned["target_user_ids"])

    return item


def _sync_targets(notification, target_type, user_ids):
    """همگام‌سازی NotificationTarget بر اساس target_type."""
    if target_type == Notification.TargetType.ALL:
        notification.targets.all().delete()
        return

    desired = set(user_ids or [])
    existing = set(notification.targets.values_list("user_id", flat=True))

    to_delete = existing - desired
    if to_delete:
        notification.targets.filter(user_id__in=to_delete).delete()

    to_add = desired - existing
    if to_add:
        NotificationTarget.objects.bulk_create(
            [NotificationTarget(notification=notification, user_id=uid) for uid in to_add],
            ignore_conflicts=True,
            batch_size=500,
        )


# ═══════════════════════════════════════════════════════════
# NOTIFICATION — Send / Cancel / Delete
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def notification__send(notification):
    """ارسال دستی یک نوتیفیکیشن draft/scheduled."""
    if notification.status == Notification.Status.SENT:
        raise ValueError("این نوتیفیکیشن قبلاً ارسال شده است")
    if notification.status not in (
        Notification.Status.DRAFT,
        Notification.Status.SCHEDULED,
    ):
        raise ValueError(
            f"وضعیت فعلی ({notification.get_status_display()}) اجازه ارسال نمی‌دهد"
        )

    if notification.target_type == Notification.TargetType.ALL:
        total = User.objects.filter(is_active=True).count()
    else:
        total = notification.targets.count()
        if total == 0:
            raise ValueError("گیرنده‌ای انتخاب نشده است")

    notification.mark_as_sent(total_recipients=total)
    return notification


@transaction.atomic
def notification__cancel(notification):
    """لغو یک نوتیفیکیشن ارسال‌نشده."""
    if notification.status == Notification.Status.SENT:
        raise ValueError("نمی‌توان نوتیفیکیشن ارسال‌شده را لغو کرد")
    if notification.status == Notification.Status.CANCELLED:
        return notification

    notification.status = Notification.Status.CANCELLED
    notification.save(update_fields=["status", "updated_at"])
    return notification


def notification__delete(notification):
    """حذف — فقط برای ارسال‌نشده‌ها."""
    if notification.status == Notification.Status.SENT:
        raise ValueError("نمی‌توان نوتیفیکیشن ارسال‌شده را حذف کرد")
    notification.delete()