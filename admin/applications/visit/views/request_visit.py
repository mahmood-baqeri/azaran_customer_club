# applications/visit/views/request_visit.py

import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess
from applications.core.utils import response_msg

from ..clean_data import (
    reject__clean__data,
    request__clean__data,
)
from ..forms import request__filters, request__form
from ..models import RequestVisit, Visit
from ..repositories import (
    request__approve,
    request__delete,
    request__reject,
    request__store,
    visit__stats,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Filter helper
# ═══════════════════════════════════════════════════════════
def _filtered_requests_qs(request):
    qs = RequestVisit.objects.select_related("user", "visit")

    q = (request.GET.get("q") or "").strip()
    if q:
        cond = (
            Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__mobile__icontains=q)
            | Q(companion_name__icontains=q)
            | Q(companion_family__icontains=q)
            | Q(companion_mobile__icontains=q)
        )
        if q.isdigit():
            cond |= Q(id=int(q))
        qs = qs.filter(cond)

    status = (request.GET.get("status") or "").strip()
    if status in dict(RequestVisit.Status.choices):
        qs = qs.filter(status=status)

    visit_id = request.GET.get("visit")
    if visit_id and str(visit_id).isdigit():
        qs = qs.filter(visit_id=int(visit_id))

    has_companion = (request.GET.get("has_companion") or "").strip()
    if has_companion == "1":
        qs = qs.filter(have_companion=True)
    elif has_companion == "0":
        qs = qs.filter(have_companion=False)

    sort = request.GET.get("sort", "desc")
    qs = qs.order_by("created_at" if sort == "asc" else "-created_at")

    return qs


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def request_index(request):
    RequiredAccess(request, "VisitRead")
    qs = _filtered_requests_qs(request)

    try:
        count = int(request.GET.get("count", "20"))
    except ValueError:
        count = 20

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": "درخواست‌های بازدید",
        "newUrl": reverse("app_visit:request_create"),
        "searchUrl": reverse("app_visit:request_index"),
        "exportUrl": reverse("app_visit:request_export"),
        "filters": request__filters(get_data=request.GET),
        "searchCount": count,
        "all": page,
        "total": paginator.count,
    }
    return render(request, "pages/visit/all_visit_requests.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def request_export(request):
    RequiredAccess(request, "VisitRead")
    qs = _filtered_requests_qs(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "درخواست‌های بازدید"
    ws.sheet_view.rightToLeft = True

    headers = [
        "#", "کاربر", "موبایل", "تاریخ بازدید", "وضعیت",
        "همراه", "نام همراه", "موبایل همراه",
        "زمان تأیید", "زمان رد", "دلیل رد", "تاریخ ایجاد",
    ]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for c in ws[1]:
        c.font = head_font
        c.fill = head_fill
        c.alignment = Alignment(horizontal="center", vertical="center")

    for r in qs.iterator():
        companion_name = ""
        if r.have_companion:
            companion_name = f"{r.companion_name or ''} {r.companion_family or ''}".strip()

        ws.append([
            r.id,
            r.user.full_name if r.user else "",
            r.user.mobile if r.user else "",
            r.visit.date.strftime("%Y-%m-%d") if r.visit.date else "",
            r.get_status_display(),
            "بله" if r.have_companion else "خیر",
            companion_name,
            r.companion_mobile or "",
            r.approved_at.strftime("%Y-%m-%d %H:%M") if r.approved_at else "",
            r.rejected_at.strftime("%Y-%m-%d %H:%M") if r.rejected_at else "",
            r.rejection_reason or "",
            r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "",
        ])

    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"visit_requests_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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
def request_create(request):
    RequiredAccess(request, "VisitCreate")

    # اگر از صفحه‌ی یک Visit آمده‌ایم
    visit_id_q = request.GET.get("visit") or request.POST.get("visit")
    visit_fixed = None
    if visit_id_q and str(visit_id_q).isdigit():
        visit_fixed = Visit.objects.filter(id=int(visit_id_q)).first()

    if request.method == "POST":
        cleaned, errors = request__clean__data(request.POST)
        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "افزودن درخواست بازدید",
                    "backUrl": reverse("app_visit:request_index"),
                    "storeUrl": reverse("app_visit:request_create"),
                    "items": request__form(raw_data=request.POST, visit_fixed=visit_fixed),
                }
            })

        try:
            r = request__store(cleaned=cleaned)
        except Exception:
            logger.exception("request_create failed")
            response_msg(request, messages.ERROR, "خطا در ذخیره درخواست")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "افزودن درخواست بازدید",
                    "backUrl": reverse("app_visit:request_index"),
                    "storeUrl": reverse("app_visit:request_create"),
                    "items": request__form(raw_data=request.POST, visit_fixed=visit_fixed),
                }
            })

        response_msg(request, messages.SUCCESS, "درخواست ایجاد شد")
        return redirect("app_visit:request_detail", id=r.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "افزودن درخواست بازدید",
            "backUrl": (
                reverse("app_visit:visit_detail", kwargs={"id": visit_fixed.id})
                if visit_fixed else reverse("app_visit:request_index")
            ),
            "storeUrl": reverse("app_visit:request_create") + (
                f"?visit={visit_fixed.id}" if visit_fixed else ""
            ),
            "items": request__form(visit_fixed=visit_fixed),
        }
    })


# ═══════════════════════════════════════════════════════════
# DETAIL
# ═══════════════════════════════════════════════════════════
@is_admin_required
def request_detail(request, id):
    RequiredAccess(request, "VisitRead")
    req = get_object_or_404(
        RequestVisit.objects.select_related("user", "visit"),
        id=id,
    )

    stats = visit__stats(req.visit)

    return render(request, "pages/visit/visit_request_detail.html", {
        "req": req,
        "stats": stats,
        "can_approve": req.status == RequestVisit.Status.PENDING,
        "can_reject": req.status == RequestVisit.Status.PENDING,
        "can_delete": req.status != RequestVisit.Status.APPROVED,
        "can_edit": req.status == RequestVisit.Status.PENDING,
    })


# ═══════════════════════════════════════════════════════════
# APPROVE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def request_approve(request, id):
    RequiredAccess(request, "VisitUpdate")
    if request.method != "POST":
        return redirect("app_visit:request_detail", id=id)

    try:
        request__approve(id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_visit:request_detail", id=id)
    except Exception:
        logger.exception("request_approve failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در تأیید")
        return redirect("app_visit:request_detail", id=id)

    response_msg(request, messages.SUCCESS, "درخواست تأیید شد")
    return redirect("app_visit:request_detail", id=id)


# ═══════════════════════════════════════════════════════════
# REJECT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def request_reject(request, id):
    RequiredAccess(request, "VisitUpdate")
    if request.method != "POST":
        return redirect("app_visit:request_detail", id=id)

    cleaned, errors = reject__clean__data(request.POST)
    if errors:
        for e in errors:
            response_msg(request, messages.ERROR, e)
        return redirect("app_visit:request_detail", id=id)

    try:
        request__reject(id, reason=cleaned["reason"])
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_visit:request_detail", id=id)
    except Exception:
        logger.exception("request_reject failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در رد")
        return redirect("app_visit:request_detail", id=id)

    response_msg(request, messages.SUCCESS, "درخواست رد شد")
    return redirect("app_visit:request_detail", id=id)


# ═══════════════════════════════════════════════════════════
# DELETE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def request_delete(request, id):
    RequiredAccess(request, "VisitDelete")
    if request.method != "POST":
        return redirect("app_visit:request_index")

    try:
        request__delete(id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_visit:request_detail", id=id)
    except Exception:
        logger.exception("request_delete failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در حذف")
        return redirect("app_visit:request_detail", id=id)

    response_msg(request, messages.SUCCESS, "درخواست حذف شد")
    return redirect("app_visit:request_index")