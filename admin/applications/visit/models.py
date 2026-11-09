# applications/visit/models.py

from django.core.exceptions import ValidationError
from django.db import models

from applications.core.baseModel import BaseModel
from applications.user.models import User


#######################################
# Visit (بازدید از کارخانه)
#######################################
class Visit(BaseModel):
    date = models.DateTimeField(null=True, blank=True, verbose_name="زمان")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    capacity = models.IntegerField(null=True, blank=True, verbose_name="ظرفیت")

    class Meta:
        db_table = "visit_visit"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]
        verbose_name = "بازدید"
        verbose_name_plural = "بازدیدها"

    def __str__(self):
        return f"بازدید {self.id} - {self.date}"


#######################################
# درخواست بازدید از کارخانه
#######################################
class RequestVisit(BaseModel):
    class Status(models.TextChoices):
        PENDING  = "pending",  "در انتظار"
        APPROVED = "approved", "تایید شده"
        REJECTED = "rejected", "رد شده"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="visit_requests", verbose_name="کاربر")
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name="requests", verbose_name="بازدید")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="وضعیت")
    
    have_companion = models.BooleanField(default=False, verbose_name="همراه دارم")
    companion_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="نام همراه")
    companion_family = models.CharField(max_length=255, null=True, blank=True, verbose_name="نام خانوادگی همراه")
    companion_mobile = models.CharField(max_length=255, null=True, blank=True, verbose_name="موبایل همراه")
    
    
    # ── زمان تایید و رد ──────────────────────────────
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان تایید")
    rejected_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان رد")
    rejection_reason = models.TextField(null=True, blank=True, verbose_name="دلیل رد") # اضافه کردن دلیل رد توصیه می‌شود

    class Meta:
        db_table = "visit_request"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["user", "-created_at"]),
        ]
        # 👈 جلوگیری از ثبت درخواست تکراری برای یک بازدید
        constraints = [
            models.UniqueConstraint(
                fields=["user", "visit"], 
                name="unique_user_visit_request"
            )
        ]
        verbose_name = "درخواست بازدید"
        verbose_name_plural = "درخواست‌های بازدید"

    def __str__(self):
        return f"درخواست #{self.id} - {self.user.mobile} برای بازدید {self.visit_id}"

    def clean(self):
        if self.have_companion:
            if not self.companion_name or not self.companion_family or not self.companion_mobile:
                raise ValidationError("اطلاعات همراه کامل نیست")
        
           # 👈 قانون عدم برگشت به عقب
        if self.pk: # اگر در حال ویرایش رکورد موجود هستیم
            original = RequestVisit.objects.get(pk=self.pk)
            if original.status in [self.Status.APPROVED, self.Status.REJECTED]:
                if original.status != self.status:
                    raise ValidationError("وضعیت درخواست‌های تایید یا رد شده، قابل تغییر نیست.")