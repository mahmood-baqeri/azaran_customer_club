# app_fastapi/views/review/review.py

import logging
from asgiref.sync import sync_to_async
from fastapi import APIRouter, Depends
from django.db import transaction

from applications.review.models import ReviewQuestion, ReviewAnswer
from applications.user.models import User
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.response import error_response, success_response
from app_fastapi.views.user.helper import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


# ═══════════════════════════════════════════════════════════
# ۱. لیست سوالات فعال
# ═══════════════════════════════════════════════════════════
@router.get("/questions/")
async def list_active_questions(user: User = Depends(get_current_user)):
    # ✅ فراخوانی مستقیم تابع تزئین‌شده
    data = await _get_questions(user.id)
    return success_response("لیست سوالات نظرسنجی", data)


@sync_to_async
def _get_questions(user_id: int):
    questions = ReviewQuestion.objects.filter(is_active=True).order_by('created_at')
    
    answered_question_ids = set(
        ReviewAnswer.objects.filter(user_id=user_id).values_list('question_id', flat=True)
    )
    
    return [
        {
            "id": q.id,
            "question": q.question,
            "is_answered": q.id in answered_question_ids
        }
        for q in questions
    ]


# ═══════════════════════════════════════════════════════════
# ۲. ثبت پاسخ‌ها (با نادیده گرفتن پاسخ‌های تکراری)
# ═══════════════════════════════════════════════════════════
@router.post("/submit/")
async def submit_answers(
    form: dict = Depends(DependencyDataRequest),
    user: User = Depends(get_current_user),
):
    answers_data = form.get("answers")
    
    if not answers_data or not isinstance(answers_data, list):
        return error_response("داده‌های ارسالی نامعتبر است")

    try:
        # ✅ اجرای منطق دیتابیس در thread pool
        result = await _submit_answers_db(user.id, answers_data)
        if result.get("error"):
            return error_response(result["error"], status_code=400)
            
        return success_response(result.get("message", "پاسخ‌های شما با موفقیت ثبت شد"), {})
    except Exception:
        logger.exception("submit_answers failed")
        return error_response("خطا در ثبت پاسخ‌ها")


@sync_to_async
def _submit_answers_db(user_id: int, answers_data: list):
    with transaction.atomic():
        valid_answers = []
        
        q_ids = [item.get("question_id") for item in answers_data if item.get("question_id")]
        if not q_ids:
            return {"error": "هیچ سوالی ارسال نشده است"}

        # ۱. پیدا کردن سوالاتی که کاربر قبلاً به آن‌ها جواب داده است
        already_answered = set(
            ReviewAnswer.objects.filter(
                user_id=user_id, 
                question_id__in=q_ids
            ).values_list('question_id', flat=True)
        )
        
        # ۲. اعتبارسنجی و فیلتر کردن سوالات جدید
        for item in answers_data:
            q_id = item.get("question_id")
            ans = item.get("answer")
            
            if not q_id or not ans:
                continue
                
            # 👈 اگر قبلاً به این سوال جواب داده، از آن رد شو (نادیده بگیر)
            if q_id in already_answered:
                continue
                
            # بررسی فعال بودن سوال
            if not ReviewQuestion.objects.filter(id=q_id, is_active=True).exists():
                return {"error": f"سوال با شناسه {q_id} یافت نشد یا غیرفعال است"}
                
            if ans not in ReviewAnswer.AnswerItem.values:
                return {"error": f"پاسخ نامعتبر برای سوال {q_id}"}
                
            valid_answers.append(
                ReviewAnswer(
                    user_id=user_id,
                    question_id=q_id,
                    answer=ans
                )
            )
            
        if not valid_answers:
            return {"message": "تمام سوالات ارسال شده قبلاً پاسخ داده شده بودند."}

        # ۳. درج گروهی فقط پاسخ‌های جدید
        ReviewAnswer.objects.bulk_create(valid_answers)
        
        return {"message": f"تعداد {len(valid_answers)} پاسخ جدید با موفقیت ثبت شد"}