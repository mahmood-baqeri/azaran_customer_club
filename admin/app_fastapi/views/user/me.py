# app_fastapi/views/user/me.py

import logging
from asgiref.sync import sync_to_async
from fastapi import APIRouter, Depends
from django.db.models import Prefetch

# ── Import Models ─────────────────────────────────
from applications.user.models import User, UserInvitation
from applications.project.models import Project
from applications.factor.models import Factor
from applications.gift.models import GiftOrder
from applications.promotion.models import PromotionOrder
from applications.support.models import Support
from applications.gallery.models import Gallery
from applications.visit.models import RequestVisit
from applications.faq.models import FAQ
from applications.review.models import ReviewQuestion

# ── Import Serializers & Helpers ──────────────────
from app_fastapi.views.user.user import user_serialize
from app_fastapi.views.user.helper import get_current_user
from app_fastapi.conf.response import success_response, error_response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/me/")
async def get_my_full_profile(user: User = Depends(get_current_user)):
    """
    دریافت اطلاعات جامع کاربر در یک درخواست واحد (بهینه با Prefetch).
    """
    try:
        data = await _get_full_profile_db(user.id)
        return success_response("پروفایل کامل کاربر", data)
    except Exception:
        logger.exception("get_my_full_profile failed")
        return error_response("خطا در دریافت اطلاعات پروفایل")


@sync_to_async
def _get_full_profile_db(user_id: int):
    # ۱. واکشی هوشمندانه کاربر با تمام روابط (جلوگیری از N+1)
    user = (
        User.objects
        .select_related('relation_profile', 'relation_score')
        .prefetch_related(
            'user_job_certificates',
            'user_favorite_answers',
            'user_projects',
            'user_factors',
            'user_gift_orders__gift', # ✅ واکشی هدیه همراه سفارش
            'user_promotion_orders',
            'user_supports',
            'user_gallery_posts',
            'user_visit_requests__visit', # ✅ واکشی زمان بازدید
            'user_faqs',
            'review_answers',
            'user_score_logs',
            'relation_sent_invitations'
        )
        .get(id=user_id)
    )

    # ۲. سریالایزر پایه (اطلاعات پروفایل، مدارک و ...)
    base_data = user_serialize(user)

    # ─────────────────────────────────────────────
    # ۳. محاسبه آمار (از دیتای پیش‌واکشی‌شده در حافظه - بدون کوئری اضافی)
    # ─────────────────────────────────────────────

    projects = list(user.user_projects.all())
    factors = list(user.user_factors.all())
    gift_orders = list(user.user_gift_orders.all())
    promo_orders = list(user.user_promotion_orders.all())
    supports = list(user.user_supports.all())
    gallery = list(user.user_gallery_posts.all())
    visits = list(user.user_visit_requests.all())
    faqs = list(user.user_faqs.all())
    reviews = list(user.review_answers.all())
    invitations = list(user.relation_sent_invitations.all())

    # شمارش در حافظه (O(N) - بسیار سریع)
    projects_stats = {
        "total": len(projects),
        "pending": sum(1 for p in projects if p.status == Project.Status.PENDING),
        "approved": sum(1 for p in projects if p.status == Project.Status.APPROVED),
        "rejected": sum(1 for p in projects if p.status == Project.Status.REJECTED),
    }

    factors_stats = {
        "total": len(factors),
        "pending": sum(1 for f in factors if f.status == Factor.Status.PENDING),
        "approved": sum(1 for f in factors if f.status == Factor.Status.APPROVED),
        "rejected": sum(1 for f in factors if f.status == Factor.Status.REJECTED),
    }

    gift_orders_stats = {
        "total": len(gift_orders),
        "pending": sum(1 for g in gift_orders if g.status == GiftOrder.Status.PENDING),
        "shipped": sum(1 for g in gift_orders if g.status == GiftOrder.Status.SHIPPED),
        "delivered": sum(1 for g in gift_orders if g.status == GiftOrder.Status.DELIVERED),
    }

    promo_orders_stats = {
        "total": len(promo_orders),
        "pending": sum(1 for p in promo_orders if p.status == PromotionOrder.Status.PENDING),
        "delivered": sum(1 for p in promo_orders if p.status == PromotionOrder.Status.DELIVERED),
    }

    supports_stats = {
        "total": len(supports),
        "open": sum(1 for s in supports if s.status == Support.Status.OPEN),
        "in_progress": sum(1 for s in supports if s.status == Support.Status.IN_PROGRESS),
        "closed": sum(1 for s in supports if s.status == Support.Status.CLOSED),
    }

    gallery_stats = {
        "total": len(gallery),
        "approved": sum(1 for g in gallery if g.status == Gallery.Status.APPROVED),
        "pending": sum(1 for g in gallery if g.status == Gallery.Status.PENDING),
    }

    visits_stats = {
        "total": len(visits),
        "pending": sum(1 for v in visits if v.status == RequestVisit.Status.PENDING),
        "approved": sum(1 for v in visits if v.status == RequestVisit.Status.APPROVED),
    }

    # نظرسنجی
    # نکته: برای بررسی تعداد سوالات فعال، یک کوئری جدا می‌زنیم (چون برای هر کاربر واکشی نمی‌شود)
    total_active_reviews = ReviewQuestion.objects.filter(is_active=True).count()
    has_answered_all_reviews = (len(reviews) >= total_active_reviews) if total_active_reviews > 0 else True

    invitation_stats = {
        "total_sent": len(invitations),
        "successful": sum(1 for i in invitations if i.invited_user_id is not None),
        "rewarded": sum(1 for i in invitations if i.is_rewarded),
    }

    # ۴. ساخت خروجی نهایی آمار
    base_data["stats"] = {
        "projects": projects_stats,
        "factors": factors_stats,
        "gift_orders": gift_orders_stats,
        "promotion_orders": promo_orders_stats,
        "supports": supports_stats,
        "gallery": gallery_stats,
        "visits": visits_stats,
        "faqs_count": len(faqs),
        "reviews": {
            "answered_count": len(reviews),
            "total_active": total_active_reviews,
            "has_answered_all": has_answered_all_reviews,
        },
        "invitations": invitation_stats,
    }

    # ─────────────────────────────────────────────
    # ۵. آخرین فعالیت‌ها (با مرتب‌سازی روی دیتای حافظه)
    # ─────────────────────────────────────────────
    
    # مرتب‌سازی در حافظه (چون از قبل لود شده‌اند)
    recent_projects = sorted(projects, key=lambda x: x.created_at, reverse=True)[:3]
    recent_factors = sorted(factors, key=lambda x: x.created_at, reverse=True)[:3]
    recent_gifts = sorted(gift_orders, key=lambda x: x.created_at, reverse=True)[:3]
    
    # برای لاگ‌های امتیاز، چون ممکن است زیاد باشند، از خود دیتابیس با limit استفاده می‌کنیم
    # اما چون prefetch کردیم، مرتب‌سازی در حافظه هم سریع است
    recent_score_logs = sorted(
        list(user.user_score_logs.all()), 
        key=lambda x: x.created_at, 
        reverse=True
    )[:5]

    base_data["recent_projects"] = [
        {
            "id": p.id,
            "title": p.title,
            "type_display": p.get_type_display(),
            "status_display": p.get_status_display(),
            "created_at": p.created_at.isoformat() if p.created_at else None,
        } for p in recent_projects
    ]

    base_data["recent_factors"] = [
        {
            "id": f.id,
            "invoice_number": f.invoice_number,
            "status_display": f.get_status_display(),
            "amount": f.amount,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        } for f in recent_factors
    ]

    base_data["recent_gift_orders"] = [
        {
            "id": g.id,
            "gift_title": g.gift.title if g.gift else "هدیه",
            "status_display": g.get_status_display(),
            "created_at": g.created_at.isoformat() if g.created_at else None,
        } for g in recent_gifts
    ]

    base_data["recent_score_logs"] = [
        {
            "id": log.id,
            "code_display": log.get_transaction_code_display(),
            "direction": log.direction,
            "amount": log.amount,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        } for log in recent_score_logs
    ]

    return base_data