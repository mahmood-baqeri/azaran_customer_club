# Path: applications/faq/repositories.py

# applications/faq/repositories.py

import logging

from django.db import transaction

from .models import Answer, Category, FAQ

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CATEGORY — Store
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def category__store(cleaned, item=None):
    if item is None:
        item = Category(
            title=cleaned["title"],
            is_active=cleaned["is_active"],
        )
    else:
        item.title = cleaned["title"]
        item.is_active = cleaned["is_active"]

    item.save()
    return item


# ═══════════════════════════════════════════════════════════
# CATEGORY — Delete
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def category__delete(category_id):
    item = Category.objects.select_for_update().filter(id=category_id).first()
    if not item:
        raise ValueError("دسته‌بندی یافت نشد")

    faqs_count = item.faqs.count()
    if faqs_count > 0:
        raise ValueError(
            f"این دسته‌بندی {faqs_count} پرسش دارد و قابل حذف نیست"
        )

    item.delete()


# ═══════════════════════════════════════════════════════════
# CATEGORY — Toggle active
# ═══════════════════════════════════════════════════════════
def category__toggle_active(category_id):
    item = Category.objects.filter(id=category_id).first()
    if not item:
        raise ValueError("دسته‌بندی یافت نشد")
    item.is_active = not item.is_active
    item.save(update_fields=["is_active", "updated_at"])
    return item.is_active


# ═══════════════════════════════════════════════════════════
# FAQ — Toggle active (تأیید/رد پرسش)
# ═══════════════════════════════════════════════════════════
def faq__toggle_active(faq_id):
    item = FAQ.objects.filter(id=faq_id).first()
    if not item:
        raise ValueError("پرسش یافت نشد")
    item.is_active = not item.is_active
    item.save(update_fields=["is_active", "updated_at"])
    return item.is_active


# ═══════════════════════════════════════════════════════════
# FAQ — Delete
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def faq__delete(faq_id):
    item = FAQ.objects.select_for_update().filter(id=faq_id).first()
    if not item:
        raise ValueError("پرسش یافت نشد")
    item.delete()


# ═══════════════════════════════════════════════════════════
# ANSWER — Store (create by admin)
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def answer__store(cleaned, faq_id, user, item=None):
    faq = FAQ.objects.filter(id=faq_id).first()
    if not faq:
        raise ValueError("پرسش یافت نشد")

    if item is None:
        item = Answer(
            faq=faq,
            user=user,
            answer=cleaned["answer"],
            is_active=cleaned["is_active"],
        )
    else:
        item.answer = cleaned["answer"]
        item.is_active = cleaned["is_active"]

    item.save()
    return item


# ═══════════════════════════════════════════════════════════
# ANSWER — Toggle active
# ═══════════════════════════════════════════════════════════
def answer__toggle_active(answer_id):
    item = Answer.objects.filter(id=answer_id).first()
    if not item:
        raise ValueError("پاسخ یافت نشد")
    item.is_active = not item.is_active
    item.save(update_fields=["is_active", "updated_at"])
    return item.is_active


# ═══════════════════════════════════════════════════════════
# ANSWER — Delete
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def answer__delete(answer_id):
    item = Answer.objects.select_for_update().filter(id=answer_id).first()
    if not item:
        raise ValueError("پاسخ یافت نشد")
    item.delete()