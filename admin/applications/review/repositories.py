# Path: applications/review/repositories.py

# applications/review/repositories.py

import logging

from django.db import transaction

from .models import ReviewAnswer, ReviewQuestion

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# QUESTION — Store
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def question__store(cleaned, item=None):
    if item is None:
        item = ReviewQuestion(
            question=cleaned["question"],
            is_active=cleaned["is_active"],
        )
    else:
        item.question = cleaned["question"]
        item.is_active = cleaned["is_active"]

    item.save()
    return item


# ═══════════════════════════════════════════════════════════
# QUESTION — Delete
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def question__delete(question_id):
    item = ReviewQuestion.objects.select_for_update().filter(id=question_id).first()
    if not item:
        raise ValueError("سوال یافت نشد")

    answers_count = item.answers.count()
    if answers_count > 0:
        raise ValueError(
            f"این سوال {answers_count} پاسخ ثبت‌شده دارد و قابل حذف نیست. "
            f"ابتدا پاسخ‌ها را حذف کنید یا سوال را غیرفعال کنید."
        )

    item.delete()


# ═══════════════════════════════════════════════════════════
# QUESTION — Toggle active
# ═══════════════════════════════════════════════════════════
def question__toggle_active(question_id):
    item = ReviewQuestion.objects.filter(id=question_id).first()
    if not item:
        raise ValueError("سوال یافت نشد")
    item.is_active = not item.is_active
    item.save(update_fields=["is_active", "updated_at"])
    return item.is_active


# ═══════════════════════════════════════════════════════════
# ANSWER — Delete (ادمین اجازه‌ی تجدید نظر می‌دهد)
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def answer__delete(answer_id):
    item = ReviewAnswer.objects.select_for_update().filter(id=answer_id).first()
    if not item:
        raise ValueError("پاسخ یافت نشد")
    item.delete()