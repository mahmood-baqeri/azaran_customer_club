# applications/gallery/models.py

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from applications.core.baseModel import BaseModel
from applications.user.models import User


#######################################
# Gallery (پست‌های گالری)
#######################################
class Gallery(BaseModel):
    class Status(models.TextChoices):
        PENDING  = "pending",  "در انتظار"
        APPROVED = "approved", "تایید شده"
        REJECTED = "rejected", "رد شده"

    # ── هویت ────────────────────────────────────────
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="gallery_posts", verbose_name="کاربر (ثبت‌کننده)")
    status = models.CharField(max_length=20,  choices=Status.choices, default=Status.PENDING, verbose_name="وضعیت")

    # ── تصویر ────────────────────────────────────────
    photo = models.ImageField(upload_to="gallery/%Y/%m/", validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])])

    # ── اطلاعات ─────────────────────────────────────
    caption = models.CharField(max_length=255, null=True, blank=True, verbose_name="کپشن")
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name="لوکیشن")

    class Meta:
        db_table = "gallery_gallery"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["user", "-created_at"]),
        ]
        verbose_name = "پست گالری"
        verbose_name_plural = "پست‌های گالری"

    def __str__(self):
        return f"گالری #{self.id} - {self.user.mobile} [{self.get_status_display()}]"


#######################################
# Gallery Like (لایک‌های گالری)
#######################################
class GalleryLike(BaseModel):
    
    # ── هویت ────────────────────────────────────────
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="gallery_likes", verbose_name="کاربر (لایک‌کننده)")
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE,  related_name="likes", verbose_name="پست گالری")

    class Meta:
        db_table = "gallery_like"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["gallery"]), # 👈 اضافه شد: برای جستجوی سریع لایک‌های یک پست
        ]
        # 👈 اضافه شد: جلوگیری از لایک تکراری توسط یک کاربر برای یک پست
        constraints = [
            models.UniqueConstraint(
                fields=["user", "gallery"], 
                name="unique_user_gallery_like"
            )
        ]
        verbose_name = "لایک گالری"
        verbose_name_plural = "لایک‌های گالری"

    def __str__(self):
        return f"{self.user.mobile} liked Gallery #{self.gallery_id}"