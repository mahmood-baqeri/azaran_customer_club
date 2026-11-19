# Path: applications/gallery/repositories.py

# applications/gallery/repositories.py

import logging

from django.db import transaction

from applications.core.fileManager import deleteFile

from .models import Gallery

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# GALLERY — Store
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def gallery__store(cleaned, item=None):
    """ذخیره/به‌روزرسانی پست گالری. photo فقط اگر جدید داده شد جایگزین می‌شود."""
    if not cleaned:
        raise ValueError("cleaned data required")

    if item is None:
        item = Gallery(
            user=cleaned["user"],
            caption=cleaned.get("caption"),
            location=cleaned.get("location"),
            status=Gallery.Status.PENDING,
        )
    else:
        item.caption = cleaned.get("caption")
        item.location = cleaned.get("location")

    new_photo = cleaned.get("photo")
    if new_photo:
        # حذف فایل قبلی
        if item.pk and item.photo:
            old_name = item.photo.name
            try:
                deleteFile(old_name)
            except Exception:
                logger.warning(
                    "Could not delete old photo %s for gallery %s", old_name, item.pk
                )
        item.photo = new_photo

    item.save()
    return item


# ═══════════════════════════════════════════════════════════
# GALLERY — Approve
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def gallery__approve(gallery_id):
    item = Gallery.objects.select_for_update().filter(id=gallery_id).first()
    if not item:
        raise ValueError("پست گالری یافت نشد")
    if item.status == Gallery.Status.APPROVED:
        raise ValueError("این پست قبلاً تأیید شده است")

    item.status = Gallery.Status.APPROVED
    item.save(update_fields=["status", "updated_at"])
    return item


# ═══════════════════════════════════════════════════════════
# GALLERY — Reject
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def gallery__reject(gallery_id):
    item = Gallery.objects.select_for_update().filter(id=gallery_id).first()
    if not item:
        raise ValueError("پست گالری یافت نشد")
    if item.status == Gallery.Status.REJECTED:
        raise ValueError("این پست قبلاً رد شده است")

    item.status = Gallery.Status.REJECTED
    item.save(update_fields=["status", "updated_at"])
    return item


# ═══════════════════════════════════════════════════════════
# GALLERY — Delete
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def gallery__delete(gallery_id):
    item = Gallery.objects.select_for_update().filter(id=gallery_id).first()
    if not item:
        raise ValueError("پست گالری یافت نشد")

    if item.photo:
        try:
            deleteFile(item.photo.name)
        except Exception:
            logger.warning(
                "Could not delete photo %s for gallery %s", item.photo.name, item.pk
            )

    item.delete()