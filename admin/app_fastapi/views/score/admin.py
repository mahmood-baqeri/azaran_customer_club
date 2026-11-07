"""
Endpointهای ادمین برای مدیریت امتیاز.
"""
from typing import Optional

from channels.db import database_sync_to_async
from fastapi import APIRouter, Depends, Query

from applications.score.models import ScoreRule, UserScoreLog
from applications.score.services import (
    ScoreError,
    admin_adjust_score,
    reverse_score_transaction,
)
from applications.user.models import User
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.response import error_response, success_response
from app_fastapi.views.user.user_helper import get_current_user
from app_fastapi.views.score.score import serialize_log, serialize_rule

router = APIRouter()


def _require_admin(user: User):
    """بررسی دسترسی ادمین (طبق سیستم نقش‌های شما — بعداً تنظیم کن)."""
    if not user.is_staff and not user.is_superuser:
        raise PermissionError("دسترسی ادمین لازم است")


# ═══════════════════════════════════════════════════════════
# تنظیم دستی
# ═══════════════════════════════════════════════════════════
@router.post("/adjust/")
async def adjust_score(
    form: dict = Depends(DependencyDataRequest),
    admin: User = Depends(get_current_user),
):
    try:
        _require_admin(admin)
        user_uuid = form.get("user_uuid")
        if not user_uuid:
            return error_response("شناسه کاربر الزامی است")
        amount = int(form.get("amount", 0))
        direction = form.get("direction")  # "earned" | "spent"
        reason = form.get("reason") or "تنظیم دستی"
        if direction not in ("earned", "spent"):
            return error_response("direction باید earned یا spent باشد")
        if amount <= 0:
            return error_response("مقدار باید مثبت باشد")

        target = await database_sync_to_async(User.objects.filter(uuid=user_uuid).first)()
        if not target:
            return error_response("کاربر یافت نشد", status_code=404)

        log, _ = await database_sync_to_async(admin_adjust_score)(
            user_id=target.id,
            amount=amount,
            direction=direction,
            created_by_id=admin.id,
            reason=reason,
            extra={"admin_name": admin.full_name},
        )
        return success_response("امتیاز تنظیم شد", serialize_log(log))
    except PermissionError as e:
        return error_response(str(e), status_code=403)
    except ScoreError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(str(e))


# ═══════════════════════════════════════════════════════════
# برگشت تراکنش
# ═══════════════════════════════════════════════════════════
@router.post("/refund/{log_id}/")
async def refund_log(
    log_id: int,
    form: dict = Depends(DependencyDataRequest),
    admin: User = Depends(get_current_user),
):
    try:
        _require_admin(admin)
        reason = form.get("reason") or "برگشت توسط ادمین"
        log, _ = await database_sync_to_async(reverse_score_transaction)(
            log_id=log_id, reason=reason, created_by_id=admin.id,
        )
        return success_response("تراکنش برگشت خورد", serialize_log(log))
    except PermissionError as e:
        return error_response(str(e), status_code=403)
    except ScoreError as e:
        return error_response(str(e))
    except Exception as e:
        return error_response(str(e))


# ═══════════════════════════════════════════════════════════
# مدیریت قواعد
# ═══════════════════════════════════════════════════════════
@router.get("/rules/")
async def admin_list_rules(admin: User = Depends(get_current_user)):
    try:
        _require_admin(admin)
        data = await database_sync_to_async(
            lambda: [serialize_rule(r) for r in ScoreRule.objects.order_by("code")]
        )()
        return success_response("قواعد", data)
    except PermissionError as e:
        return error_response(str(e), status_code=403)


@router.patch("/rules/{code}/")
async def update_rule(
    code: str,
    form: dict = Depends(DependencyDataRequest),
    admin: User = Depends(get_current_user),
):
    try:
        _require_admin(admin)
        updates = {}
        for field in (
            "default_amount", "cap_count", "max_amount_per_period",
            "is_active", "requires_approval", "requires_reference",
            "metadata", "valid_from", "valid_until",
        ):
            if field in form:
                updates[field] = form[field]

        updated = await database_sync_to_async(
            lambda: ScoreRule.objects.filter(code=code).update(**updates)
        )()
        if not updated:
            return error_response("قاعده یافت نشد", status_code=404)

        rule = await database_sync_to_async(
            lambda: ScoreRule.objects.get(code=code)
        )()
        return success_response("قاعده به‌روزرسانی شد", serialize_rule(rule))
    except PermissionError as e:
        return error_response(str(e), status_code=403)