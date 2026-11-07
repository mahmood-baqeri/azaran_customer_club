# applications/gift/models.py

from django.db import models
from applications.core.baseModel import BaseModel
from applications.user.models import User
from django.utils.translation import gettext_lazy as _


class Gift(BaseModel):
     
     class ForUser(models.TextChoices):
        SELLER = "seller", "هدایا فروشندگان"
        EXECUTIVE = "executive", "هدایا مجریان"
     
     for_user = models.CharField(max_length=16, choices=ForUser.choices, default=ForUser.SELLER)
     title = models.CharField(max_length=200, verbose_name="عنوان")
     description = models.TextField(null=True, blank=True, verbose_name="توضیحات")
     photo = models.ImageField(upload_to="gifts/", null=True, blank=True, verbose_name="تصویر")
     gallery = models.JSONField(default=list, blank=True, null=True, verbose_name="گالری تصاویر")
     azar_value = models.PositiveIntegerField(default=0, verbose_name="ارزش به آذر")
     stock = models.IntegerField(default=0, verbose_name="موجودی")
     is_active = models.BooleanField(default=True, verbose_name="فعال")

     class Meta:
        db_table = "gift_gift"
        verbose_name = "هدیه"
        verbose_name_plural = "هدایا"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active"]),
        ]

     def __str__(self):
        return f"{self.title} ({self.azar_value} آذر)"


class GiftOrder(BaseModel):
    # بدون تغییر — همان قبلی
    class Status(models.TextChoices):        
        PENDING = "pending", "ثبت سفارش"
        APPROVED = "approved", "تایید سفارش"
        SHIPPED = "shipped", "تحویل به پست"
        DELIVERED = "delivered", "تحویل به مشتری"
        REJECTED = "rejected", "رد شده"
        CANCELLED = "cancelled", "لغو شده"
        RETURNED = "returned", "مرجوع شده"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="gift_orders", verbose_name="کاربر")
    gift = models.ForeignKey(Gift, on_delete=models.PROTECT, related_name="orders", verbose_name="هدیه")
    
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")
    total_azar_value = models.PositiveIntegerField(default=0, verbose_name="ارزش کل (آذر)")

    receiver_name = models.CharField(max_length=150, verbose_name="نام گیرنده")
    receiver_phone = models.CharField(max_length=20, verbose_name="تلفن گیرنده")
    address = models.TextField(verbose_name="آدرس")
    postal_code = models.CharField(max_length=20, verbose_name="کد پستی")
    tracking_code = models.CharField(max_length=100, null=True, blank=True, verbose_name="کد رهگیری")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="وضعیت")

    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_gift_orders", verbose_name="مسئول پیگیری")

    internal_note = models.TextField(null=True, blank=True, verbose_name="یادداشت داخلی")

    idempotency_key = models.CharField(max_length=64, null=True, blank=True, db_index=True, verbose_name="کلید یکتایی درخواست")

    class Meta:
        db_table = "gift_order"
        verbose_name = "سفارش"
        verbose_name_plural = "سفارشات"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["user"]),
            models.Index(fields=["-created_at"]),
        ]
        constraints = [
        # جلوگیری از ثبت دو سفارش با یک کلید برای یک کاربر
               models.UniqueConstraint(
                    fields=["user", "idempotency_key"],
                    condition=models.Q(idempotency_key__isnull=False),
                    name="uniq_gift_order_idempotency_per_user",
               ),
          ]
                    

    def __str__(self):
        return f"Order #{self.id} - {self.gift.title} ({self.get_status_display()})"

    @property
    def status_display(self):
        return self.get_status_display()


class GiftOrderLog(BaseModel):
    # بدون تغییر
    order = models.ForeignKey(GiftOrder, on_delete=models.CASCADE, related_name="logs", verbose_name="سفارش")
    from_status = models.CharField(max_length=20, null=True, blank=True, verbose_name="از وضعیت")
    to_status = models.CharField(max_length=20, null=True, blank=True, verbose_name="به وضعیت")
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="gift_order_logs", verbose_name="توسط")
    action = models.CharField(max_length=50, default="status_change", verbose_name="عملیات")
    note = models.TextField(null=True, blank=True, verbose_name="توضیح")

    class Meta:
        db_table = "gift_order_log"
        verbose_name = "لاگ سفارش"
        verbose_name_plural = "لاگ سفارشات"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order", "-created_at"]),
        ]

    def __str__(self):
        return f"Log #{self.id} - Order #{self.order_id} - {self.action}"