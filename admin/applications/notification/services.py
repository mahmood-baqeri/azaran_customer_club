"""
سرویس‌های ماژول نوتیفیکیشن — لایه‌ی منطق اتمی، مستقل از FastAPI.
"""
import logging
from typing import Iterable, Optional

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from applications.notification.models import (
    Notification,
    NotificationState,
    NotificationTarget,
)
from applications.user.models import User

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# ارسال
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def send_to_user(
    user: User,
    title: str,
    body: str,
    *,
    notification_type: str = Notification.NotificationType.SYSTEM,
    priority: str = Notification.Priority.NORMAL,
    image=None,
    action_type: str = "",
    action_url: str = "",
    action_data: Optional[dict] = None,
    created_by: Optional[User] = None,
    expires_at=None,
) -> Notification:
    """ارسال نوتیفیکیشن به یک کاربر"""
    notification = Notification.objects.create(
        title=title,
        body=body,
        image=image,
        target_type=Notification.TargetType.USER,
        notification_type=notification_type,
        priority=priority,
        action_type=action_type,
        action_url=action_url,
        action_data=action_data or {},
        created_by=created_by,
        expires_at=expires_at,
        status=Notification.Status.SENDING,
    )
    NotificationTarget.objects.create(notification=notification, user=user)
    notification.mark_as_sent(total_recipients=1)
    return notification


@transaction.atomic
def send_to_users(
    users: Iterable[User],
    title: str,
    body: str,
    *,
    notification_type: str = Notification.NotificationType.SYSTEM,
    priority: str = Notification.Priority.NORMAL,
    image=None,
    action_type: str = "",
    action_url: str = "",
    action_data: Optional[dict] = None,
    created_by: Optional[User] = None,
    expires_at=None,
) -> Notification:
    """ارسال به چند کاربر مشخص — bulk insert برای عملکرد بالا"""
    user_ids = list({u.id for u in users})  # deduplicate + فقط id
    if not user_ids:
        raise ValueError("لیست کاربران خالی است")

    notification = Notification.objects.create(
        title=title,
        body=body,
        image=image,
        target_type=Notification.TargetType.USERS,
        notification_type=notification_type,
        priority=priority,
        action_type=action_type,
        action_url=action_url,
        action_data=action_data or {},
        created_by=created_by,
        expires_at=expires_at,
        status=Notification.Status.SENDING,
    )
    NotificationTarget.objects.bulk_create(
        [NotificationTarget(notification=notification, user_id=uid) for uid in user_ids],
        ignore_conflicts=True,
        batch_size=500,
    )
    notification.mark_as_sent(total_recipients=len(user_ids))
    return notification


@transaction.atomic
def broadcast(
    title: str,
    body: str,
    *,
    notification_type: str = Notification.NotificationType.SYSTEM,
    priority: str = Notification.Priority.NORMAL,
    image=None,
    action_type: str = "",
    action_url: str = "",
    action_data: Optional[dict] = None,
    created_by: Optional[User] = None,
    expires_at=None,
) -> Notification:
    """ارسال همگانی — صفر رکورد در NotificationTarget"""
    notification = Notification.objects.create(
        title=title,
        body=body,
        image=image,
        target_type=Notification.TargetType.ALL,
        notification_type=notification_type,
        priority=priority,
        action_type=action_type,
        action_url=action_url,
        action_data=action_data or {},
        created_by=created_by,
        expires_at=expires_at,
        status=Notification.Status.SENDING,
    )
    total = User.objects.filter(is_active=True).count()
    notification.mark_as_sent(total_recipients=total)
    return notification


# ═══════════════════════════════════════════════════════════
# خواندن / حذف
# ═══════════════════════════════════════════════════════════
def mark_as_read(user: User, notification: Notification) -> bool:
    """علامت خوانده‌شده — برمی‌گرداند آیا وضعیت تغییر کرد"""
    now = timezone.now()
    state, created = NotificationState.objects.get_or_create(
        notification=notification,
        user=user,
        defaults={"is_read": True, "read_at": now},
    )

    changed = False
    if created:
        changed = True
    elif not state.is_read:
        state.is_read = True
        state.read_at = now
        state.save(update_fields=["is_read", "read_at", "updated_at"])
        changed = True

    if changed:
        Notification.objects.filter(pk=notification.pk).update(
            total_reads=F("total_reads") + 1
        )
    return changed


def mark_all_as_read(user: User) -> int:
    """
    علامت خوانده‌شده برای همه‌ی نخوانده‌های کاربر.
    برمی‌گرداند تعداد نوتیفیکیشن‌هایی که تازه خوانده شدند.
    """
    now = timezone.now()
    qs = Notification.objects.for_user(user)

    # ۱. stateهایی که وجود دارند ولی unread هستند → update
    existing_unread_ids = list(
        NotificationState.objects
        .filter(user=user, is_read=False, notification__in=qs)
        .values_list("notification_id", flat=True)
    )
    if existing_unread_ids:
        NotificationState.objects.filter(
            user=user, notification_id__in=existing_unread_ids
        ).update(is_read=True, read_at=now)

    # ۲. نوتیف‌هایی که هیچ state ندارند → bulk insert
    notif_ids_with_state = set(
        NotificationState.objects
        .filter(user=user, notification__in=qs)
        .values_list("notification_id", flat=True)
    )
    notif_ids_without_state = list(
        qs.exclude(id__in=notif_ids_with_state).values_list("id", flat=True)
    )
    if notif_ids_without_state:
        NotificationState.objects.bulk_create(
            [
                NotificationState(
                    notification_id=nid,
                    user=user,
                    is_read=True,
                    read_at=now,
                )
                for nid in notif_ids_without_state
            ],
            ignore_conflicts=True,
            batch_size=500,
        )

    # ۳. total_reads برای همه‌ی نوتیف‌هایی که تازه transition شدند +1
    affected = set(existing_unread_ids) | set(notif_ids_without_state)
    if affected:
        Notification.objects.filter(id__in=affected).update(
            total_reads=F("total_reads") + 1
        )

    return len(affected)


def dismiss(user: User, notification: Notification) -> bool:
    """حذف از لیست کاربر — برمی‌گرداند آیا وضعیت تغییر کرد"""
    now = timezone.now()
    state, created = NotificationState.objects.get_or_create(
        notification=notification,
        user=user,
        defaults={"is_dismissed": True, "dismissed_at": now},
    )

    if not created and not state.is_dismissed:
        state.is_dismissed = True
        state.dismissed_at = now
        state.save(update_fields=["is_dismissed", "dismissed_at", "updated_at"])
        return True
    return created