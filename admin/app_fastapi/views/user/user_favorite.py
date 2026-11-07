# admin/app_fastapi/views/user/user_favorite.py

from channels.db import database_sync_to_async
from fastapi import APIRouter, Depends

from app_fastapi.views.user.user_helper import get_current_user
from applications.user.models import (
    User, FavoriteQuestion, FavoriteAnswer, FavoriteAnswerItem,
)
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.response import success_response, error_response

router = APIRouter()


# =========================================================
# سریالایزرها
# =========================================================
def favorite_question_serialize(q, user_answer=None):
    return {
        "id": q.id,
        "question": q.question,
        "answer_options": [
            {"value": v, "label": lbl}
            for v, lbl in FavoriteAnswerItem.choices
        ],
        "user_answer": (
            {
                "id": user_answer.id,
                "answer": user_answer.answer,
                "answer_display": user_answer.get_answer_display(),
                "updated_at": (
                    user_answer.updated_at.isoformat()
                    if getattr(user_answer, "updated_at", None)
                    else user_answer.created_at.isoformat()
                    if getattr(user_answer, "created_at", None)
                    else None
                ),
            }
            if user_answer else None
        ),
    }


# =========================================================
# دریافت سوالات علاقه‌مندی
# =========================================================
@router.get("/favorite-questions/")
async def list_favorite_questions(user: User = Depends(get_current_user)):
    data = await async_list_favorite_questions(user)
    return success_response("سوالات علاقه‌مندی", data)


# =========================================================
# ثبت / به‌روزرسانی پاسخ
# =========================================================
@router.post("/favorite-questions/answer/")
async def submit_favorite_answer(
    form: dict = Depends(DependencyDataRequest),
    user: User = Depends(get_current_user),
):
    question_id = form.get("question_id")
    answer = form.get("answer")

    if not question_id:
        return error_response("شناسه سوال الزامی است", status_code=400)

    valid_answers = [c[0] for c in FavoriteAnswerItem.choices]
    if answer not in valid_answers:
        return error_response("پاسخ معتبر نیست", status_code=400)

    obj, err = await async_upsert_favorite_answer(user, int(question_id), answer)
    if err:
        return error_response(err, status_code=404)

    return success_response(
        "ذخیره شد",
        {
            "id": obj.id,
            "question_id": obj.question_id,
            "answer": obj.answer,
            "answer_display": obj.get_answer_display(),
        },
    )


# =========================================================
# توابع کمکی پایگاه داده
# =========================================================
@database_sync_to_async
def async_list_favorite_questions(user):
    questions = list(
        FavoriteQuestion.objects.filter(is_active=True).order_by("id")
    )
    answers = {
        a.question_id: a
        for a in FavoriteAnswer.objects.filter(user=user)
    }
    return [
        favorite_question_serialize(q, answers.get(q.id))
        for q in questions
    ]


@database_sync_to_async
def async_upsert_favorite_answer(user, question_id, answer_value):
    q = FavoriteQuestion.objects.filter(id=question_id, is_active=True).first()
    if not q:
        return None, "سوال یافت نشد"

    obj, _created = FavoriteAnswer.objects.update_or_create(
        user=user, question=q,
        defaults={"answer": answer_value},
    )
    return obj, None