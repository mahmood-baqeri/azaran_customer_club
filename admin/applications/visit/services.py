# applications/visit/services.py

import logging
from django.db import transaction
from django.utils import timezone

from applications.visit.models import Visit, RequestVisit
from applications.user.models import User

logger = logging.getLogger(__name__)


class VisitError(Exception):
    """خطای منطقی بازدید"""


@transaction.atomic
def create_request_visit(
    user: User,
    visit_id: int,
    have_companion: bool,
    companion_name: str = None,
    companion_family: str = None,
    companion_mobile: str = None,
) -> RequestVisit:
    
    # ۱. بررسی استان کاربر (باید اصفهان باشد - فرض میکنیم ID=4)
    profile = getattr(user, 'relation_profile', None)
    if not profile or profile.province_id != 4:
        raise VisitError("آدرس ثبت شده شما در اصفهان نیست")

    # ۲. بررسی وجود و فعال بودن بازدید
    visit = Visit.objects.select_for_update().filter(id=visit_id).first()
    if not visit:
        raise VisitError("برنامه بازدید یافت نشد")
    if not visit.is_active:
        raise VisitError("این برنامه بازدید در حال حاضر فعال نیست")

    # ۳. بررسی ظرفیت (اختیاری)
    if visit.capacity is not None:
        # تعداد درخواست‌های تایید شده + در انتظار
        current_requests = RequestVisit.objects.filter(
            visit=visit, 
            status__in=[RequestVisit.Status.APPROVED, RequestVisit.Status.PENDING]
        ).count()
        if current_requests >= visit.capacity:
            raise VisitError("ظرفیت این بازدید تکمیل شده است")

    # ۴. بررسی درخواست تکراری
    if RequestVisit.objects.filter(user=user, visit=visit).exists():
        raise VisitError("شما قبلاً برای این بازدید درخواست ثبت کرده‌اید")

    # ۵. ساخت درخواست
    req = RequestVisit.objects.create(
        user=user,
        visit=visit,
        have_companion=have_companion,
        companion_name=companion_name if have_companion else None,
        companion_family=companion_family if have_companion else None,
        companion_mobile=companion_mobile if have_companion else None,
    )
    
    logger.info("Visit request #%s created by user=%s", req.id, user.id)
    return req


@transaction.atomic
def delete_request_visit(request_id: int, user_id: int) -> bool:
    req = RequestVisit.objects.select_for_update().filter(id=request_id, user_id=user_id).first()
    if not req:
        raise VisitError("درخواست یافت نشد")
    
    # کاربر فقط تا زمانی که درخواستش تایید نشده می‌تواند آن را حذف کند
    if req.status == RequestVisit.Status.APPROVED:
        raise VisitError("درخواست شما تایید شده و قابل حذف نیست. لطفاً با پشتیبانی تماس بگیرید")
        
    req.delete()
    logger.info("Visit request #%s deleted by user=%s", request_id, user_id)
    return True


@transaction.atomic
def approve_or_reject_request(
    request_id: int, 
    admin_user: User, 
    new_status: str, 
    rejection_reason: str = None
) -> RequestVisit:
    """تایید یا رد درخواست توسط ادمین"""
    if new_status not in [RequestVisit.Status.APPROVED, RequestVisit.Status.REJECTED]:
        raise VisitError("وضعیت نامعتبر است")

    req = RequestVisit.objects.select_for_update().filter(id=request_id).first()
    if not req:
        raise VisitError("درخواست یافت نشد")

    # 👈 قانون عدم برگشت به عقب
    if req.status in [RequestVisit.Status.APPROVED, RequestVisit.Status.REJECTED]:
        raise VisitError("این درخواست قبلاً تعیین تکلیف شده است و قابل تغییر نیست")

    now = timezone.now()
    
    if new_status == RequestVisit.Status.APPROVED:
        req.status = RequestVisit.Status.APPROVED
        req.approved_at = now
    else:
        req.status = RequestVisit.Status.REJECTED
        req.rejected_at = now
        req.rejection_reason = rejection_reason

    req.save()
    logger.info("Visit request #%s status changed to %s by admin=%s", req.id, new_status, admin_user.id)
    return req