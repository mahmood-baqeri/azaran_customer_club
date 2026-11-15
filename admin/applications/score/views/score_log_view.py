# applications/score/view/score_log_view.py

import logging

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess
from applications.core.validators import is_valid_date

from ..forms import log__filters
from ..models import UserScoreLog

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Filter helper — بین لیست و اکسل مشترک
# ═══════════════════════════════════════════════════════════
def _filtered_logs_qs(request):
    qs = UserScoreLog.objects.select_related("user", "created_by", "reverses_log")

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

    filter_val = (request.GET.get("filter") or "").strip()
    if filter_val in dict(UserScoreLog.TransactionCode.choices):
        qs = qs.filter(transaction_code=filter_val)

    filter2_val = (request.GET.get("filter2") or "").strip()
    if filter2_val in dict(UserScoreLog.Direction.choices):
        qs = qs.filter(direction=filter2_val)

    source = (request.GET.get("source") or "").strip()
    if source in dict(UserScoreLog.Source.choices):
        qs = qs.filter(source=source)

    ref_type = (request.GET.get("reference_type") or "").strip()
    if ref_type:
        qs = qs.filter(reference_type=ref_type)

    df = request.GET.get("filterDateStart")
    dt = request.GET.get("filterDateEnd")
    if df and is_valid_date(df):
        qs = qs.filter(created_at__date__gte=df)
    if dt and is_valid_date(dt):
        qs = qs.filter(created_at__date__lte=dt)

    min_amount = request.GET.get("min_amount")
    if min_amount and str(min_amount).isdigit():
        qs = qs.filter(amount__gte=int(min_amount))
    max_amount = request.GET.get("max_amount")
    if max_amount and str(max_amount).isdigit():
        qs = qs.filter(amount__lte=int(max_amount))

    reversed_filter = (request.GET.get("is_reversed") or "").strip()
    if reversed_filter == "1":
        qs = qs.filter(is_reversed=True)
    elif reversed_filter == "0":
        qs = qs.filter(is_reversed=False)

    sort = request.GET.get("sort", "desc")
    if sort == "asc":
        qs = qs.order_by("created_at")
    elif sort == "amount_desc":
        qs = qs.order_by("-amount")
    elif sort == "amount_asc":
        qs = qs.order_by("amount")
    else:
        qs = qs.order_by("-created_at")

    return qs


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def log_index(request):
    RequiredAccess(request, "ScoreLogRead")

    qs = _filtered_logs_qs(request)

    try:
        count = int(request.GET.get("count", "50"))
    except ValueError:
        count = 50

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": "تاریخچه امتیازات",
        "searchUrl": reverse("app_score:log_index"),
        "exportUrl": reverse("app_score:log_export"),   # ← جدید
        "filters": log__filters(get_data=request.GET),
        "showAdvanced": any(
            request.GET.get(k)
            for k in ("reference_type", "is_reversed", "min_amount", "max_amount")
        ),
        "all": page,
        "total": paginator.count,
        "searchCount": count,
    }
    return render(request, "pages/score/all_logs.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def log_export(request):
    RequiredAccess(request, "ScoreLogRead")

    qs = _filtered_logs_qs(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "تاریخچه امتیازات"
    ws.sheet_view.rightToLeft = True

    headers = [
        "#", "کاربر", "موبایل", "کد", "جهت", "مقدار",
        "موجودی قبل", "موجودی بعد", "منبع", "مرجع",
        "دلیل", "وضعیت", "تاریخ",
    ]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for cell in ws[1]:
        cell.font = head_font
        cell.fill = head_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for l in qs.iterator():
        if l.is_reversed:
            status = "برگشت‌خورده"
        elif l.reverses_log_id:
            status = f"برگشتِ #{l.reverses_log_id}"
        else:
            status = "عادی"

        ref = f"{l.reference_type}:{l.reference_id}" if l.reference_type else ""

        ws.append([
            l.id,
            l.user.full_name if l.user else "",
            l.user.mobile if l.user else "",
            l.get_transaction_code_display(),
            l.get_direction_display(),
            l.amount,
            l.balance_before,
            l.balance_after,
            l.get_source_display(),
            ref,
            l.reason or "",
            status,
            l.created_at.strftime("%Y-%m-%d %H:%M") if l.created_at else "",
        ])

    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"score_logs_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    resp = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(resp)
    return resp


# ═══════════════════════════════════════════════════════════
# DETAIL — بدون تغییر
# ═══════════════════════════════════════════════════════════
@is_admin_required
def log_detail(request, id):
    RequiredAccess(request, "ScoreLogRead")

    log = get_object_or_404(
        UserScoreLog.objects.select_related("user", "created_by", "reverses_log"),
        id=id,
    )
    reversals = log.reversal_logs.select_related("created_by").all()
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