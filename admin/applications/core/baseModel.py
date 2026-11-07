# django/applications/core/baseModel.py

import jdatetime
import time
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class BaseModel(models.Model):
    """
    مدل پایه برای همه مدل‌ها
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان بروزرسانی")

    class Meta:
        abstract = True

    @property
    def created_at_jalali(self):
        """تبدیل به تاریخ شمسی"""
        if not self.created_at:
            return None
        return jdatetime.datetime.fromgregorian(datetime=self.created_at).strftime("%Y/%m/%d %H:%M")


class SoftDeleteModel(BaseModel):
    """
    مدل پایه با قابلیت حذف نرم
    """
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان حذف")

    class Meta:
        abstract = True

    def delete(self, soft=True):
        if soft:
            self.deleted_at = timezone.now()
            self.save(update_fields=['deleted_at'])
        else:
            super().delete()

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    @property
    def is_deleted(self):
        return self.deleted_at is not None
