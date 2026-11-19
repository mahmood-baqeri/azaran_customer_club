# Path: applications/score/views/user_score_view.py

# applications/score/view/user_score_view.py

import logging
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess
from applications.user.models import User

from ..clean_data import score_adjust__clean__data
from ..forms import adjust__form, user_score__filters
from ..models import UserScore, UserScoreLog
from ..repositories import score__adjust

logger = logging.getLogger(__name__)



# ═══════════════════════════════════════════════════════════
# Filter helper
# ═══════════════════════════════════════════════════════════
def _filtered_user_scores_qs(request):
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

    min_balance = request.GET.get("min_balance")
    if min_balance and str(min_balance).isdigit():
        qs = qs.filter(relation_score__current_balance__gte=int(min_balance))
    max_balance = request.GET.get("max_balance")
    if max_balance and str(max_balance).isdigit():
        qs = qs.filter(relation_score__current_balance__lte=int(max_balance))

    sort = request.GET.get("sort", "balance_high")
    if sort == "balance_low":
        qs = qs.order_by("relation_score__current_balance")
    elif sort == "earned_high":
        qs = qs.order_by("-relation_score__total_earned")
    elif sort == "earned_low":
        qs = qs.order_by("relation_score__total_earned")
    elif sort == "spent_high":
        qs = qs.order_by("-relation_score__total_spent")
    else:
        qs = qs.order_by("-relation_score__current_balance")

    return qs


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def user_score_index(request):
    RequiredAccess(request, "UserScoreRead")

    qs = _filtered_user_scores_qs(request)

    try:
        count = int(request.GET.get("count", "30"))
    except ValueError:
        count = 30

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": "امتیازات کاربران",
        "searchUrl": reverse("app_score:user_score_index"),
        "exportUrl": reverse("app_score:user_score_export"),   # ← جدید
        "filters": user_score__filters(get_data=request.GET),
        "showAdvanced": False,
        "all": page,
        "total": paginator.count,
    }
    return render(request, "pages/score/all_user_scores.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def user_score_export(request):
    RequiredAccess(request, "UserScoreRead")

    qs = _filtered_user_scores_qs(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "امتیازات کاربران"
    ws.sheet_view.rightToLeft = True

    headers = [
        "#", "کاربر", "موبایل", "کد معرف", "موجودی فعلی",
        "کل کسب", "کل مصرف", "سطح",
    ]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for cell in ws[1]:
        cell.font = head_font
        cell.fill = head_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for u in qs.iterator():
        score = getattr(u, "relation_score", None)
        level_label = "استادکار" if getattr(u, "is_ostadkar", False) else "کاردان"

        ws.append([
            u.id,
            u.full_name or u.username or "",
            u.mobile or "",
            u.referral_code or "",
            score.current_balance if score else 0,
            score.total_earned if score else 0,
            score.total_spent if score else 0,
            level_label,
        ])

    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"user_scores_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    resp = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(resp)
    return resp



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