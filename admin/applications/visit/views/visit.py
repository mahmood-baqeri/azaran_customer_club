# applications/visit/views/visit.py

import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess
from applications.core.utils import response_msg

from ..clean_data import visit__clean__data
from ..forms import visit__filters, visit__form
from ..models import RequestVisit, Visit
from ..repositories import (
    visit__delete,
    visit__stats,
    visit__store,
    visit__toggle_active,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Filter helper
# ═══════════════════════════════════════════════════════════
def _filtered_visits_qs(request):
    qs = Visit.objects.annotate(
        approved_count=Count(
            "requests",
            filter=Q(requests__status=RequestVisit.Status.APPROVED),
            distinct=True,
        ),
        pending_count=Count(
            "requests",
            filter=Q(requests__status=RequestVisit.Status.PENDING),
            distinct=True,
        ),
    )

    q = (request.GET.get("q") or "").strip()
    if q and q.isdigit():
        qs = qs.filter(id=int(q))

    is_active = (request.GET.get("is_active") or "").strip()
    if is_active == "1":
        qs = qs.filter(is_active=True)
    elif is_active == "0":
        qs = qs.filter(is_active=False)

    date_from = request.GET.get("date_from")
    if date_from:
        qs = qs.filter(date__date__gte=date_from)

    sort = request.GET.get("sort", "date_desc")
    if sort == "date_asc":
        qs = qs.order_by("date")
    elif sort == "created_desc":
        qs = qs.order_by("-created_at")
    elif sort == "created_asc":
        qs = qs.order_by("created_at")
    else:
        qs = qs.order_by("-date")

    return qs


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def visit_index(request):
    RequiredAccess(request, "VisitRead")
    qs = _filtered_visits_qs(request)

    try:
        count = int(request.GET.get("count", "20"))
    except ValueError:
        count = 20

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    for v in page:
        v.remaining = (
            max(0, v.capacity - v.approved_count) if v.capacity else None
        )
        
    data = {
        "pageTitle": "بازدیدهای کارخانه",
        "newUrl": reverse("app_visit:visit_create"),
        "searchUrl": reverse("app_visit:visit_index"),
        "exportUrl": reverse("app_visit:visit_export"),
        "filters": visit__filters(get_data=request.GET),
        "searchCount": count,
        "all": page,
        "total": paginator.count,
    }
    return render(request, "pages/visit/all_visits.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def visit_export(request):
    RequiredAccess(request, "VisitRead")
    qs = _filtered_visits_qs(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "بازدیدها"
    ws.sheet_view.rightToLeft = True

    headers = [
        "#", "تاریخ بازدید", "ظرفیت", "تأیید‌شده", "در انتظار",
        "باقی‌مانده", "وضعیت", "تاریخ ایجاد",
    ]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for c in ws[1]:
        c.font = head_font
        c.fill = head_fill
        c.alignment = Alignment(horizontal="center", vertical="center")

    for v in qs.iterator():
        remaining = ""
        if v.capacity:
            remaining = max(0, v.capacity - v.approved_count)

        ws.append([
            v.id,
            v.date.strftime("%Y-%m-%d %H:%M") if v.date else "",
            v.capacity or "نامحدود",
            v.approved_count,
            v.pending_count,
            remaining,
            "فعال" if v.is_active else "غیرفعال",
            v.created_at.strftime("%Y-%m-%d %H:%M") if v.created_at else "",
        ])

    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"visits_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    resp = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(resp)
    return resp


# ═══════════════════════════════════════════════════════════
# CREATE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def visit_create(request):
    RequiredAccess(request, "VisitCreate")

    if request.method == "POST":
        cleaned, errors = visit__clean__data(request.POST)
        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد بازدید",
                    "backUrl": reverse("app_visit:visit_index"),
                    "storeUrl": reverse("app_visit:visit_create"),
                    "items": visit__form(raw_data=request.POST),
                }
            })

        try:
            v = visit__store(cleaned=cleaned)
        except Exception:
            logger.exception("visit_create failed")
            response_msg(request, messages.ERROR, "خطا در ذخیره بازدید")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد بازدید",
                    "backUrl": reverse("app_visit:visit_index"),
                    "storeUrl": reverse("app_visit:visit_create"),
                    "items": visit__form(raw_data=request.POST),
                }
            })

        response_msg(request, messages.SUCCESS, "بازدید ایجاد شد")
        return redirect("app_visit:visit_detail", id=v.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ایجاد بازدید",
            "backUrl": reverse("app_visit:visit_index"),
            "storeUrl": reverse("app_visit:visit_create"),
            "items": visit__form(),
        }
    })


# ═══════════════════════════════════════════════════════════
# UPDATE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def visit_update(request, id):
    RequiredAccess(request, "VisitUpdate")
    v = get_object_or_404(Visit, id=id)

    if request.method == "POST":
        cleaned, errors = visit__clean__data(request.POST, current_visit=v)
        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"ویرایش بازدید #{v.id}",
                    "backUrl": reverse("app_visit:visit_detail", kwargs={"id": v.id}),
                    "storeUrl": reverse("app_visit:visit_update", kwargs={"id": v.id}),
                    "items": visit__form(visit=v, raw_data=request.POST),
                }
            })

        try:
            visit__store(cleaned=cleaned, item=v)
        except Exception:
            logger.exception("visit_update failed id=%s", id)
            response_msg(request, messages.ERROR, "خطا در ذخیره تغییرات")
            return redirect("app_visit:visit_detail", id=v.id)

        response_msg(request, messages.SUCCESS, "بازدید به‌روزرسانی شد")
        return redirect("app_visit:visit_detail", id=v.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": f"ویرایش بازدید #{v.id}",
            "backUrl": reverse("app_visit:visit_detail", kwargs={"id": v.id}),
            "storeUrl": reverse("app_visit:visit_update", kwargs={"id": v.id}),
            "items": visit__form(visit=v),
        }
    })


# ═══════════════════════════════════════════════════════════
# DETAIL — show visit + its requests
# ═══════════════════════════════════════════════════════════
@is_admin_required
def visit_detail(request, id):
    RequiredAccess(request, "VisitRead")
    v = get_object_or_404(Visit, id=id)

    # درخواست‌های این بازدید
    requests_qs = (
        RequestVisit.objects
        .filter(visit=v)
        .select_related("user")
        .order_by("-created_at")
    )

    stats = visit__stats(v)

    return render(request, "pages/visit/visit_detail.html", {
        "visit": v,
        "requests": requests_qs,
        "stats": stats,
    })


# ═══════════════════════════════════════════════════════════
# DELETE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def visit_delete(request, id):
    RequiredAccess(request, "VisitDelete")
    if request.method != "POST":
        return redirect("app_visit:visit_index")

    try:
        visit__delete(id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_visit:visit_detail", id=id)
    except Exception:
        logger.exception("visit_delete failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در حذف")
        return redirect("app_visit:visit_detail", id=id)

    response_msg(request, messages.SUCCESS, "بازدید حذف شد")
    return redirect("app_visit:visit_index")


# ═══════════════════════════════════════════════════════════
# TOGGLE ACTIVE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def visit_toggle_active(request, id):
    RequiredAccess(request, "VisitUpdate")
    if request.method != "POST":
        return redirect("app_visit:visit_detail", id=id)

    try:
        is_active = visit__toggle_active(id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_visit:visit_detail", id=id)

    response_msg(
        request, messages.SUCCESS,
        "بازدید فعال شد" if is_active else "بازدید غیرفعال شد",
    )
    return redirect("app_visit:visit_detail", id=id)