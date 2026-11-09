# applications/review/models.py

from django.db import models
from django.core.validators import FileExtensionValidator
from applications.core.baseModel import BaseModel

#######################################
# Learn (آموزش‌ها)
#######################################
class Learn(BaseModel):   
    class Size(models.TextChoices):
        HALF = "half", "نیم صفحه"
        FULL = "full", "تمام صفحه"

    title = models.CharField(max_length=255, verbose_name="عنوان")
    sub_text = models.CharField(max_length=255, verbose_name="توضیح", null=True, blank=True) # 👈 blank=True اضافه شد
    caption = models.CharField(max_length=255, verbose_name="کپشن", null=True, blank=True)   # 👈 blank=True اضافه شد
    full_text = models.TextField(verbose_name="متن کامل")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    size = models.CharField(max_length=20, choices=Size.choices, default=Size.HALF, verbose_name="عرض صفحه")
    time = models.IntegerField(null=True, blank=True, verbose_name="تایم مطالعه (دقیقه)")

    # ── تصویر ────────────────────────────────
    photo = models.ImageField(
        upload_to="learn/%Y/%m/", 
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
        verbose_name="تصویر"
    )

    class Meta:
        db_table = 'learn_learn'
        verbose_name = "آموزش"
        verbose_name_plural = "آموزش‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title 