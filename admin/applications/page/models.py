# django/applications/page/models.py

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from applications.category.models import Category
from applications.core.fileManager import ImageProcessingMixin
from applications.core.baseModel import SoftDeleteModel

        
#######################################
#  Page 
#######################################
class Page(ImageProcessingMixin, SoftDeleteModel):
    class PageType(models.TextChoices):
        PAGE = 'Page', 'صفحه عادی'
        ARTICLE = 'Article', 'مقاله'
        NEWS = 'News', 'خبر'
        SERVICE = 'Service', 'خدمات'

    # ========== دسته‌بندی ==========
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="pages", null=True, blank=True, verbose_name="دسته‌بندی")

    # ========== فیلدهای اصلی ==========
    title = models.CharField(max_length=120, verbose_name="عنوان صفحه", help_text="عنوان صفحه (اجباری)")
    summer = models.TextField(verbose_name="متن کوتاه", help_text="متن کوتاه برای نمایش در کارت‌ها", blank=True, null=True)
    text = models.TextField(verbose_name="متن اصلی", help_text="محتوای اصلی صفحه", blank=True, null=True)
    slug = models.SlugField(max_length=150, unique=True, allow_unicode=True, blank=True, editable=False, verbose_name="اسلاگ", help_text="به‌صورت خودکار از عنوان ساخته می‌شود")
    type = models.CharField(max_length=20, choices=PageType.choices, default=PageType.PAGE, db_index=True, verbose_name="نوع صفحه")

    # ========== تصاویر ==========
    photo = models.ImageField(upload_to='pages/', null=True, blank=True, verbose_name="تصویر صفحه")
    gallery = models.JSONField(default=list, blank=True, verbose_name="گالری تصاویر")

    # ========== وضعیت ==========
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")

    class Meta:
        db_table = "page"
        verbose_name = "صفحه"
        verbose_name_plural = "صفحات"
        ordering = ["-id"]
        indexes = [
            # فیلترهای پرکاربرد
            models.Index(fields=["type", "is_active"], name="page_type_active_idx"),
            models.Index(fields=["category", "is_active"], name="page_cat_active_idx"),
            models.Index(fields=["is_active", "-id"], name="page_active_recent_idx"),
        ]

    # ---------------------------------------------------------------
    # نمایش
    # ---------------------------------------------------------------
    def __str__(self):
        return self.title or self.slug or f"Page #{self.pk}"

    # ---------------------------------------------------------------
    # ساخت خودکار اسلاگ
    # ---------------------------------------------------------------
    def _generate_slug(self) -> str:
        """
        اسلاگ یکتا از عنوان می‌سازد.
        اگر عنوان خالی یا غیرقابل تبدیل بود، از uuid کوتاه استفاده می‌کند.
        """
        base = (self.title or "").strip()
        candidate = slugify(base, allow_unicode=True) if base else ""

        if not candidate:
            candidate = f"page-{uuid.uuid4().hex[:8]}"

        # اطمینان از یکتایی
        model = type(self)
        original = candidate
        suffix = 1
        while model.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
            candidate = f"{original}-{suffix}"
            suffix += 1
            if suffix > 1000:  # گارد ایمنی
                candidate = f"{original}-{uuid.uuid4().hex[:6]}"
                break

        return candidate

    # ---------------------------------------------------------------
    # save
    # ---------------------------------------------------------------
    def save(self, *args, **kwargs):
        # اگر slug خالی است یا صریحاً درخواست بازتولید شده
        regenerate = getattr(self, "_regenerate_slug", False)
        if not self.slug or regenerate:
            self.slug = self._generate_slug()
            self._regenerate_slug = False

        super().save(*args, **kwargs)

    def regenerate_slug(self, save: bool = True) -> str:
        """برای بازتولید دستی اسلاگ (مثلاً از ادمین)."""
        self.slug = self._generate_slug()
        if save:
            # برای اینکه save دوباره slug نسازد
            self._regenerate_slug = False
            self.save(update_fields=["slug"])
        return self.slug


#######################################
#  Page Content Item
#######################################
class PageContentItem(models.Model):
    class Kind(models.TextChoices):
        STEP = "step", "Step"
        FAQ = "faq", "FAQ"

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="content_items", verbose_name="صفحه")
    title = models.CharField(max_length=255, verbose_name="عنوان")
    body = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    kind = models.CharField(max_length=32, choices=Kind.choices, db_index=True, verbose_name="نوع آیتم")
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب")
    extra = models.JSONField(default=dict, blank=True, verbose_name="داده‌های اضافی")

    class Meta:
        db_table = "page_content_item"
        verbose_name = "آیتم محتوا"
        verbose_name_plural = "آیتم‌های محتوا"
        ordering = ["kind", "order", "pk"]
        indexes = [
            models.Index(fields=["page", "kind"], name="pci_page_kind_idx"),
            models.Index(fields=["page", "kind", "order"], name="pci_page_kind_order_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["page", "kind", "order"],
                name="uniq_page_kind_order",
            ),
        ]

    def __str__(self):
        return f"{self.page_id} - {self.kind} - {self.title[:50]}"