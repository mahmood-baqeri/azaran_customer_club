# Path: applications/notification/clean_data.py

# applications/notification/clean_data.py

from datetime import datetime

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import Notification


def _parse_dt(value):
    """رشته ISO/date → datetime آگاه به timezone | None."""
    value = (value or "").strip()
    if not value:
        return None
    dt = parse_datetime(value)
    if dt is None:
        try:
            dt = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    return dt


def notification__clean__data(post, files=None):
    """اعتبارسنجی فرم نوتیفیکیشن.

    خروجی: (cleaned_dict, errors_list)
    """
    errors = []

    title = (post.get("title") or "").strip()
    if not title:
        errors.append("عنوان الزامی است")
    elif len(title) > 200:
        errors.append("عنوان حداکثر ۲۰۰ کاراکتر است")

    body = (post.get("body") or "").strip()
    if not body:
        errors.append("متن الزامی است")

    target_type = (post.get("target_type") or "").strip()
    if target_type not in dict(Notification.TargetType.choices):
        errors.append("نوع هدف‌گیری نامعتبر است")

    target_user_ids = []
    if target_type == Notification.TargetType.USER:
        ids = [int(x) for x in post.getlist("target_users") if str(x).isdigit()]
        if len(ids) != 1:
            errors.append("برای هدف‌گیری «کاربر خاص» دقیقاً یک کاربر انتخاب کنید")
        target_user_ids = ids
    elif target_type == Notification.TargetType.USERS:
        ids = [int(x) for x in post.getlist("target_users") if str(x).isdigit()]
        if not ids:
            errors.append("برای هدف‌گیری «چند کاربر» حداقل یک کاربر انتخاب کنید")
        target_user_ids = ids
    # ALL → target_user_ids خالی

    notification_type = (post.get("notification_type") or "").strip()
    if notification_type not in dict(Notification.NotificationType.choices):
        errors.append("نوع نوتیفیکیشن نامعتبر است")

    priority = (post.get("priority") or "").strip()
    if priority not in dict(Notification.Priority.choices):
        errors.append("اولویت نامعتبر است")

    scheduled_at = _parse_dt(post.get("scheduled_at"))
    expires_at = _parse_dt(post.get("expires_at"))
    if scheduled_at and expires_at and expires_at < scheduled_at:
        errors.append("زمان انقضا نمی‌تواند قبل از زمان ارسال باشد")

    if errors:
        return {}, errors

    return {
        "title":             title,
        "body":              body,
        "target_type":       target_type,
        "target_user_ids":   target_user_ids,
        "notification_type": notification_type,
        "priority":          priority,
        "action_type":       (post.get("action_type") or "").strip(),
        "action_url":        (post.get("action_url") or "").strip(),
        "scheduled_at":      scheduled_at,
        "expires_at":        expires_at,
    }, []