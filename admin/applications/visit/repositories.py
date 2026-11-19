# Path: applications/visit/repositories.py

# applications/visit/repositories.py

import logging

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import RequestVisit, Visit

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# VISIT — Store
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def visit__store(cleaned, item=None):
    if item is None:
        item = Visit(
            date=cleaned.get("date"),
            capacity=cleaned.get("capacity"),
            is_active=cleaned["is_active"],
        )
    else:
        item.date = cleaned.get("date")
        item.capacity = cleaned.get("capacity")
        item.is_active = cleaned["is_active"]

    item.save()
    return item


# ═══════════════════════════════════════════════════════════
# VISIT — Delete
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def visit__delete(visit_id):
    item = Visit.objects.select_for_update().filter(id=visit_id).first()
    if not item:
        raise ValueError("بازدید یافت نشد")

    # جلوگیری از حذف بازدیدی که درخواست تأیید‌شده دارد
    approved = item.requests.filter(status=RequestVisit.Status.APPROVED).count()
    if approved > 0:
        raise ValueError(
            f"این بازدید {approved} درخواست تأیید‌شده دارد و قابل حذف نیست"
        )

    item.delete()


# ═══════════════════════════════════════════════════════════
# VISIT — Toggle active
# ═══════════════════════════════════════════════════════════
def visit__toggle_active(visit_id):
    item = Visit.objects.filter(id=visit_id).first()
    if not item:
        raise ValueError("بازدید یافت نشد")
    item.is_active = not item.is_active
    item.save(update_fields=["is_active", "updated_at"])
    return item.is_active


# ═══════════════════════════════════════════════════════════
# VISIT — Stats helper
# ═══════════════════════════════════════════════════════════
def visit__stats(visit):
    """محاسبه آمار برای نمایش."""
    from .models import RequestVisit as R
    qs = visit.requests.all()
    approved = qs.filter(status=R.Status.APPROVED).count()
    pending = qs.filter(status=R.Status.PENDING).count()
    rejected = qs.filter(status=R.Status.REJECTED).count()
    remaining = (visit.capacity - approved) if visit.capacity else None
    return {
        "approved": approved,
        "pending": pending,
        "rejected": rejected,
        "total": approved + pending + rejected,
        "remaining": remaining,
    }


# ═══════════════════════════════════════════════════════════
# REQUEST — Approve
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def request__approve(request_id):
    req = (
        RequestVisit.objects
        .select_for_update()
        .filter(id=request_id)
        .first()
    )
    if not req:
        raise ValueError("درخواست یافت نشد")

    if req.status == RequestVisit.Status.APPROVED:
        raise ValueError("این درخواست قبلاً تأیید شده است")
    if req.status == RequestVisit.Status.REJECTED:
        raise ValueError("درخواست رد شده و قابل تأیید نیست")

    # قفل روی Visit برای جلوگیری از race condition
    visit = Visit.objects.select_for_update().filter(id=req.visit_id).first()
    if not visit:
        raise ValueError("بازدید مربوطه یافت نشد")

    if not visit.is_active:
        raise ValueError("این بازدید غیرفعال شده است")

    # چک ظرفیت
    if visit.capacity:
        approved_count = RequestVisit.objects.filter(
            visit=visit, status=RequestVisit.Status.APPROVED,
        ).count()
        if approved_count >= visit.capacity:
            raise ValueError(
                f"ظرفیت بازدید ({visit.capacity} نفر) تکمیل شده است"
            )

    req.status = RequestVisit.Status.APPROVED
    req.approved_at = timezone.now()
    req.rejected_at = None
    req.rejection_reason = None
    req.save(update_fields=[
        "status", "approved_at", "rejected_at", "rejection_reason", "updated_at",
    ])
    return req


# ═══════════════════════════════════════════════════════════
# REQUEST — Reject
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def request__reject(request_id, reason):
    req = (
        RequestVisit.objects
        .select_for_update()
        .filter(id=request_id)
        .first()
    )
    if not req:
        raise ValueError("درخواست یافت نشد")

    if req.status == RequestVisit.Status.APPROVED:
        raise ValueError("درخواست تأیید‌شده قابل رد نیست")
    if req.status == RequestVisit.Status.REJECTED:
        raise ValueError("این درخواست قبلاً رد شده است")

    req.status = RequestVisit.Status.REJECTED
    req.rejected_at = timezone.now()
    req.rejection_reason = reason
    req.save(update_fields=["status", "rejected_at", "rejection_reason", "updated_at"])
    return req


# ═══════════════════════════════════════════════════════════
# REQUEST — Store (create by admin)
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def request__store(cleaned, item=None):
    if item is None:
        item = RequestVisit(
            user=cleaned["user"],
            visit=cleaned["visit"],
            have_companion=cleaned["have_companion"],
            companion_name=cleaned.get("companion_name"),
            companion_family=cleaned.get("companion_family"),
            companion_mobile=cleaned.get("companion_mobile"),
            status=RequestVisit.Status.PENDING,
        )
    else:
        if item.status != RequestVisit.Status.PENDING:
            raise ValueError("فقط درخواست‌های در انتظار قابل ویرایش هستند")
        item.user = cleaned["user"]
        item.visit = cleaned["visit"]
        item.have_companion = cleaned["have_companion"]
        item.companion_name = cleaned.get("companion_name")
        item.companion_family = cleaned.get("companion_family")
        item.companion_mobile = cleaned.get("companion_mobile")

    item.save()
    return item


# ═══════════════════════════════════════════════════════════
# REQUEST — Delete
# ═══════════════════════════════════════════════════════════
@transaction.atomic
def request__delete(request_id):
    req = RequestVisit.objects.select_for_update().filter(id=request_id).first()
    if not req:
        raise ValueError("درخواست یافت نشد")
    if req.status == RequestVisit.Status.APPROVED:
        raise ValueError("درخواست تأیید‌شده قابل حذف نیست")
    req.delete()