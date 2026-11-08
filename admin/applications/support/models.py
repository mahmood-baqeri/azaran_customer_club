# applications/support/models.py

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

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

    # ── وضعیت ─────────────────────────
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
    subject = models.CharField(max_length=255, verbose_name="موضوع")

    # ── آخرین فعالیت (برای مرتب‌سازی چت‌ها) ─────────
    # این فیلد برای این است که تیکت‌های دارای پیام جدید، در بالای لیست قرار بگیرند
    last_message_at = models.DateTimeField(default=timezone.now, verbose_name="زمان آخرین پیام")

    # ── بستن تیکت ──────────────────────────────────
    closed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="support_closures", verbose_name="بسته‌کننده")
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان بسته شدن")
    close_reason = models.TextField(null=True, blank=True, verbose_name="دلیل بستن")

    class Meta:
        db_table = "support_support"
        ordering = ["-last_message_at"] # مرتب‌سازی بر اساس آخرین پیام
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["category"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["user", "-last_message_at"]),
        ]
        verbose_name = "تیکت پشتیبانی"
        verbose_name_plural = "تیکت‌های پشتیبانی"

    def __str__(self):
        return f"تیکت #{self.id} - {self.user.mobile} [{self.get_category_display()}]"

    # ── متدهای کمکی ─────────────────────────────────
    def can_user_close(self) -> bool:
        return self.status in (self.Status.OPEN, self.Status.IN_PROGRESS)

    def is_open(self) -> bool:
        return self.status in (self.Status.OPEN, self.Status.IN_PROGRESS)

    def clean(self):
        errors = {}
        
        if not self.subject or not self.subject.strip():
            errors["subject"] = "موضوع تیکت الزامی است"

        if self.status == self.Status.CLOSED:
            if not self.closed_by_id:
                errors["closed_by"] = "بسته‌کننده تیکت الزامی است"
            if not self.closed_at:
                self.closed_at = timezone.now()

        if errors:
            raise ValidationError(errors)


#######################################
# SupportMessage (پیام‌های چت)
#######################################
class SupportMessage(BaseModel):
    ticket = models.ForeignKey(Support, on_delete=models.CASCADE, related_name="messages", verbose_name="تیکت مربوطه")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="فرستنده")
    
    # ── محتوا ───────────────────────────────────────
    text = models.TextField(verbose_name="متن پیام")
    file = models.FileField(
        upload_to="supports/attachments/%Y/%m/", 
        null=True, 
        blank=True, 
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp", "pdf", "zip", "rar"])], 
        verbose_name="فایل پیوست"
    )

    # ── وضعیت پیام ──────────────────────────────────
    is_admin_reply = models.BooleanField(default=False, verbose_name="آیا پاسخ ادمین است؟")
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده؟") # برای نمایش تیک آبی یا نوتیفیکیشن

    class Meta:
        db_table = "support_message"
        ordering = ["created_at"] # پیام‌ها به ترتیب زمان ارسال
        indexes = [
            models.Index(fields=["ticket", "created_at"]),
        ]
        verbose_name = "پیام تیکت"
        verbose_name_plural = "پیام‌های تیکت"

    def __str__(self):
        sender_type = "ادمین" if self.is_admin_reply else "کاربر"
        return f"پیام #{self.id} - تیکت {self.ticket.id} - {sender_type}"

    def save(self, *args, **kwargs):
        # وقتی پیام جدیدی ارسال می‌شود، زمان آخرین پیام تیکت را به‌روزرسانی می‌کنیم
        # تا در لیست تیکت‌ها، این تیکت به بالای لیست منتقل شود
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if is_new:
            # آپدیت زمان تیکت بدون ایجاد سیگنال‌های اضافی
            Support.objects.filter(id=self.ticket_id).update(last_message_at=self.created_at)
            
            # اگر ادمین پاسخ داد و تیکت در حالت OPEN بود، آن را به IN_PROGRESS تغییر می‌دهیم
            if self.is_admin_reply and self.ticket.status == Support.Status.OPEN:
                Support.objects.filter(id=self.ticket_id).update(status=Support.Status.IN_PROGRESS)

    def clean(self):
        if not self.text or not self.text.strip():
            if not self.file:
                raise ValidationError({"text": "متن پیام یا فایل پیوست الزامی است"})