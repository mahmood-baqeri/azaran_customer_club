from django.db import models
from django.utils import timezone
from applications.user.models import User
from applications.core.keyValue import Applications


class RequestLog(models.Model):
    # کاربر
    user = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="request_logs",
        verbose_name="کاربر",
    )
    is_authenticated = models.BooleanField(default=False)

    # محل درخواست
    method = models.CharField(max_length=10)                 # GET/POST/PUT/...
    path = models.CharField(max_length=512)                  # /admin/users/1/
    full_path = models.TextField(blank=True)                 # با query string
    view_name = models.CharField(max_length=255, blank=True, null=True)  # نام url
    module = models.CharField(max_length=100, blank=True, null=True)     # Admin / User / ...

    # پارامترها
    query_params = models.JSONField(default=dict, blank=True)
    body_params = models.JSONField(default=dict, blank=True) # فقط کلیدهای امن
    status_code = models.IntegerField(null=True, blank=True)
    is_ajax = models.BooleanField(default=False)
    is_api = models.BooleanField(default=False)              # FastAPI/DRF

    # نتیجه
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    action = models.CharField(max_length=100, blank=True, null=True)  # از view یا دکوراتور

    # زمان
    created = models.DateTimeField(default=timezone.now, db_index=True)
    duration_ms = models.IntegerField(null=True, blank=True)  # زمان اجرای ویو

    # متادیتای کلاینت
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    os = models.CharField(max_length=100, blank=True, null=True)
    device = models.CharField(max_length=100, blank=True, null=True)
    browser = models.CharField(max_length=100, blank=True, null=True)
    referer = models.TextField(blank=True, null=True)
    session_key = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'log'
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["user", "-created"]),
            models.Index(fields=["path", "-created"]),
            models.Index(fields=["created"]),
        ]
        
        