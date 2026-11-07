# applications/support/models.py

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from applications.core.baseModel import BaseModel
from applications.user.models import User


#######################################
# Support (تیکت پشتیبانی)
#######################################
class Support(BaseModel):

    # ── دسته‌بندی ──────────────────────────────────
    class Category(models.TextChoices):
        SITE_ISSUE    = "site_issue",    "مشکلات سایت"
        INVOICE       = "invoice",       "ثبت فاکتور"
        GIFT_ORDER    = "gift_order",    "سفارش هدیه"
        COMPLAINT     = "complaint",     "انتقاد"
        SUGGESTION    = "suggestion",    "پیشنهاد"
        OTHER         = "other",         "سایر"

    # ── وضعیت (مناسب تیکت) ─────────────────────────
    class Status(models.TextChoices):
        OPEN        = "open",         "باز"
        IN_PROGRESS = "in_progress",  "در حال بررسی"
        RESOLVED    = "resolved",     "حل شده"
        CLOSED      = "closed",       "بسته شده"

    # ── اولویت ─────────────────────────────────────
    class Priority(models.TextChoices):
        LOW    = "low",    "کم"
        NORMAL = "normal", "عادی"
        HIGH   = "high",   "زیاد"
        URGENT = "urgent", "فوری"

    # ── هویت ────────────────────────────────────────
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="supports", verbose_name="کاربر (ثبت‌کننده)")
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER, verbose_name="دسته‌بندی")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, verbose_name="وضعیت")
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL, verbose_name="اولویت")

    # ── محتوا ───────────────────────────────────────
    subject = models.CharField(max_length=255, verbose_name="موضوع")
    text = models.TextField(verbose_name="متن پیام")
    file = models.FileField(upload_to="supports/%Y/%m/", null=True, blank=True, validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp", "pdf"])], verbose_name="فایل پیوست")

    # ── لینک به موجودیت مرتبط (اختیاری) ────────────
    reference_type = models.CharField(max_length=32, null=True, blank=True, verbose_name="نوع مرجع", help_text="factor / project / gift_order / promotion_order")
    reference_id = models.CharField(
        max_length=100, null=True, blank=True, db_index=True,
        verbose_name="شناسه مرجع",
    )

    # ── پاسخ ادمین ──────────────────────────────────
    admin_reply = models.TextField(null=True, blank=True, verbose_name="پاسخ ادمین")
    replied_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="support_replies", verbose_name="پاسخ‌دهنده")
    replied_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان پاسخ")

    # ── بستن تیکت ──────────────────────────────────
    closed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="support_closures", verbose_name="بسته‌کننده")
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان بسته شدن")
    close_reason = models.TextField(null=True, blank=True, verbose_name="دلیل بستن")

    class Meta:
        db_table = "support_support"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["category"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["reference_type", "reference_id"]),
        ]
        # برای display در admin
        verbose_name = "تیکت پشتیبانی"
        verbose_name_plural = "تیکت‌های پشتیبانی"

    def __str__(self):
        return f"تیکت #{self.id} - {self.user.mobile} [{self.get_category_display()}]"

    # ── متدهای کمکی ─────────────────────────────────
    def can_user_close(self) -> bool:
        """آیا کاربر می‌تونه تیکت رو ببنده؟"""
        return self.status in (self.Status.OPEN, self.Status.IN_PROGRESS)

    def is_open(self) -> bool:
        return self.status in (self.Status.OPEN, self.Status.IN_PROGRESS)

    def clean(self):
        errors = {}

        if not self.subject or not self.subject.strip():
            errors["subject"] = "موضوع تیکت الزامی است"

        if not self.text or not self.text.strip():
            errors["text"] = "متن پیام الزامی است"

        # اگه reference_type داده شد، reference_id هم باید باشه
        if self.reference_type and not self.reference_id:
            errors["reference_id"] = "شناسه مرجع الزامی است"
        if self.reference_id and not self.reference_type:
            errors["reference_type"] = "نوع مرجع الزامی است"

        # اگه پاسخ داده شده، replied_by هم باید باشه
        if self.admin_reply and not self.replied_by_id:
            errors["replied_by"] = "پاسخ‌دهنده الزامی است"

        if errors:
            raise ValidationError(errors)