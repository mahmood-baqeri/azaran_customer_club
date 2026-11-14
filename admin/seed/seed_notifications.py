# admin/seed/seed_notifications.py

import os
import sys
import django
import random
from datetime import timedelta

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # پوشه admin/
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import transaction
from django.utils import timezone

from applications.user.models import User
from applications.notification.models import (
    Notification,
    NotificationState,
    NotificationTarget,
)

# نشانگر رکوردهای فیک — برای پاکسازی ایمن بدون آسیب به داده‌های واقعی
FAKE_MARKER = {"is_fake": True}


# ═══════════════════════════════════════════════════════════
# قالب‌های آماده‌ی اعلان اختصاصی (USER)
# (title, body, type, priority, action_type, action_url, action_data)
# ═══════════════════════════════════════════════════════════
USER_TEMPLATES = [
    (
        "هدیه خوش‌آمدگویی",
        "به باشگاه آذر خوش آمدید! یک هدیه ویژه برای شما آماده است.",
        Notification.NotificationType.GIFT,
        Notification.Priority.HIGH,
        "open_gift",
        "/gift",
        {"gift_id": 1},
    ),
    (
        "پروژه شما تایید شد",
        "پروژه ثبت‌شده شما توسط کارشناس تایید شد و ۵۰ امتیاز به شما تعلق گرفت.",
        Notification.NotificationType.PROJECT,
        Notification.Priority.NORMAL,
        "open_project",
        "/projects/42",
        {"project_id": 42},
    ),
    (
        "چالش روزانه آماده است",
        "چالش امروز آماده است، شرکت کنید و امتیاز بگیرید.",
        Notification.NotificationType.SYSTEM,
        Notification.Priority.NORMAL,
        "",
        "",
        {},
    ),
    (
        "فاکتور شما صادر شد",
        "فاکتور شماره ۹۸۷۶ برای شما صادر شد. جهت مشاهده جزئیات وارد بخش فاکتورها شوید.",
        Notification.NotificationType.FACTOR,
        Notification.Priority.NORMAL,
        "open_factor",
        "/factors/9876",
        {"factor_id": 9876},
    ),
    (
        "سفارش هدیه ارسال شد",
        "سفارش هدیه شما به ارزش ۲۰۰ امتیاز ارسال شد. کد رهگیری: ۱۲۳۴۵۶",
        Notification.NotificationType.GIFT,
        Notification.Priority.NORMAL,
        "track_gift",
        "/gifts/orders/12",
        {"order_id": 12},
    ),
    (
        "پاسخ جدید در پشتیبانی",
        "کارشناس پشتیبانی به تیکت شما پاسخ داد. لطفاً بررسی کنید.",
        Notification.NotificationType.SUPPORT,
        Notification.Priority.HIGH,
        "open_ticket",
        "/support/55",
        {"ticket_id": 55},
    ),
    (
        "تکمیل مدارک شغلی",
        "برای افزایش اعتبار و دریافت امتیاز، مدارک شغلی خود را تکمیل کنید.",
        Notification.NotificationType.ACCOUNT,
        Notification.Priority.LOW,
        "open_certificates",
        "/profile/completion",
        {},
    ),
    (
        "نظرسنجی جدید",
        "لطفاً در نظرسنجی جدید شرکت کنید و ۳۰ امتیاز کسب کنید.",
        Notification.NotificationType.REVIEW,
        Notification.Priority.NORMAL,
        "open_review",
        "/review",
        {"review_id": 3},
    ),
    (
        "بازدید حضوری تایید شد",
        "درخواست بازدید حضوری شما از کارخانه تایید شد.",
        Notification.NotificationType.VISIT,
        Notification.Priority.HIGH,
        "open_visit",
        "/visits/8",
        {"visit_id": 8},
    ),
    (
        "پک تبلیغاتی ارسال شد",
        "پک تبلیغاتی شما با موفقیت ارسال شد و در حال پردازش است.",
        Notification.NotificationType.PROMOTION,
        Notification.Priority.NORMAL,
        "open_promotion",
        "/promotions/4",
        {"promotion_id": 4},
    ),
    (
        "پروژه شما رد شد",
        "متأسفانه پروژه شما به دلیل نقص اطلاعات رد شد. لطفاً اصلاح و مجدداً ارسال کنید.",
        Notification.NotificationType.PROJECT,
        Notification.Priority.HIGH,
        "open_project",
        "/projects/41",
        {"project_id": 41},
    ),
    (
        "تبریک! به سطح استادکار رسیدید",
        "شما به سطح استادکار رسیدید و مزایای جدیدی برای شما فعال شد.",
        Notification.NotificationType.SYSTEM,
        Notification.Priority.HIGH,
        "open_level",
        "/profile/level",
        {},
    ),
]

# اعلان همگانی
BROADCAST_TEMPLATES = [
    (
        "به‌روزرسانی باشگاه",
        "نسخه جدید باشگاه آذر با امکانات بیشتر منتشر شد. از بخش تنظیمات به‌روزرسانی کنید.",
        Notification.NotificationType.SYSTEM,
        Notification.Priority.NORMAL,
    ),
    (
        "جشنواره فروش ویژه",
        "تخفیف ویژه هدایا تا پایان هفته! همین حالا از بخش هدایا خرید کنید.",
        Notification.NotificationType.PROMOTION,
        Notification.Priority.HIGH,
    ),
]


# ═══════════════════════════════════════════════════════════
# ساخت یک اعلان با sent_at و created_at دلخواه
# ═══════════════════════════════════════════════════════════
def _create_notification(
    *,
    title: str,
    body: str,
    target_type: str,
    notification_type: str,
    priority: str,
    sent_at,
    created_by: User,
    action_type: str = "",
    action_url: str = "",
    action_data: dict | None = None,
    total_recipients: int = 1,
) -> Notification:
    notification = Notification.objects.create(
        title=title,
        body=body,
        target_type=target_type,
        notification_type=notification_type,
        priority=priority,
        action_type=action_type,
        action_url=action_url,
        action_data={**(action_data or {}), **FAKE_MARKER},
        status=Notification.Status.SENT,
        sent_at=sent_at,
        created_by=created_by,
        total_recipients=total_recipients,
        total_reads=0,
    )
    # created_at از BaseModel با auto_now_add ست می‌شود → override با sent_at
    Notification.objects.filter(id=notification.id).update(created_at=sent_at)
    notification.refresh_from_db()
    return notification


# ═══════════════════════════════════════════════════════════
# Seeder
# ═══════════════════════════════════════════════════════════
def seed_notifications():
    user_id = 1

    if not User.objects.filter(id=user_id).exists():
        print(f"❌ کاربر با آیدی {user_id} یافت نشد!")
        return

    user = User.objects.get(id=user_id)
    print(f"⏳ در حال تولید اعلان‌های فیک برای کاربر {user_id}...")

    with transaction.atomic():
        # ─────────────── ۱. پاکسازی رکوردهای فیک قبلی ───────────────
        # حالت ۱: اعلان‌هایی که همین کاربر گیرنده‌شان بوده
        existing_user_notif_ids = list(
            NotificationTarget.objects
            .filter(user=user, notification__action_data__contains=FAKE_MARKER)
            .values_list("notification_id", flat=True)
        )
        # حالت ۲: اعلان‌های broadcast فیک (بدون target)
        existing_broadcast_ids = list(
            Notification.objects
            .filter(target_type=Notification.TargetType.ALL, action_data__contains=FAKE_MARKER)
            .values_list("id", flat=True)
        )
        all_fake_ids = set(existing_user_notif_ids) | set(existing_broadcast_ids)

        if all_fake_ids:
            NotificationState.objects.filter(notification_id__in=all_fake_ids).delete()
            NotificationTarget.objects.filter(notification_id__in=all_fake_ids).delete()
            Notification.objects.filter(id__in=all_fake_ids).delete()
            print(f"🧹 {len(all_fake_ids)} اعلان فیک قبلی پاک شد.")

        now = timezone.now()
        total_created = 0
        total_read = 0
        total_dismissed = 0

        # ─────────────── ۲. اعلان‌های اختصاصی (USER) ───────────────
        for (
            title,
            body,
            ntype,
            priority,
            action_type,
            action_url,
            action_data,
        ) in USER_TEMPLATES:
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            sent_at = now - timedelta(days=days_ago, hours=hours_ago)

            notif = _create_notification(
                title=title,
                body=body,
                target_type=Notification.TargetType.USER,
                notification_type=ntype,
                priority=priority,
                sent_at=sent_at,
                created_by=user,
                action_type=action_type,
                action_url=action_url,
                action_data=action_data,
                total_recipients=1,
            )
            NotificationTarget.objects.create(notification=notif, user=user)

            # ۶۰٪ خوانده‌شده
            if random.random() < 0.6:
                read_at = sent_at + timedelta(minutes=random.randint(3, 240))
                NotificationState.objects.create(
                    notification=notif,
                    user=user,
                    is_read=True,
                    read_at=min(read_at, now),
                )
                Notification.objects.filter(id=notif.id).update(total_reads=1)
                total_read += 1

            total_created += 1

        # ─────────────── ۳. یک اعلان چندکاربره (USERS) ───────────────
        sent_at = now - timedelta(days=random.randint(2, 15))
        multi = _create_notification(
            title="اطلاعیه گروهی",
            body="این اعلان برای گروهی از کاربران فعال ارسال شده است.",
            target_type=Notification.TargetType.USERS,
            notification_type=Notification.NotificationType.SYSTEM,
            priority=Notification.Priority.NORMAL,
            sent_at=sent_at,
            created_by=user,
            total_recipients=1,
        )
        NotificationTarget.objects.create(notification=multi, user=user)
        total_created += 1

        # ─────────────── ۴. اعلان‌های همگانی (ALL) ───────────────
        active_count = User.objects.filter(is_active=True).count()
        for title, body, ntype, priority in BROADCAST_TEMPLATES:
            sent_at = now - timedelta(days=random.randint(1, 20))
            notif = _create_notification(
                title=title,
                body=body,
                target_type=Notification.TargetType.ALL,
                notification_type=ntype,
                priority=priority,
                sent_at=sent_at,
                created_by=user,
                total_recipients=active_count,
            )
            total_created += 1

            if random.random() < 0.5:
                read_at = sent_at + timedelta(minutes=random.randint(10, 300))
                NotificationState.objects.create(
                    notification=notif,
                    user=user,
                    is_read=True,
                    read_at=min(read_at, now),
                )
                Notification.objects.filter(id=notif.id).update(total_reads=1)
                total_read += 1

        # ─────────────── ۵. یک اعلان dismiss شده ───────────────
        dismissed_sent = now - timedelta(days=5)
        dismissed = _create_notification(
            title="اعلان حذف‌شده (تست)",
            body="این اعلان برای تست قابلیت dismiss استفاده شده است.",
            target_type=Notification.TargetType.USER,
            notification_type=Notification.NotificationType.OTHER,
            priority=Notification.Priority.LOW,
            sent_at=dismissed_sent,
            created_by=user,
            total_recipients=1,
        )
        NotificationTarget.objects.create(notification=dismissed, user=user)
        NotificationState.objects.create(
            notification=dismissed,
            user=user,
            is_read=True,
            read_at=dismissed_sent + timedelta(hours=1),
            is_dismissed=True,
            dismissed_at=dismissed_sent + timedelta(hours=2),
        )
        Notification.objects.filter(id=dismissed.id).update(total_reads=1)
        total_created += 1
        total_read += 1
        total_dismissed += 1

        # ─────────────── ۶. خلاصه ───────────────
        visible_unread = total_created - total_read
        print("✅ اعلان‌های فیک با موفقیت ثبت شدند!")
        print(f"📊 کل اعلان‌ها        : {total_created}")
        print(f"📖 خوانده‌شده         : {total_read}")
        print(f"🔴 نخوانده           : {visible_unread}")
        print(f"🗑️ حذف‌شده از لیست    : {total_dismissed}")


if __name__ == "__main__":
    seed_notifications()