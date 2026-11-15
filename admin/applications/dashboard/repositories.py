# applications/dashboard/repositories.py

import logging
from datetime import timedelta

from django.db.models import Count, Sum, Q
from django.utils import timezone

from applications.core.constant import LEVEL_THRESHOLD
from applications.user.models import User
from applications.score.models import UserScore, UserScoreLog
from applications.gift.models import Gift, GiftOrder
from applications.promotion.models import Promotion, PromotionOrder
from applications.project.models import Project
from applications.factor.models import Factor
from applications.visit.models import Visit, RequestVisit
from applications.support.models import Support
from applications.gallery.models import Gallery
from applications.review.models import ReviewQuestion, ReviewAnswer
from applications.faq.models import Category, FAQ, Answer
from applications.notification.models import Notification
from applications.learn.models import Learn

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# KPI — تمام آمار در یک فراخوانی
# ═══════════════════════════════════════════════════════════
def dashboard_kpis():
    now = timezone.now()
    d7 = now - timedelta(days=7)
    d30 = now - timedelta(days=30)

    # ─── کاربران ─────────────────────────────────────
    users_qs = User.objects.all()
    users = {
        "total": users_qs.count(),
        "active": users_qs.filter(is_active=True).count(),
        "verified": users_qs.filter(is_mobile_verified=True).count(),
        "new_7d": users_qs.filter(date_joined__gte=d7).count(),
        "new_30d": users_qs.filter(date_joined__gte=d30).count(),
        "managers": users_qs.filter(Q(is_staff=True) | Q(is_superuser=True)).count(),
        "ostadkar": users_qs.filter(
            relation_score__total_earned__gte=LEVEL_THRESHOLD
        ).count(),
        "kardan": users_qs.filter(
            Q(relation_score__total_earned__lt=LEVEL_THRESHOLD)
            | Q(relation_score__isnull=True)
        ).count(),
    }

    # ─── امتیازات ────────────────────────────────────
    agg = UserScore.objects.aggregate(
        total_balance=Sum("current_balance"),
        total_earned=Sum("total_earned"),
        total_spent=Sum("total_spent"),
    )
    scores = {
        "total_balance": agg["total_balance"] or 0,
        "total_earned": agg["total_earned"] or 0,
        "total_spent": agg["total_spent"] or 0,
        "logs_7d": UserScoreLog.objects.filter(created_at__gte=d7).count(),
        "logs_30d": UserScoreLog.objects.filter(created_at__gte=d30).count(),
        "earned_7d": UserScoreLog.objects.filter(
            created_at__gte=d7, direction="earned"
        ).aggregate(t=Sum("amount"))["t"] or 0,
        "spent_7d": UserScoreLog.objects.filter(
            created_at__gte=d7, direction="spent"
        ).aggregate(t=Sum("amount"))["t"] or 0,
    }

    # ─── هدایا ───────────────────────────────────────
    go = GiftOrder.objects.all()
    gifts = {
        "total": Gift.objects.count(),
        "active": Gift.objects.filter(is_active=True).count(),
        "orders_total": go.count(),
        "orders_pending": go.filter(status="pending").count(),
        "orders_approved": go.filter(status="approved").count(),
        "orders_shipped": go.filter(status="shipped").count(),
        "orders_delivered": go.filter(status="delivered").count(),
        "orders_7d": go.filter(created_at__gte=d7).count(),
        "azar_spent": go.filter(
            status__in=["approved", "shipped", "delivered"]
        ).aggregate(t=Sum("total_azar_value"))["t"] or 0,
    }

    # ─── اقلام تبلیغاتی ──────────────────────────────
    po = PromotionOrder.objects.all()
    promotions = {
        "total": Promotion.objects.count(),
        "active": Promotion.objects.filter(is_active=True).count(),
        "orders_total": po.count(),
        "orders_pending": po.filter(status="pending").count(),
        "orders_approved": po.filter(status="approved").count(),
        "orders_shipped": po.filter(status="shipped").count(),
        "orders_delivered": po.filter(status="delivered").count(),
        "orders_7d": po.filter(created_at__gte=d7).count(),
    }

    # ─── پروژه‌ها ────────────────────────────────────
    pq = Project.objects.all()
    projects = {
        "total": pq.count(),
        "pending": pq.filter(status="pending").count(),
        "approved": pq.filter(status="approved").count(),
        "rejected": pq.filter(status="rejected").count(),
        "new_7d": pq.filter(created_at__gte=d7).count(),
        "water": pq.filter(type="water").count(),
        "gas": pq.filter(type="gas").count(),
    }

    # ─── فاکتورها ────────────────────────────────────
    fq = Factor.objects.all()
    factors = {
        "total": fq.count(),
        "pending": fq.filter(status="pending").count(),
        "approved": fq.filter(status="approved").count(),
        "rejected": fq.filter(status="rejected").count(),
        "new_7d": fq.filter(created_at__gte=d7).count(),
        "total_amount": fq.filter(status="approved").aggregate(
            t=Sum("amount")
        )["t"] or 0,
        "amount_7d": fq.filter(
            status="approved", created_at__gte=d7
        ).aggregate(t=Sum("amount"))["t"] or 0,
    }

    # ─── بازدیدها ────────────────────────────────────
    rq = RequestVisit.objects.all()
    visits = {
        "total": Visit.objects.count(),
        "active": Visit.objects.filter(is_active=True).count(),
        "requests_total": rq.count(),
        "requests_pending": rq.filter(status="pending").count(),
        "requests_approved": rq.filter(status="approved").count(),
        "requests_rejected": rq.filter(status="rejected").count(),
        "requests_7d": rq.filter(created_at__gte=d7).count(),
    }

    # ─── پشتیبانی ────────────────────────────────────
    sq = Support.objects.all()
    support = {
        "total": sq.count(),
        "open": sq.filter(status="open").count(),
        "in_progress": sq.filter(status="in_progress").count(),
        "resolved": sq.filter(status="resolved").count(),
        "closed": sq.filter(status="closed").count(),
        "urgent_open": sq.filter(
            priority="urgent", status__in=["open", "in_progress"]
        ).count(),
        "new_7d": sq.filter(created_at__gte=d7).count(),
    }

    # ─── گالری ───────────────────────────────────────
    gq = Gallery.objects.all()
    gallery = {
        "total": gq.count(),
        "pending": gq.filter(status="pending").count(),
        "approved": gq.filter(status="approved").count(),
        "rejected": gq.filter(status="rejected").count(),
        "new_7d": gq.filter(created_at__gte=d7).count(),
        "total_likes": Gallery.objects.aggregate(t=Count("likes"))["t"] or 0,
    }

    # ─── نظرسنجی ─────────────────────────────────────
    reviews = {
        "questions": ReviewQuestion.objects.count(),
        "active_questions": ReviewQuestion.objects.filter(is_active=True).count(),
        "answers": ReviewAnswer.objects.count(),
        "answers_7d": ReviewAnswer.objects.filter(created_at__gte=d7).count(),
    }

    # ─── FAQ ─────────────────────────────────────────
    fq2 = FAQ.objects.all()
    faqs = {
        "categories": Category.objects.count(),
        "total": fq2.count(),
        "active": fq2.filter(is_active=True).count(),
        "pending": fq2.filter(is_active=False).count(),
        "answers": Answer.objects.count(),
        "active_answers": Answer.objects.filter(is_active=True).count(),
    }

    # ─── اعلانات ─────────────────────────────────────
    nq = Notification.objects.all()
    notifications = {
        "total": nq.count(),
        "sent": nq.filter(status="sent").count(),
        "draft": nq.filter(status="draft").count(),
        "scheduled": nq.filter(status="scheduled").count(),
        "sent_7d": nq.filter(sent_at__gte=d7).count(),
    }

    # ─── آموزش ───────────────────────────────────────
    lq = Learn.objects.all()
    learns = {
        "total": lq.count(),
        "active": lq.filter(is_active=True).count(),
        "new_7d": lq.filter(created_at__gte=d7).count(),
    }

    return {
        "users": users,
        "scores": scores,
        "gifts": gifts,
        "promotions": promotions,
        "projects": projects,
        "factors": factors,
        "visits": visits,
        "support": support,
        "gallery": gallery,
        "reviews": reviews,
        "faqs": faqs,
        "notifications": notifications,
        "learns": learns,
    }


# ═══════════════════════════════════════════════════════════
# Charts — داده برای نمودارها
# ═══════════════════════════════════════════════════════════
def chart_users_monthly(months=12):
    since = timezone.now() - timedelta(days=months * 31)
    values = (
        User.objects
        .filter(date_joined__gte=since)
        .values_list("date_joined", flat=True)
    )

    months_map = {}
    for dt in values:
        if not dt:
            continue
        key = dt.strftime("%Y/%m")
        months_map[key] = months_map.get(key, 0) + 1

    return [
        {"label": k, "value": v}
        for k, v in sorted(months_map.items())
    ]

def chart_orders_status():
    return list(
        GiftOrder.objects.values("status").annotate(count=Count("id")).order_by()
    )


def chart_promotion_orders_status():
    return list(
        PromotionOrder.objects.values("status").annotate(count=Count("id")).order_by()
    )


def chart_projects_type():
    return list(
        Project.objects.values("type").annotate(count=Count("id")).order_by()
    )


def chart_users_nature():
    return list(
        User.objects.values("nature").annotate(count=Count("id")).order_by()
    )


def chart_scores_daily(days=30):
    since = timezone.now() - timedelta(days=days)

    values = (
        UserScoreLog.objects
        .filter(created_at__gte=since)
        .values_list("created_at", "direction", "amount")
    )

    days_map = {}
    for dt, direction, amount in values:
        if not dt:
            continue
        key = dt.strftime("%Y/%m/%d")
        if key not in days_map:
            days_map[key] = {"label": key, "earned": 0, "spent": 0}
        if direction == "earned":
            days_map[key]["earned"] += amount or 0
        else:
            days_map[key]["spent"] += amount or 0

    return [days_map[k] for k in sorted(days_map)]


def chart_factors_monthly(months=6):
    since = timezone.now() - timedelta(days=months * 31)

    values = (
        Factor.objects
        .filter(status="approved", created_at__gte=since)
        .values_list("created_at", "amount")
    )

    months_map = {}
    for dt, amount in values:
        if not dt:
            continue
        key = dt.strftime("%Y/%m")
        if key not in months_map:
            months_map[key] = {"label": key, "total": 0, "count": 0}
        months_map[key]["total"] += amount or 0
        months_map[key]["count"] += 1

    return [months_map[k] for k in sorted(months_map)]

# ═══════════════════════════════════════════════════════════
# Reports — per module (لایه‌ی filter مشترک برای list و export)
# ═══════════════════════════════════════════════════════════
def _date_filter(qs, request, field="created_at"):
    df = request.GET.get("date_from")
    dt = request.GET.get("date_to")
    if df:
        qs = qs.filter(**{f"{field}__date__gte": df})
    if dt:
        qs = qs.filter(**{f"{field}__date__lte": dt})
    return qs


def report_users(request):
    qs = User.objects.select_related("relation_score", "relation_profile")
    qs = _date_filter(qs, request, field="date_joined")

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(mobile__icontains=q)
        )

    return qs.order_by("-date_joined")


def report_scores(request):
    qs = UserScoreLog.objects.select_related("user", "created_by")
    qs = _date_filter(qs, request)

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(user__mobile__icontains=q)
            | Q(reason__icontains=q)
        )

    direction = (request.GET.get("direction") or "").strip()
    if direction in ("earned", "spent"):
        qs = qs.filter(direction=direction)

    return qs.order_by("-created_at")


def report_gift_orders(request):
    qs = GiftOrder.objects.select_related("user", "gift", "assigned_to")
    qs = _date_filter(qs, request)

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(user__mobile__icontains=q)
            | Q(receiver_name__icontains=q)
            | Q(tracking_code__icontains=q)
        )

    status = (request.GET.get("status") or "").strip()
    if status:
        qs = qs.filter(status=status)

    return qs.order_by("-created_at")


def report_promotion_orders(request):
    qs = PromotionOrder.objects.select_related("user", "promotion", "assigned_to")
    qs = _date_filter(qs, request)

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(user__mobile__icontains=q)
            | Q(receiver_name__icontains=q)
            | Q(tracking_code__icontains=q)
        )

    status = (request.GET.get("status") or "").strip()
    if status:
        qs = qs.filter(status=status)

    return qs.order_by("-created_at")


def report_projects(request):
    qs = Project.objects.select_related("user", "approved_by")
    qs = _date_filter(qs, request)

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(user__mobile__icontains=q)
        )

    status = (request.GET.get("status") or "").strip()
    if status:
        qs = qs.filter(status=status)

    return qs.order_by("-created_at")


def report_factors(request):
    qs = Factor.objects.select_related("user", "approved_by")
    qs = _date_filter(qs, request)

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(invoice_number__icontains=q)
            | Q(user__mobile__icontains=q)
            | Q(shop_name__icontains=q)
        )

    status = (request.GET.get("status") or "").strip()
    if status:
        qs = qs.filter(status=status)

    return qs.order_by("-created_at")


def report_visit_requests(request):
    qs = RequestVisit.objects.select_related("user", "visit")
    qs = _date_filter(qs, request)

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(user__mobile__icontains=q)
            | Q(companion_name__icontains=q)
        )

    status = (request.GET.get("status") or "").strip()
    if status:
        qs = qs.filter(status=status)

    return qs.order_by("-created_at")


def report_support(request):
    qs = Support.objects.select_related("user", "closed_by")
    qs = _date_filter(qs, request)

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(subject__icontains=q) | Q(user__mobile__icontains=q)
        )

    status = (request.GET.get("status") or "").strip()
    if status:
        qs = qs.filter(status=status)

    return qs.order_by("-created_at")