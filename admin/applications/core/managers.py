# backend/apps/core/managers.py
from django.db import models
from django.utils import timezone


class ActiveManager(models.Manager):
    """
    مدیریت فقط آیتم‌های فعال و حذف نشده
    """

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def active(self):
        return self.get_queryset()

    def archived(self):
        return super().get_queryset().filter(deleted_at__isnull=False)