# applications/review/repositories.py

import logging

from django.db import transaction

from applications.core.fileManager import deleteFile

from .models import Learn

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# LEARN — Store
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def learn__store(cleaned, item=None):
    """ذخیره/به‌روزرسانی آموزش. photo فقط اگر جدید داده شد جایگزین می‌شود."""
    if not cleaned:
        raise ValueError("cleaned data required")

    if item is None:
        item = Learn(
            title=cleaned["title"],
            sub_text=cleaned.get("sub_text"),
            caption=cleaned.get("caption"),
            full_text=cleaned["full_text"],
            is_active=cleaned["is_active"],
            size=cleaned["size"],
            time=cleaned.get("time"),
        )
    else:
        item.title = cleaned["title"]
        item.sub_text = cleaned.get("sub_text")
        item.caption = cleaned.get("caption")
        item.full_text = cleaned["full_text"]
        item.is_active = cleaned["is_active"]
        item.size = cleaned["size"]
        item.time = cleaned.get("time")

    new_photo = cleaned.get("photo")
    if new_photo:
        # حذف فایل قبلی در صورت وجود
        if item.pk and item.photo:
            old_name = item.photo.name
            try:
                deleteFile(old_name)
            except Exception:
                logger.warning("Could not delete old photo %s for learn %s", old_name, item.pk)
        item.photo = new_photo

    item.save()
    return item


# ═══════════════════════════════════════════════════════════
# LEARN — Delete
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def learn__delete(learn_id):
    item = Learn.objects.select_for_update().filter(id=learn_id).first()
    if not item:
        raise ValueError("آموزش یافت نشد")

    # حذف فایل تصویر از دیسک
    if item.photo:
        try:
            deleteFile(item.photo.name)
        except Exception:
            logger.warning("Could not delete photo %s for learn %s", item.photo.name, item.pk)

    item.delete()


# ═══════════════════════════════════════════════════════════
# LEARN — Toggle active
# ═══════════════════════════════════════════════════════════
def learn__toggle_active(learn_id):
    item = Learn.objects.filter(id=learn_id).first()
    if not item:
        raise ValueError("آموزش یافت نشد")
    item.is_active = not item.is_active
    item.save(update_fields=["is_active", "updated_at"])
    return item.is_active