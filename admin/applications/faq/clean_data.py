# applications/faq/clean_data.py

from .models import Category


# ═══════════════════════════════════════════════════════════
# CATEGORY
# ═══════════════════════════════════════════════════════════
def category__clean__data(post, current_category=None):
    errors = []

    title = (post.get("title") or "").strip()
    if not title:
        errors.append("عنوان دسته‌بندی الزامی است")
    elif len(title) > 255:
        errors.append("عنوان حداکثر ۲۵۵ کاراکتر است")
    else:
        qs = Category.objects.filter(title=title)
        if current_category is not None:
            qs = qs.exclude(pk=current_category.pk)
        if qs.exists():
            errors.append("دسته‌بندی‌ای با همین عنوان قبلاً ثبت شده است")

    is_active = str(post.get("is_active", "")).lower() in ("on", "true", "1")

    if errors:
        return {}, errors

    return {"title": title, "is_active": is_active}, []


# ═══════════════════════════════════════════════════════════
# ANSWER
# ═══════════════════════════════════════════════════════════
def answer__clean__data(post, current_answer=None):
    errors = []

    answer_text = (post.get("answer") or "").strip()
    if not answer_text:
        errors.append("متن پاسخ الزامی است")
    elif len(answer_text) > 10000:
        errors.append("متن پاسخ حداکثر ۱۰,۰۰۰ کاراکتر است")

    is_active = str(post.get("is_active", "")).lower() in ("on", "true", "1")

    if errors:
        return {}, errors

    return {"answer": answer_text, "is_active": is_active}, []