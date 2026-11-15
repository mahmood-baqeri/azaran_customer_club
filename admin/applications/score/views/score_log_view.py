# applications/score/view/score_log_view.py

import logging

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess
from applications.core.validators import is_valid_date

from ..models import UserScoreLog

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def log_index(request):
    RequiredAccess(request, "ScoreLogRead")

    qs = UserScoreLog.objects.select_related("user", "created_by")

    # ─── جستجوی متنی ───
    q = (request.GET.get("q") or "").strip()
    if q:
        cond = (
            Q(user__mobile__icontains=q)
            | Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(reason__icontains=q)
            | Q(reference_id__icontains=q)
        )
        if q.isdigit():
            cond |= Q(id=int(q))
        qs = qs.filter(cond)

    # ─── filter: transaction_code ───
    filter_val = (request.GET.get("filter") or "").strip()
    if filter_val in dict(UserScoreLog.TransactionCode.choices):
        qs = qs.filter(transaction_code=filter_val)

    # ─── filter2: direction ───
    filter2_val = (request.GET.get("filter2") or "").strip()
    if filter2_val in dict(UserScoreLog.Direction.choices):
        qs = qs.filter(direction=filter2_val)

    # ─── source ───
    source = (request.GET.get("source") or "").strip()
    if source in dict(UserScoreLog.Source.choices):
        qs = qs.filter(source=source)

    # ─── reference_type ───
    ref_type = (request.GET.get("reference_type") or "").strip()
    if ref_type:
        qs = qs.filter(reference_type=ref_type)

    # ─── بازه تاریخ ───
    df = request.GET.get("filterDateStart")
    dt = request.GET.get("filterDateEnd")
    if df and is_valid_date(df):
        qs = qs.filter(created_at__date__gte=df)
    if dt and is_valid_date(dt):
        qs = qs.filter(created_at__date__lte=dt)

    # ─── بازه مقدار ───
    min_amount = request.GET.get("min_amount")
    if min_amount and str(min_amount).isdigit():
        qs = qs.filter(amount__gte=int(min_amount))
    max_amount = request.GET.get("max_amount")
    if max_amount and str(max_amount).isdigit():
        qs = qs.filter(amount__lte=int(max_amount))

    # ─── برگشت‌خورده ───
    reversed_filter = (request.GET.get("is_reversed") or "").strip()
    if reversed_filter == "1":
        qs = qs.filter(is_reversed=True)
    elif reversed_filter == "0":
        qs = qs.filter(is_reversed=False)

    # ─── مرتب‌سازی ───
    sort = request.GET.get("sort", "desc")
    if sort == "asc":
        qs = qs.order_by("created_at")
    elif sort == "amount_desc":
        qs = qs.order_by("-amount")
    elif sort == "amount_asc":
        qs = qs.order_by("amount")
    else:
        qs = qs.order_by("-created_at")

    try:
        count = int(request.GET.get("count", "50"))
    except ValueError:
        count = 50

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": "تاریخچه امتیازات",
        "searchUrl": reverse("app_score:log_index"),
        "searchText": q,
        "searchSort": sort,
        "searchCount": count,
        "sortWithSystemLog": [
            {"en": "desc", "fa": "جدیدترین"},
            {"en": "asc", "fa": "قدیمی‌ترین"},
            {"en": "amount_desc", "fa": "بیشترین مقدار"},
            {"en": "amount_asc", "fa": "کمترین مقدار"},
        ],
        "filterDate": 1,
        "filterDateStart": df or "",
        "filterDateEnd": dt or "",
        "theFilterItems": list(UserScoreLog.TransactionCode.choices),
        "filter": filter_val,
        "theFilterItems2": list(UserScoreLog.Direction.choices),
        "filter2": filter2_val,
        "source": source,
        "reference_type": ref_type,
        "is_reversed": reversed_filter,
        "min_amount": min_amount or "",
        "max_amount": max_amount or "",
        "all": page,
        "total": paginator.count,
        "request_get": request.GET,
    }
    return render(request, "pages/score/all_logs.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# DETAIL
# ═══════════════════════════════════════════════════════════
@is_admin_required
def log_detail(request, id):
    RequiredAccess(request, "ScoreLogRead")

    log = get_object_or_404(
        UserScoreLog.objects.select_related("user", "created_by", "reverses_log"),
        id=id,
    )
    # لاگ‌هایی که همین لاگ را برگشت زده‌اند
    reversals = log.reversal_logs.select_related("created_by").all()

    # لاگ‌های اخیر همین کاربر
    user_recent = (
        UserScoreLog.objects
        .filter(user=log.user)
        .exclude(pk=log.pk)
        .order_by("-created_at")[:10]
    )

    return render(request, "pages/score/log_detail.html", {
        "log": log,
        "reversals": reversals,
        "user_recent": user_recent,
    })