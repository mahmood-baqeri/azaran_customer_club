"""
Endpointهای score.
فقط خواندن + عملیات ادمین.
هیچ endpointی اینجا امتیاز مستقیم نمی‌دهد (به جز ADMIN_ADJUST).
"""
from typing import Optional

from channels.db import database_sync_to_async
from fastapi import APIRouter, Depends, Query

from applications.score import api as score_api
from applications.score.models import ScoreRule, UserScoreLog
from applications.score.services import ScoreError
from applications.user.models import User
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.response import error_response, success_response
from app_fastapi.views.user.user_helper import get_current_user

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
    code: Optional[str] = Query(None),
    direction: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
):
    data = await database_sync_to_async(_list_logs)(
        user.id, code, direction, page, page_size,
    )
    return success_response("تاریخچه امتیازات", data)


def _list_logs(user_id, code, direction, page, page_size):
    from django.core.paginator import Paginator

    qs = UserScoreLog.objects.filter(user_id=user_id).order_by("-created_at")
    if code:
        qs = qs.filter(transaction_code=code)
    if direction:
        qs = qs.filter(direction=direction)

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


# ═══════════════════════════════════════════════════════════
# ادمین — تنها endpointهایی که امتیاز تغییر می‌دهند
# ═══════════════════════════════════════════════════════════
def _require_admin(user: User):
    if not (user.is_staff or user.is_superuser):
        raise PermissionError("دسترسی ادمین لازم است")


@router.post("/admin/adjust/")
async def admin_adjust(
    form: dict = Depends(DependencyDataRequest),
    admin: User = Depends(get_current_user),
):
    try:
        _require_admin(admin)
        target = await database_sync_to_async(
            lambda: User.objects.filter(uuid=form.get("user_uuid")).first()
        )()
        if not target:
            return error_response("کاربر یافت نشد", status_code=404)

        direction = form.get("direction")
        if direction not in ("earned", "spent"):
            return error_response("direction باید earned یا spent باشد")

        log = await database_sync_to_async(score_api.adjust)(
            target,
            int(form.get("amount", 0)),
            direction,
            admin=admin,
            reason=form.get("reason") or "تنظیم دستی",
            extra={"admin_name": admin.full_name},
        )
        return success_response("امتیاز تنظیم شد", _log(log))
    except PermissionError as e:
        return error_response(str(e), status_code=403)
    except ScoreError as e:
        return error_response(str(e))


@router.post("/admin/refund/{log_id}/")
async def admin_refund(
    log_id: int,
    form: dict = Depends(DependencyDataRequest),
    admin: User = Depends(get_current_user),
):
    try:
        _require_admin(admin)
        log = await database_sync_to_async(score_api.refund)(
            log_id,
            reason=form.get("reason") or "برگشت توسط ادمین",
            created_by=admin,
        )
        return success_response("تراکنش برگشت خورد", _log(log))
    except PermissionError as e:
        return error_response(str(e), status_code=403)
    except ScoreError as e:
        return error_response(str(e))