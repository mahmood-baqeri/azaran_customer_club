# app_fastapi/views/visit/visit.py

import logging

from asgiref.sync import sync_to_async
from fastapi import APIRouter, Depends
from django.db.models import Count, Q
from django.utils import timezone

from applications.visit.models import Visit, RequestVisit
from applications.visit.services import (
    VisitError,
    create_request_visit,
    delete_request_visit,
)
from applications.user.models import User
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.response import error_response, success_response
from app_fastapi.views.user.helper import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


# ═══════════════════════════════════════════════════════════
# Serializers (توابع سینک هستند و باید در thread pool اجرا شوند)
# ═══════════════════════════════════════════════════════════
def _serialize_visit(v: Visit) -> dict:
    current_requests = getattr(v, 'current_requests_count', 0)
    remaining_capacity = None
    if v.capacity is not None:
        remaining_capacity = max(0, v.capacity - current_requests)

    return {
        "id": v.id,
        "date": v.date.isoformat() if v.date else None,
        "capacity": v.capacity,
        "remaining_capacity": remaining_capacity,
        "is_full": remaining_capacity == 0 if remaining_capacity is not None else False,
    }


def _serialize_request_visit(r: RequestVisit, full: bool = False) -> dict:
    data = {
        "id": r.id,
        "status": r.status,
        "status_display": r.get_status_display(),
        "created_at": r.created_at.isoformat() if r.created_at else None,
        
        "approved_at": r.approved_at.isoformat() if r.approved_at else None,
        "rejected_at": r.rejected_at.isoformat() if r.rejected_at else None,
        "rejection_reason": r.rejection_reason if full else None,
        
        "have_companion": r.have_companion,
        "companion": {
            "name": r.companion_name,
            "family": r.companion_family,
            "mobile": r.companion_mobile,
        } if r.have_companion else None,
        "visit": {
            "id": r.visit.id,
            "date": r.visit.date.isoformat() if r.visit.date else None,
        }
    }
    
    if full:
        data["visit"]["location"] = r.visit.location if hasattr(r.visit, 'location') else None
        
    return data


# ═══════════════════════════════════════════════════════════
# ۱. لیست بازدیدهای فعال
# ═══════════════════════════════════════════════════════════
@router.get("/list-available/")
async def list_available_visits(user: User = Depends(get_current_user)):
    # ✅ چون تابع _list_available_visits_db با @sync_to_async تزئین شده، مستقیم await می‌شود
    data = await _list_available_visits_db()
    return success_response("لیست بازدیدهای فعال", data)


@sync_to_async
def _list_available_visits_db():
    now = timezone.now()
    visits = (
        Visit.objects
        .filter(
            is_active=True,
            date__gte=now
        )
        .annotate(
            current_requests_count=Count(
                'requests', 
                filter=Q(requests__status__in=[
                    RequestVisit.Status.PENDING, 
                    RequestVisit.Status.APPROVED
                ])
            )
        )
        .order_by('date')
        [:6]
    )
    return [_serialize_visit(v) for v in visits]


# ═══════════════════════════════════════════════════════════
# ۲. ثبت درخواست بازدید
# ═══════════════════════════════════════════════════════════
@router.post("/create/")
async def create_visit_request(
    form: dict = Depends(DependencyDataRequest),
    user: User = Depends(get_current_user),
):
    
    is_ostadkar = await sync_to_async(lambda: user.is_ostadkar)()
    if not is_ostadkar:
        return error_response("درخواست بازدید از کارخانه فقط برای اعضای سطح استادکار امکان‌پذیر است",)
        
        
    visit_id = form.get("visit_id")
    if not visit_id:
        return error_response("شناسه بازدید الزامی است")

    try:
        have_companion = str(form.get("have_companion", "false")).lower() in ("true", "1", "yes")

        # ✅ ۱. اجرای سرویس در thread pool
        req = await sync_to_async(create_request_visit)(
            user=user,
            visit_id=int(visit_id),
            have_companion=have_companion,
            companion_name=form.get("companion_name"),
            companion_family=form.get("companion_family"),
            companion_mobile=form.get("companion_mobile"),
        )
        
        # ✅ ۲. سریالایز کردن هم باید در thread pool باشد چون req.visit یک رابطه Lazy است
        data = await sync_to_async(_serialize_request_visit)(req, full=True)
        
        return success_response(
            "درخواست بازدید شما با موفقیت ثبت شد",
            data
        )
    except VisitError as e:
        return error_response(str(e), status_code=400)
    except Exception:
        logger.exception("create_visit_request failed")
        return error_response("خطا در ثبت درخواست بازدید")


# ═══════════════════════════════════════════════════════════
# ۳. لیست درخواست‌های من
# ═══════════════════════════════════════════════════════════
@router.get("/list/")
async def list_my_visit_requests(user: User = Depends(get_current_user)):
    data = await _list_requests(user.id)
    return success_response("درخواست‌های بازدید من", data)


@sync_to_async
def _list_requests(user_id: int):
    qs = (
        RequestVisit.objects
        .select_related("visit")
        .filter(user_id=user_id)
        .order_by("-created_at")
    )
    return [_serialize_request_visit(r) for r in qs]


# ═══════════════════════════════════════════════════════════
# ۴. جزئیات یک درخواست
# ═══════════════════════════════════════════════════════════
@router.get("/{request_id}/")
async def get_visit_request_detail(
    request_id: int,
    user: User = Depends(get_current_user),
):
    data = await _get_one_request(request_id, user.id)
    if not data:
        return error_response("درخواست بازدید یافت نشد", status_code=404)
        
    return success_response("جزئیات درخواست بازدید", data)


@sync_to_async
def _get_one_request(request_id: int, user_id: int):
    r = (
        RequestVisit.objects
        .select_related("visit")
        .filter(id=request_id, user_id=user_id)
        .first()
    )
    return _serialize_request_visit(r, full=True) if r else None


# ═══════════════════════════════════════════════════════════
# ۵. حذف درخواست
# ═══════════════════════════════════════════════════════════
@router.delete("/{request_id}/")
async def delete_visit_request(
    request_id: int,
    user: User = Depends(get_current_user),
):
    try:
        # ✅ اجرای سرویس حذف در thread pool
        await sync_to_async(delete_request_visit)(request_id, user.id)
        return success_response("درخواست بازدید با موفقیت حذف شد", {})
    except VisitError as e:
        return error_response(str(e), status_code=400)
    except Exception:
        logger.exception("delete_visit_request failed")
        return error_response("خطا در حذف درخواست بازدید")