from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone

from applications.core.baseModel import BaseModel

User = get_user_model()


# ═══════════════════════════════════════════════════════════
# QuerySet / Manager
# ═══════════════════════════════════════════════════════════
class NotificationQuerySet(models.QuerySet):
    def for_user(self, user):
        """نوتیفیکیشن‌هایی که این کاربر باید ببیند (sent + منقضی‌نشده)"""
        now = timezone.now()
        return (
            self.filter(
                Q(target_type=Notification.TargetType.ALL)
                | Q(targets__user=user),
                status=Notification.Status.SENT,
                sent_at__lte=now,
            )
            .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
            .distinct()
        )

    def with_read_status(self, user):
        """افزودن is_read و is_dismissed به هر نوتیفیکیشن برای این کاربر"""
        return self.annotate(
            is_read=Exists(
                NotificationState.objects.filter(
                    notification=OuterRef("pk"),
                    user=user,
                    is_read=True,
                )
            ),
            is_dismissed=Exists(
                NotificationState.objects.filter(
                    notification=OuterRef("pk"),
                    user=user,
                    is_dismissed=True,
                )
            ),
        )

    def visible_for_user(self, user):
        """نوتیفیکیشن‌های قابل نمایش (حذف‌نشده)"""
        return self.for_user(user).with_read_status(user).filter(is_dismissed=False)

    def unread_for_user(self, user):
        """نوتیفیکیشن‌های خوانده‌نشده"""
        return (
            self.for_user(user)
            .with_read_status(user)
            .filter(is_read=False, is_dismissed=False)
        )


# ═══════════════════════════════════════════════════════════
# Notification — محتوا + هدف‌گیری + متادیتا
# ═══════════════════════════════════════════════════════════
class Notification(BaseModel):
    class TargetType(models.TextChoices):
        USER = "user", "کاربر خاص"
        USERS = "users", "چند کاربر"
        ALL = "all", "همه کاربران"

    class NotificationType(models.TextChoices):
        SYSTEM = "system", "سیستمی"
        PROMOTION = "promotion", "تبلیغاتی"
        GIFT = "gift", "هدیه"
        PROJECT = "project", "پروژه"
        FACTOR = "factor", "فاکتور"
        SUPPORT = "support", "پشتیبانی"
        ACCOUNT = "account", "حساب کاربری"
        REVIEW = "review", "نظرسنجی"
        VISIT = "visit", "بازدید"
        OTHER = "other", "سایر"

    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        SCHEDULED = "scheduled", "زمان‌بندی شده"
        SENDING = "sending", "در حال ارسال"
        SENT = "sent", "ارسال شده"
        FAILED = "failed", "خطا در ارسال"
        CANCELLED = "cancelled", "لغو شده"

    class Priority(models.TextChoices):
        LOW = "low", "کم"
        NORMAL = "normal", "معمولی"
        HIGH = "high", "فوری"

    # ─────────────── محتوا ───────────────
    title = models.CharField(max_length=200, verbose_name="عنوان")
    body = models.TextField(verbose_name="متن")

    image = models.ImageField(upload_to="notifications/%Y/%m/", null=True, blank=True, verbose_name="تصویر")
    image_size = models.PositiveIntegerField(default=0, verbose_name="حجم تصویر (بایت)")
    image_type = models.CharField(max_length=100, blank=True, default="", verbose_name="نوع تصویر")

    # ─────────────── هدف‌گیری ───────────────
    target_type = models.CharField(max_length=16, choices=TargetType.choices, default=TargetType.USER, db_index=True, verbose_name="نوع هدف‌گیری")

    # ─────────────── دسته و اولویت ───────────────
    notification_type = models.CharField(max_length=32, choices=NotificationType.choices, default=NotificationType.SYSTEM, db_index=True, verbose_name="نوع نوتیفیکیشن")
    priority = models.CharField(max_length=8, choices=Priority.choices, default=Priority.NORMAL, db_index=True, verbose_name="اولویت")

    # ─────────────── اقدام (deep link) ───────────────
    action_type = models.CharField(max_length=32, blank=True, default="", verbose_name="نوع اقدام")
    action_url = models.CharField(max_length=500, blank=True, default="", verbose_name="لینک اقدام")
    action_data = models.JSONField(default=dict, blank=True, verbose_name="داده‌های اقدام")

    # ─────────────── زمان‌بندی ───────────────
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان ارسال برنامه‌ریزی‌شده")
    sent_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name="زمان ارسال واقعی")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان انقضا")

    # ─────────────── وضعیت ───────────────
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT, db_index=True, verbose_name="وضعیت")

    # ─────────────── متادیتا ───────────────
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="notifications_created", verbose_name="سازنده")

    # ─────────────── شمارنده‌های denormalized ───────────────
    # total_recipients: برای ALL بعد از ارسال پر می‌شود (تعداد کاربران فعال در لحظه ارسال)
    # total_reads: با هر transition unread→read در services افزایش می‌یابد
    total_recipients = models.PositiveIntegerField(default=0, verbose_name="تعداد کل گیرندگان")
    total_reads = models.PositiveIntegerField(default=0, verbose_name="تعداد خوانده‌شده")

    objects = NotificationQuerySet.as_manager()

    class Meta:
        db_table = "notification_notification"
        verbose_name = "نوتیفیکیشن"
        verbose_name_plural = "نوتیفیکیشن‌ها"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "sent_at"]),
            models.Index(fields=["target_type", "status", "sent_at"]),
            models.Index(fields=["notification_type", "sent_at"]),
            models.Index(fields=["priority", "status"]),
        ]

    def __str__(self):
        return f"{self.title} [{self.get_target_type_display()}]"

    def clean(self):
        """اعتبارسنجی سازگاری target_type و رکوردهای NotificationTarget"""
        if self.target_type == self.TargetType.ALL:
            if self.pk and self.targets.exists():
                raise ValidationError(
                    "برای target_type=ALL نباید گیرنده مشخص داشته باشید"
                )
        else:
            if self.pk and not self.targets.exists():
                raise ValidationError(
                    "برای USER/USERS باید حداقل یک گیرنده مشخص داشته باشید"
                )

    def mark_as_sent(self, total_recipients: int | None = None):
        """نشان‌گذاری به‌عنوان ارسال‌شده (برای استفاده در services)"""
        self.status = self.Status.SENT
        self.sent_at = timezone.now()
        update_fields = ["status", "sent_at", "updated_at"]
        if total_recipients is not None:
            self.total_recipients = total_recipients
            update_fields.append("total_recipients")
        self.save(update_fields=update_fields)


# ═══════════════════════════════════════════════════════════
# NotificationTarget — گیرندگان مشخص (برای USER/USERS)
# ═══════════════════════════════════════════════════════════
class NotificationTarget(BaseModel):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="targets", verbose_name="نوتیفیکیشن")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_targets", verbose_name="کاربر")

    class Meta:
        db_table = "notification_target"
        verbose_name = "گیرنده نوتیفیکیشن"
        verbose_name_plural = "گیرندگان نوتیفیکیشن"
        unique_together = ("notification", "user")
        indexes = [
            models.Index(fields=["user", "notification"]),
        ]

    def __str__(self):
        return f"{self.notification_id} → {self.user_id}"


# ═══════════════════════════════════════════════════════════
# NotificationState — وضعیت خواندن / حذف برای هر کاربر
# ═══════════════════════════════════════════════════════════
class NotificationState(BaseModel):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="states", verbose_name="نوتیفیکیشن")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_states", verbose_name="کاربر")

    is_read = models.BooleanField(default=False, db_index=True, verbose_name="خوانده شده")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان خواندن")

    is_dismissed = models.BooleanField(default=False, db_index=True, verbose_name="از لیست حذف شده")
    dismissed_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان حذف از لیست")

    class Meta:
        db_table = "notification_state"
        verbose_name = "وضعیت نوتیفیکیشن کاربر"
        verbose_name_plural = "وضعیت‌های نوتیفیکیشن کاربران"
        unique_together = ("notification", "user")
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["user", "is_dismissed"]),
        ]

    def __str__(self):
        return f"{self.notification_id}/{self.user_id} read={self.is_read}"