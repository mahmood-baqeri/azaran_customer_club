# applications/promotion/models.py

from django.db import models
from applications.core.baseModel import BaseModel
from applications.user.models import User

class Promotion(BaseModel): 
    title = models.CharField(max_length=200, verbose_name="عنوان")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        db_table = "promotion_promotion"                      
        verbose_name = "پک اقلام تبلیغاتی"             
        ordering = ["-created_at"]


    def __str__(self):
        return self.title


class PromotionItem(BaseModel): 
    promotion = models.ForeignKey(Promotion, on_delete=models.PROTECT, related_name="promotion_items_relation")
    title = models.CharField(max_length=200, verbose_name="عنوان")
    badge = models.CharField(max_length=200, null=True, blank=True, verbose_name="برچسب")
    photo = models.ImageField(upload_to="promotions/", null=True, blank=True, verbose_name="تصویر")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        db_table = "promotion_promotion_items"
        verbose_name = "آیتم اقلام تبلیغاتی"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} (پک {self.promotion.title})"


class PromotionOrder(BaseModel):
    class Status(models.TextChoices):        
        PENDING = "pending", "ثبت سفارش"
        APPROVED = "approved", "تایید سفارش"
        SHIPPED = "shipped", "تحویل به پست"
        DELIVERED = "delivered", "تحویل به مشتری"
        REJECTED = "rejected", "رد شده"
        CANCELLED = "cancelled", "لغو شده"
        RETURNED = "returned", "مرجوع شده"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_promotion_orders_relation", verbose_name="کاربر")
    promotion = models.ForeignKey(Promotion, on_delete=models.PROTECT, related_name="promotion_orders_relation", verbose_name="اقلام تبلیغاتی")
    
    # اطلاعات گیرنده
    receiver_name = models.CharField(max_length=150, verbose_name="نام گیرنده")
    receiver_phone = models.CharField(max_length=20, verbose_name="تلفن گیرنده")
    address = models.TextField(verbose_name="آدرس")
    postal_code = models.CharField(max_length=20, verbose_name="کد پستی")
    tracking_code = models.CharField(max_length=100, null=True, blank=True, verbose_name="کد رهگیری")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="وضعیت")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_promotion_orders", verbose_name="مسئول پیگیری")

    idempotency_key = models.CharField(max_length=64, null=True, blank=True, db_index=True, verbose_name="کلید یکتایی درخواست")

    class Meta:
        db_table = "promotion_order"
        verbose_name = "سفارش اقلام تبلیغاتی"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "idempotency_key"],
                condition=models.Q(idempotency_key__isnull=False),
                name="uniq_promotion_order_idempotency_per_user",
            ),
            # ✅ جدید: هر کاربر فقط یک سفارش برای هر پک
            models.UniqueConstraint(
                fields=["user", "promotion"],
                name="uniq_promotion_order_per_user_promotion",
            ),
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.promotion.title} ({self.get_status_display()})"

    @property
    def status_display(self):
        return self.get_status_display()


class PromotionalOrderLog(BaseModel):
    order = models.ForeignKey(PromotionOrder, on_delete=models.CASCADE, related_name="promotion_logs_relation", verbose_name="سفارش")
    from_status = models.CharField(max_length=20, null=True, blank=True, verbose_name="از وضعیت")
    to_status = models.CharField(max_length=20, null=True, blank=True, verbose_name="به وضعیت")
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="promotion_order_logs", verbose_name="توسط")
    action = models.CharField(max_length=50, default="status_change", verbose_name="عملیات")
    note = models.TextField(null=True, blank=True, verbose_name="توضیح")

    class Meta:
        db_table = "promotion_order_log"
        verbose_name = "لاگ سفارش اقلام تبلیغاتی"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Log #{self.id} - Order #{self.order_id} - {self.action}"