# applications/factor/models.py

import re

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from applications.core.baseModel import BaseModel
from applications.user.models import User


#######################################
# Factor
#######################################
class Factor(BaseModel):
    class Status(models.TextChoices):
        PENDING  = "pending",  "در انتظار"
        APPROVED = "approved", "تایید شده"
        REJECTED = "rejected", "رد شده"

    # ── هویت ────────────────────────────────────────
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="factors", verbose_name="کاربر (ثبت‌کننده)")
    invoice_number = models.CharField(max_length=64, null=True, blank=True, db_index=True, verbose_name="شماره فاکتور", help_text="اختیاری — شماره رسمی فاکتور برای پیگیری")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="وضعیت")

    # ── تصویر فاکتور ────────────────────────────────
    photo = models.ImageField(upload_to="factors/%Y/%m/", validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp", "pdf"])])

    # ── اطلاعات فاکتور ──────────────────────────────
    invoice_issue_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ صدور فاکتور")
    amount = models.PositiveIntegerField(
        null=True, blank=True, db_index=True,
        validators=[MinValueValidator(1)],
        verbose_name="مبلغ فاکتور (ریال)",
        help_text="برای محاسبه امتیاز INVOICE الزامی است",
    )

    # ── متره (اطلاعات کمکی — روی امتیاز اثر ندارد) ────
    number_water_taps  = models.PositiveIntegerField(null=True, blank=True, verbose_name="تعداد شیر")
    number_connections = models.PositiveIntegerField(null=True, blank=True, verbose_name="تعداد اتصالات")
    pipe_length        = models.PositiveIntegerField(null=True, blank=True, verbose_name="متراژ لوله")

    # ── اطلاعات فروشگاه ─────────────────────────────
    shop_name      = models.CharField(max_length=255, null=True, blank=True, verbose_name="نام فروشگاه")
    seller_phone   = models.CharField(max_length=20, null=True, blank=True, verbose_name="تلفن فروشنده")
    seller_address = models.CharField(max_length=255, null=True, blank=True, verbose_name="آدرس فروشنده")

    # ── Audit trail ─────────────────────────────────
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_factors", verbose_name="تأییدکننده")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان تأیید")
    rejected_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان رد")
    rejection_reason = models.TextField(null=True, blank=True, verbose_name="دلیل رد")

    class Meta:
        db_table = "factor_factor"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["invoice_number"]),
            models.Index(fields=["invoice_issue_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["invoice_number"],
                condition=models.Q(invoice_number__isnull=False),
                name="uniq_factor_invoice_number",
            ),
        ]

    def __str__(self):
        num = self.invoice_number or f"#{self.id}"
        return f"فاکتور {num} - {self.user.mobile}"

    def clean(self):
        errors = {}

        if self.amount is not None and self.amount <= 0:
            errors["amount"] = "مبلغ فاکتور باید بزرگ‌تر از صفر باشد"

        if self.invoice_issue_at and self.invoice_issue_at > timezone.now():
            errors["invoice_issue_at"] = "تاریخ صدور فاکتور نمی‌تواند در آینده باشد"

        if self.seller_phone:
            if not (
                re.match(r"^09\d{9}$", self.seller_phone)
                or re.match(r"^0\d{2,3}\d{7,8}$", self.seller_phone)
            ):
                errors["seller_phone"] = "فرمت تلفن فروشنده نامعتبر است"

        if self.status == self.Status.REJECTED and not self.rejection_reason:
            errors["rejection_reason"] = "دلیل رد الزامی است"

        if errors:
            raise ValidationError(errors)