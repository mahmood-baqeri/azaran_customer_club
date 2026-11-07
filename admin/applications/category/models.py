import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


class Category(models.Model):
    title = models.CharField(max_length=120, verbose_name="عنوان")
    slug = models.SlugField(max_length=150, unique=True, allow_unicode=True, blank=True, editable=False, verbose_name="اسلاگ")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="children", null=True, blank=True, verbose_name="دسته والد")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="فعال")

    class Meta:
        db_table = "category"
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["title"]
        indexes = [
            models.Index(fields=["is_active", "title"], name="cat_active_title_idx"),
        ]

    def __str__(self):
        return self.title or self.slug or f"Category #{self.pk}"

    # ---------------------------------------------------------------
    def _generate_slug(self) -> str:
        base = (self.title or "").strip()
        candidate = slugify(base, allow_unicode=True) if base else ""

        if not candidate:
            import uuid
            candidate = f"cat-{uuid.uuid4().hex[:8]}"

        model = type(self)
        original = candidate
        suffix = 1
        while model.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
            candidate = f"{original}-{suffix}"
            suffix += 1
            if suffix > 1000:
                import uuid
                candidate = f"{original}-{uuid.uuid4().hex[:6]}"
                break
        return candidate

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_slug()
        super().save(*args, **kwargs)
        