# Path: applications/review/clean_data.py

# applications/review/clean_data.py

from .models import ReviewQuestion


# ═══════════════════════════════════════════════════════════
# QUESTION
# ═══════════════════════════════════════════════════════════
def question__clean__data(post, current_question=None):
    """اعتبارسنجی فرم سوال نظرسنجی."""
    errors = []

    question_text = (post.get("question") or "").strip()
    if not question_text:
        errors.append("متن سوال الزامی است")
    elif len(question_text) > 255:
        errors.append("متن سوال حداکثر ۲۵۵ کاراکتر است")
    else:
        # چک تکراری بودن (اختیاری — فقط برای هشدار)
        qs = ReviewQuestion.objects.filter(question=question_text)
        if current_question is not None:
            qs = qs.exclude(pk=current_question.pk)
        if qs.exists():
            errors.append("سوالی با همین متن قبلاً ثبت شده است")

    is_active = str(post.get("is_active", "")).lower() in ("on", "true", "1")

    if errors:
        return {}, errors

    return {
        "question": question_text,
        "is_active": is_active,
    }, []