# app_fastapi/views/faq.py

from typing import Optional
from fastapi import APIRouter, Depends
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.db.models import Count, Q

from applications.faq.models import Category, FAQ, Answer, AnswerReaction
from applications.user.models import User
from app_fastapi.views.user.user_helper import get_current_user
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.response import success_response, error_response

router = APIRouter()


# =========================================================
# Serializers
# =========================================================
def category_serialize(c: Category) -> dict:
    return {"id": c.id, "title": c.title}


def answer_serialize(a: Answer, current_user_id: int) -> dict:
    # شمارش لایک و دیس‌لایک
    likes = a.reactions.filter(reaction=AnswerReaction.ReactionType.LIKE).count()
    dislikes = a.reactions.filter(reaction=AnswerReaction.ReactionType.DISLIKE).count()
    
    # واکنش فعلی این کاربر
    user_reaction = a.reactions.filter(user_id=current_user_id).first()
    my_reaction = user_reaction.reaction if user_reaction else None

    return {
        "id": a.id,
        "answer": a.answer,
        "likes_count": likes,
        "dislikes_count": dislikes,
        "my_reaction": my_reaction, # "like", "dislike" یا None
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "user": {
            "id": a.user.id if a.user else None,
            "name": a.user.full_name if a.user else "پشتیبانی",
        }
    }


def faq_serialize(f: FAQ, current_user_id: int, include_answers: bool = False) -> dict:
    data = {
        "id": f.id,
        "question": f.question,
        "created_at": f.created_at.isoformat() if f.created_at else None,
        "category": {
            "id": f.category_id,
            "title": f.category.title
        },
        "user": {
            "id": f.user_id,
            "name": f.user.full_name,
            "avatar": f.user.avatar.url if f.user.avatar else None,
        },
        "answers_count": f.answers.count()
    }
    if include_answers:
        data["answers"] = [
            answer_serialize(a, current_user_id) 
            for a in f.answers.filter(is_active=True).order_by("created_at")
        ]
    return data


# =========================================================
# CATEGORIES
# =========================================================
@router.get("/categories/")
async def list_categories():
    try:
        items = await async_list_categories()
        return success_response("لیست دسته‌بندی‌ها", items)
    except Exception as e:
        return error_response(str(e), 203)

@database_sync_to_async
def async_list_categories():
    qs = Category.objects.filter(is_active=True)
    return [category_serialize(c) for c in qs]


# =========================================================
# FAQS (سوالات)
# =========================================================
@router.get("/")
async def list_faqs(
    category_id: Optional[int] = None,
    sort: Optional[str] = "newest", # ✅ پارامتر جدید
    user: User = Depends(get_current_user),
):
    try:
        items = await async_list_faqs(category_id, sort, user.id)
        return success_response("لیست پرسش‌ها", items)
    except Exception as e:
        return error_response(str(e), 203)

@database_sync_to_async
def async_list_faqs(category_id, sort, user_id):
    # استفاده از prefetch_related برای جلوگیری از کوئری اضافی در حلقه
    qs = FAQ.objects.filter(is_active=True).select_related("category", "user").prefetch_related("answers")
    
    # ۱. فیلتر دسته‌بندی
    if category_id:
        qs = qs.filter(category_id=category_id)
    
    # ۲. اعمال مرتب‌سازی (فیلتر) درخواستی
    if sort == "most_answered":
        # annotate برای شمارش پاسخ‌ها در سطح دیتابیس (بهینه و سریع)
        qs = qs.annotate(answers_num=Count('answers')).order_by("-answers_num", "-created_at")
    elif sort == "my_questions":
        # فقط سوالاتی که خود کاربر پرسیده است
        qs = qs.filter(user_id=user_id).order_by("-created_at")
    else: 
        # پیش‌فرض: جدیدترین‌ها (newest)
        qs = qs.order_by("-created_at")
    
    return [faq_serialize(f, user_id) for f in qs]


@router.get("/{faq_id}/")
async def get_faq_detail(
    faq_id: int,
    user: User = Depends(get_current_user),
):
    try:
        item = await async_get_faq(faq_id, user.id)
        if not item:
            return error_response("پرسش یافت نشد", 404)
        return success_response("جزئیات پرسش", item)
    except Exception as e:
        return error_response(str(e), 203)

@database_sync_to_async
def async_get_faq(faq_id, user_id):
    f = FAQ.objects.filter(id=faq_id, is_active=True).select_related("category", "user").first()
    if not f:
        return None
    return faq_serialize(f, user_id, include_answers=True)


@router.post("/")
async def create_faq(
    form: dict = Depends(DependencyDataRequest),
    user: User = Depends(get_current_user),
):
    question = form.get("question")
    category_id = form.get("category_id")

    if not question or not category_id:
        return error_response("سوال و دسته‌بندی الزامی است", 203)

    try:
        result = await async_create_faq(user.id, category_id, question)
        if result.get("error"):
            return error_response(result["error"], 203)
        return success_response("پرسش با موفقیت ثبت شد", result["faq"])
    except Exception as e:
        return error_response(str(e), 203)

@sync_to_async
def async_create_faq(user_id, category_id, question):
    category = Category.objects.filter(id=category_id, is_active=True).first()
    if not category:
        return {"error": "دسته‌بندی یافت نشد"}
        
    f = FAQ.objects.create(
        user_id=user_id,
        category=category,
        question=question.strip()
    )
    return {"faq": faq_serialize(f, user_id)}


# =========================================================
# ANSWERS (پاسخ‌ها)
# =========================================================
@router.post("/{faq_id}/answers/")
async def create_answer(
    faq_id: int,
    form: dict = Depends(DependencyDataRequest),
    user: User = Depends(get_current_user),
):
    answer_text = form.get("answer")
    if not answer_text:
        return error_response("متن پاسخ الزامی است", 203)

    try:
        result = await async_create_answer(faq_id, user.id, answer_text)
        if result.get("error"):
            return error_response(result["error"], 203)
        return success_response("پاسخ با موفقیت ثبت شد", result["answer"])
    except Exception as e:
        return error_response(str(e), 203)

@sync_to_async
def async_create_answer(faq_id, user_id, answer_text):
    faq = FAQ.objects.filter(id=faq_id, is_active=True).first()
    if not faq:
        return {"error": "پرسش یافت نشد"}

    a = Answer.objects.create(
        faq=faq,
        user_id=user_id,
        answer=answer_text.strip()
    )
    return {"answer": answer_serialize(a, user_id)}


# =========================================================
# REACTIONS (لایک و دیس‌لایک)
# =========================================================
@router.post("/answers/{answer_id}/react/")
async def react_to_answer(
    answer_id: int,
    form: dict = Depends(DependencyDataRequest),
    user: User = Depends(get_current_user),
):
    reaction_type = form.get("reaction") # "like" یا "dislike" یا None (برای حذف)
    
    if reaction_type not in ["like", "dislike", None]:
        return error_response("نوع واکنش نامعتبر است", 203)

    try:
        result = await async_react_to_answer(answer_id, user.id, reaction_type)
        if result.get("error"):
            return error_response(result["error"], 203)
        return success_response("واکنش شما ثبت شد", result["answer"])
    except Exception as e:
        return error_response(str(e), 203)

@sync_to_async
def async_react_to_answer(answer_id, user_id, reaction_type):
    answer = Answer.objects.filter(id=answer_id, is_active=True).first()
    if not answer:
        return {"error": "پاسخ یافت نشد"}

    existing = AnswerReaction.objects.filter(answer=answer, user_id=user_id).first()

    if existing:
        if reaction_type is None:
            # حذف واکنش
            existing.delete()
        elif existing.reaction == reaction_type:
            # اگر روی همان دکمه کلیک کرد، واکنش حذف می‌شود (Toggle)
            existing.delete()
        else:
            # تغییر از لایک به دیس‌لایک یا برعکس
            existing.reaction = reaction_type
            existing.save(update_fields=["reaction"])
    else:
        if reaction_type is not None:
            # ثبت واکنش جدید
            AnswerReaction.objects.create(
                answer=answer,
                user_id=user_id,
                reaction=reaction_type
            )

    return {"answer": answer_serialize(answer, user_id)}