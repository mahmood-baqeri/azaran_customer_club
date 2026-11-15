# applications/score/view/user_score_view.py

import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess
from applications.user.models import User

from ..clean_data import score_adjust__clean__data
from ..forms import adjust__form
from ..models import UserScore, UserScoreLog
from ..repositories import score__adjust

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# LIST — کاربران با امتیاز
# ═══════════════════════════════════════════════════════════
@is_admin_required
def user_score_index(request):
    RequiredAccess(request, "UserScoreRead")

    # ✅ از User شروع می‌کنیم تا کاربران بدون Score هم دیده شوند
    qs = (
        User.objects
        .select_related("relation_score")
        .filter(is_active=True)
    )

    q = (request.GET.get("q") or "").strip()
    if q:
        cond = (
            Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(mobile__icontains=q)
        )
        if q.isdigit():
            cond |= Q(id=int(q))
        qs = qs.filter(cond)

    # مرتب‌سازی
    sort = request.GET.get("sort", "balance_high")
    if sort == "balance_high":
        qs = qs.order_by("-relation_score__current_balance")
    elif sort == "balance_low":
        qs = qs.order_by("relation_score__current_balance")
    elif sort == "earned_high":
        qs = qs.order_by("-relation_score__total_earned")
    elif sort == "earned_low":
        qs = qs.order_by("relation_score__total_earned")
    elif sort == "spent_high":
        qs = qs.order_by("-relation_score__total_spent")
    else:
        qs = qs.order_by("-id")

    # بازه موجودی
    min_balance = request.GET.get("min_balance")
    if min_balance and str(min_balance).isdigit():
        qs = qs.filter(relation_score__current_balance__gte=int(min_balance))
    max_balance = request.GET.get("max_balance")
    if max_balance and str(max_balance).isdigit():
        qs = qs.filter(relation_score__current_balance__lte=int(max_balance))

    try:
        count = int(request.GET.get("count", "30"))
    except ValueError:
        count = 30

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": "امتیازات کاربران",
        "searchUrl": reverse("app_score:user_score_index"),
        "searchText": q,
        "searchSort": sort,
        "searchCount": count,
        "sortWithSystemLog": [
            {"en": "balance_high", "fa": "بیشترین موجودی"},
            {"en": "balance_low", "fa": "کمترین موجودی"},
            {"en": "earned_high", "fa": "بیشترین کسب"},
            {"en": "earned_low", "fa": "کمترین کسب"},
            {"en": "spent_high", "fa": "بیشترین مصرف"},
        ],
        "min_balance": min_balance or "",
        "max_balance": max_balance or "",
        "all": page,
        "total": paginator.count,
        "request_get": request.GET,
    }
    return render(request, "pages/score/all_user_scores.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# DETAIL — امتیاز و لاگ‌های یک کاربر
# ═══════════════════════════════════════════════════════════
@is_admin_required
def user_score_detail(request, user_id):
    RequiredAccess(request, "UserScoreRead")

    user = get_object_or_404(
        User.objects.select_related("relation_score"),
        id=user_id,
    )
    score = user.get_score  # ممکن است None باشد
    logs = (
        UserScoreLog.objects
        .filter(user=user)
        .select_related("created_by")
        .order_by("-created_at")[:50]
    )

    return render(request, "pages/score/user_score_detail.html", {
        "target_user": user,
        "score": score,
        "logs": logs,
        "log_count_total": UserScoreLog.objects.filter(user=user).count(),
    })


# ═══════════════════════════════════════════════════════════
# ADJUST — تنظیم دستی
# ═══════════════════════════════════════════════════════════
@is_admin_required
def user_score_adjust(request, user_id):
    RequiredAccess(request, "UserScoreAdjust")
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        cleaned, errors = score_adjust__clean__data(request.POST)
        if errors:
            for err in errors:
                messages.add_message(
                    request, messages.ERROR,
                    __import__("json").dumps({"text": err}),
                )
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"تنظیم دستی امتیاز «{user.full_name}»",
                    "backUrl": reverse("app_score:user_score_detail", kwargs={"user_id": user.id}),
                    "storeUrl": reverse("app_score:user_score_adjust", kwargs={"user_id": user.id}),
                    "items": adjust__form(user=user, raw_data=request.POST),
                }
            })

        try:
            log = score__adjust(
                user=user,
                direction=cleaned["direction"],
                amount=cleaned["amount"],
                reason=cleaned["reason"],
                changed_by=request.user,
            )
        except ValueError as e:
            messages.add_message(
                request, messages.ERROR,
                __import__("json").dumps({"text": str(e)}),
            )
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"تنظیم دستی امتیاز «{user.full_name}»",
                    "backUrl": reverse("app_score:user_score_detail", kwargs={"user_id": user.id}),
                    "storeUrl": reverse("app_score:user_score_adjust", kwargs={"user_id": user.id}),
                    "items": adjust__form(user=user, raw_data=request.POST),
                }
            })
        except Exception:
            logger.exception("user_score_adjust failed user=%s", user_id)
            messages.add_message(
                request, messages.ERROR,
                __import__("json").dumps({"text": "خطا در تنظیم امتیاز"}),
            )
            return redirect("app_score:user_score_detail", user_id=user.id)

        messages.add_message(
            request, messages.SUCCESS,
            __import__("json").dumps({
                "text": f"{'افزودن' if cleaned['direction'] == 'earned' else 'کسر'} "
                        f"{cleaned['amount']} امتیاز انجام شد"
            }),
        )
        return redirect("app_score:user_score_detail", user_id=user.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": f"تنظیم دستی امتیاز «{user.full_name}»",
            "backUrl": reverse("app_score:user_score_detail", kwargs={"user_id": user.id}),
            "storeUrl": reverse("app_score:user_score_adjust", kwargs={"user_id": user.id}),
            "items": adjust__form(user=user),
        }
    })