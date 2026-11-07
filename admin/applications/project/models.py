# applications/project/models.py

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q, Sum

from applications.core.baseModel import BaseModel
from applications.user.models import User


#######################################
# Project
#######################################
class Project(BaseModel):
    class Type(models.TextChoices):
        WATER  = "water",  "آبی"
        GAS = "gas", "گازی"

        
    class Status(models.TextChoices):
        PENDING  = "pending",  "در انتظار"
        APPROVED = "approved", "تایید شده"
        REJECTED = "rejected", "رد شده"


    type = models.CharField(max_length=20, choices=Type.choices, default=Type.WATER, verbose_name="نوع")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects", verbose_name="کاربر")
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name="عنوان")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="وضعیت")
    
    # ── اطلاعات اجرایی ──────────────────────────────
    completion_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ اتمام پروزه")
    address = models.CharField(max_length=255 ,null=True, blank=True, verbose_name="استان،شهر،خیایان،کوچه،پلاک")
    owner_mobile = models.CharField(max_length=255, null=True, blank=True, verbose_name="")
    
    # ── متره ────────────────────────────────────────
    unit_count          = models.PositiveIntegerField(null=True, blank=True, verbose_name="تعداد واحد")
    number_water_taps   = models.PositiveIntegerField(null=True, blank=True, verbose_name="تعداد شیرآبی")
    number_gas_taps     = models.PositiveIntegerField(null=True, blank=True, verbose_name="تعداد شیرگازی")
    number_connections  = models.PositiveIntegerField(null=True, blank=True, verbose_name="تعداد اتصالات")
    pipe_length         = models.PositiveIntegerField(null=True, blank=True, verbose_name="متراژ لوله")

    # Audit trail
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_projects", verbose_name="تأییدکننده")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان تأیید")
    rejected_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان رد")
    rejection_reason = models.TextField(null=True, blank=True, verbose_name="دلیل رد")

    class Meta:
        db_table = "project_project"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["type"]),  
        ]

    def __str__(self):
        return (self.title or f"پروژه #{self.id}")[:50]

    # ✅ کمکی برای بررسی مجموع درصد
    def total_colleague_percent(self) -> int:
        return self.colleagues.aggregate(t=Sum("percent"))["t"] or 0


#######################################
# Colleague (همکاران پروژه)
#######################################
class Colleague(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="colleagues")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="project_participation_roles", verbose_name="همکار")
    percent = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(100)], verbose_name="درصد مشارکت در پروژه")

    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        db_table = "project_colleague"
        ordering = ["id"]
        unique_together = ("project", "user")

    def __str__(self):
        return f"{self.user.mobile} - {self.percent}%"

    def clean(self):
        """چک در سطح مدل (admin panel هم اینو صدا می‌زنه)."""
        if self.user_id and self.project_id and self.user_id == self.project.user_id:
            raise ValidationError("صاحب پروژه نمی‌تواند همکار خودش باشد")


#######################################
# Attachment
#######################################
class Attachment(BaseModel):
    class FileType(models.TextChoices):
        Building  = "exterior_view_building",  "نمای خارجی ساختمان"
        Installed = "azar_products_installed", "محصولات آذر نصب شده"
        Depot     = "azar_products_depot",     "دپو محصولات آذر نصب شده"
        Invoice   = "Invoice",                 "فاکتور"

    class Status(models.TextChoices):
        PENDING  = "pending",  "در انتظار"
        APPROVED = "approved", "تایید شده"
        REJECTED = "rejected", "رد شده"

    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="attachments")
    type = models.CharField(max_length=100, choices=FileType.choices, default=FileType.Building, verbose_name="نوع فایل")
    file = models.FileField(upload_to="projects/attachments/%Y/%m/", verbose_name="فایل")
    file_size = models.PositiveIntegerField(default=0, verbose_name="حجم فایل (بایت)")
    file_type = models.CharField(max_length=100, blank=True, default="", verbose_name="MIME")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="وضعیت")

    class Meta:
        db_table = "project_attachment"
        unique_together = ("project", "type")

    def __str__(self):
        return f"{self.get_type_display()} - پروژه #{self.project_id}"