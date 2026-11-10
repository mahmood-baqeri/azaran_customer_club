from typing import Optional
from datetime import datetime
from typing import Optional
from django.core.paginator import Paginator
from channels.db import database_sync_to_async
from fastapi import APIRouter, Depends, Query
from datetime import datetime, time
from django.utils import timezone
from applications.score import api as score_api
from applications.score.models import ScoreRule, UserScoreLog
from applications.score.services import ScoreError
from applications.user.models import User
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.response import error_response, success_response
from app_fastapi.views.user.helper import get_current_user

router = APIRouter()


# ─────────────────────────────────────────────
# Serializers
# ─────────────────────────────────────────────
def _log(log: UserScoreLog) -> dict:
    return {
        "id": log.id,
        "code": log.transaction_code,
        "code_display": log.get_transaction_code_display(),
        "direction": log.direction,
        "amount": log.amount,
        "balance_before": log.balance_before,
        "balance_after": log.balance_after,
        "reference_type": log.reference_type,
        "reference_id": log.reference_id,
        "reason": log.reason,
        "extra_data": log.extra_data,
        "is_reversed": log.is_reversed,
        "created_at": log.created_at.isoformat() if log.created_at else None,
    }


def _rule(rule: ScoreRule) -> dict:
    return {
        "code": rule.code,
        "code_display": rule.get_code_display(),
        "calc_type": rule.calc_type,
        "default_amount": rule.default_amount,
        "cap_period": rule.cap_period,
        "cap_count": rule.cap_count,
    }


# ═══════════════════════════════════════════════════════════
# خواندن — کاربر
# ═══════════════════════════════════════════════════════════
@router.get("/balance/")
async def balance(user: User = Depends(get_current_user)):
    data = await database_sync_to_async(score_api.get_balance)(user)
    return success_response("موجودی امتیاز", data)


@router.get("/logs/")
async def logs(
    code: Optional[str] = Query(None, description="فیلتر بر اساس کد تراکنش"),
    direction: Optional[str] = Query(None, description="جهت تراکنش: earned (کسب) یا spent (خرج)"),
    start_date: Optional[str] = Query(None, description="تاریخ شروع (فرمت: YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="تاریخ پایان (فرمت: YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
):
    data = await database_sync_to_async(_list_logs)(
        user.id, code, direction, start_date, end_date, page, page_size,
    )
    return success_response("تاریخچه امتیازات", data)



def _list_logs(user_id, code, direction, start_date, end_date, page, page_size):
    qs = UserScoreLog.objects.filter(user_id=user_id).order_by("-created_at")

    # ۱. فیلتر کد تراکنش
    if code:
        qs = qs.filter(transaction_code=code)
        
    # ۲. فیلتر جهت (کسب/خرج)
    if direction and direction in UserScoreLog.Direction.values:
        qs = qs.filter(direction=direction)

    # ۳. فیلتر محدوده تاریخ (نسخه ضدضربه)
    try:
        if start_date:
            parsed_start = datetime.strptime(start_date[:10], "%Y-%m-%d").date()
            # شروع روز (00:00:00)
            start_datetime = timezone.make_aware(datetime.combine(parsed_start, time.min))
            qs = qs.filter(created_at__gte=start_datetime)
            
        if end_date:
            parsed_end = datetime.strptime(end_date[:10], "%Y-%m-%d").date()
            # پایان روز (23:59:59)
            end_datetime = timezone.make_aware(datetime.combine(parsed_end, time.max))
            qs = qs.filter(created_at__lte=end_datetime)
    except ValueError:
        pass

    # صفحه‌بندی
    p = Paginator(qs, page_size)
    page_obj = p.get_page(page)
    
    return {
        "total": p.count,
        "page": page,
        "page_size": page_size,
        "items": [_log(x) for x in page_obj],
    }
    


@router.get("/rules/")
async def rules(user: User = Depends(get_current_user)):
    data = await database_sync_to_async(_all_rules)()
    return success_response("قواعد امتیاز", data)


def _all_rules():
    return [_rule(r) for r in ScoreRule.objects.filter(is_active=True).order_by("code")]


@router.get("/progress/")
async def progress(user: User = Depends(get_current_user)):
    data = await database_sync_to_async(score_api.get_daily_progress)(user)
    return success_response("پیشرفت امروز", data)


@router.get("/can-do/{code}/")
async def can_do(code: str, user: User = Depends(get_current_user)):
    allowed, msg = await database_sync_to_async(score_api.can_do)(user, code)
    return success_response(msg or "مجاز", {"allowed": allowed, "message": msg})


@router.get("/leaderboard/")
async def leaderboard(
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
):
    data = await database_sync_to_async(_leaderboard)(limit)
    return success_response("جدول امتیازات", data)


def _leaderboard(limit):
    from applications.score.models import UserScore
    qs = UserScore.objects.select_related("user").order_by("-current_balance")[:limit]
    return [
        {
            "rank": i + 1,
            "user_uuid": str(s.user.uuid),
            "name": s.user.full_name,
            "avatar": s.user.avatar.url if s.user.avatar else None,
            "current_balance": s.current_balance,
        }
        for i, s in enumerate(qs)
    ]



