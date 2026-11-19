# Path: applications/factor/views/factor_view.py

# applications/factor/views/factor_view.py

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
from applications.user.models import User

from ..clean_data import factor__clean__data, reject__clean__data
from ..forms import factor__filters, factor__form
from ..models import Factor
from ..repositories import (
    factor__approve,
    factor__delete,
    factor__reject,
    factor__store,
)
from ..services import FactorError

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Filter helper
# ═══════════════════════════════════════════════════════════
def _filtered_factors_qs(request):
    qs = Factor.objects.select_related("user", "approved_by")

    q = (request.GET.get("q") or "").strip()
    if q:
        cond = (
            Q(invoice_number__icontains=q)
            | Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__mobile__icontains=q)
            | Q(shop_name__icontains=q)
            | Q(seller_phone__icontains=q)
        )
        if q.isdigit():
            cond |= Q(id=int(q))
        qs = qs.filter(cond)

    status = (request.GET.get("status") or "").strip()
    if status in dict(Factor.Status.choices):
        qs = qs.filter(status=status)

    amount_min = request.GET.get("amount_min")
    if amount_min and str(amount_min).isdigit():
        qs = qs.filter(amount__gte=int(amount_min))
    amount_max = request.GET.get("amount_max")
    if amount_max and str(amount_max).isdigit():
        qs = qs.filter(amount__lte=int(amount_max))

    cf = request.GET.get("created_from")
    ct = request.GET.get("created_to")
    if cf:
        qs = qs.filter(created_at__date__gte=cf)
    if ct:
        qs = qs.filter(created_at__date__lte=ct)

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
def factor_index(request):
    RequiredAccess(request, "FactorRead")
    qs = _filtered_factors_qs(request)

    try:
        count = int(request.GET.get("count", "20"))
    except ValueError:
        count = 20

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": "فاکتورها",
        "newUrl": reverse("app_factor:factor_create"),
        "searchUrl": reverse("app_factor:factor_index"),
        "exportUrl": reverse("app_factor:factor_export"),
        "filters": factor__filters(get_data=request.GET),
        "searchCount": count,
        "all": page,
        "total": paginator.count,
    }
    return render(request, "pages/factor/all_factors.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def factor_export(request):
    RequiredAccess(request, "FactorRead")
    qs = _filtered_factors_qs(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "فاکتورها"
    ws.sheet_view.rightToLeft = True

    headers = [
        "#", "شماره فاکتور", "کاربر", "موبایل", "مبلغ (ریال)",
        "تاریخ صدور", "فروشگاه", "تلفن فروشنده", "وضعیت",
        "تأییدکننده", "تاریخ ایجاد", "دلیل رد",
    ]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for c in ws[1]:
        c.font = head_font
        c.fill = head_fill
        c.alignment = Alignment(horizontal="center", vertical="center")

    for f in qs.iterator():
        ws.append([
            f.id,
            f.invoice_number or "",
            f.user.full_name if f.user else "",
            f.user.mobile if f.user else "",
            f.amount or 0,
            f.invoice_issue_at.strftime("%Y-%m-%d") if f.invoice_issue_at else "",
            f.shop_name or "",
            f.seller_phone or "",
            f.get_status_display(),
            f.approved_by.full_name if f.approved_by else "",
            f.created_at.strftime("%Y-%m-%d %H:%M") if f.created_at else "",
            f.rejection_reason or "",
        ])

    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"factors_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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
def factor_create(request):
    RequiredAccess(request, "FactorCreate")

    if request.method == "POST":
        user_id = (request.POST.get("user") or "").strip()
        user = User.objects.filter(pk=user_id).first() if user_id.isdigit() else None
        if not user:
            response_msg(request, messages.ERROR, "کاربر انتخاب‌شده معتبر نیست")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد فاکتور",
                    "backUrl": reverse("app_factor:factor_index"),
                    "storeUrl": reverse("app_factor:factor_create"),
                    "items": factor__form(raw_data=request.POST),
                }
            })

        cleaned, errors = factor__clean__data(request.POST, request.FILES)
        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد فاکتور",
                    "backUrl": reverse("app_factor:factor_index"),
                    "storeUrl": reverse("app_factor:factor_create"),
                    "items": factor__form(raw_data=request.POST),
                }
            })

        try:
            factor = factor__store(request, cleaned=cleaned, user=user)
        except FactorError as e:
            response_msg(request, messages.ERROR, str(e))
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد فاکتور",
                    "backUrl": reverse("app_factor:factor_index"),
                    "storeUrl": reverse("app_factor:factor_create"),
                    "items": factor__form(raw_data=request.POST),
                }
            })

        response_msg(request, messages.SUCCESS, "فاکتور ثبت شد")
        return redirect("app_factor:factor_detail", id=factor.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ایجاد فاکتور",
            "backUrl": reverse("app_factor:factor_index"),
            "storeUrl": reverse("app_factor:factor_create"),
            "items": factor__form(),
        }
    })


# ═══════════════════════════════════════════════════════════
# UPDATE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def factor_update(request, id):
    RequiredAccess(request, "FactorUpdate")
    factor = get_object_or_404(Factor, id=id)

    if factor.status != Factor.Status.PENDING:
        response_msg(request, messages.ERROR, "فقط فاکتورهای در انتظار قابل ویرایش هستند")
        return redirect("app_factor:factor_detail", id=factor.id)

    if request.method == "POST":
        cleaned, errors = factor__clean__data(
            request.POST, request.FILES, current_factor=factor,
        )
        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"ویرایش فاکتور #{factor.invoice_number or factor.id}",
                    "backUrl": reverse("app_factor:factor_detail", kwargs={"id": factor.id}),
                    "storeUrl": reverse("app_factor:factor_update", kwargs={"id": factor.id}),
                    "items": factor__form(factor=factor, raw_data=request.POST, show_user=False),
                }
            })

        try:
            factor__store(request, cleaned=cleaned, user=factor.user, item=factor)
        except FactorError as e:
            response_msg(request, messages.ERROR, str(e))
            return redirect("app_factor:factor_detail", id=factor.id)

        response_msg(request, messages.SUCCESS, "فاکتور به‌روزرسانی شد")
        return redirect("app_factor:factor_detail", id=factor.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": f"ویرایش فاکتور #{factor.invoice_number or factor.id}",
            "backUrl": reverse("app_factor:factor_detail", kwargs={"id": factor.id}),
            "storeUrl": reverse("app_factor:factor_update", kwargs={"id": factor.id}),
            "items": factor__form(factor=factor, show_user=False),
        }
    })


# ═══════════════════════════════════════════════════════════
# DETAIL
# ═══════════════════════════════════════════════════════════
@is_admin_required
def factor_detail(request, id):
    RequiredAccess(request, "FactorRead")
    factor = get_object_or_404(
        Factor.objects.select_related("user", "approved_by"),
        id=id,
    )

    return render(request, "pages/factor/factor_detail.html", {
        "factor": factor,
        "can_edit": factor.status == Factor.Status.PENDING,
        "can_approve": factor.status == Factor.Status.PENDING,
        "can_reject": factor.status == Factor.Status.PENDING,
        "can_delete": factor.status != Factor.Status.APPROVED,
    })


# ═══════════════════════════════════════════════════════════
# DELETE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def factor_delete(request, id):
    RequiredAccess(request, "FactorDelete")
    if request.method != "POST":
        return redirect("app_factor:factor_index")

    try:
        factor__delete(id)
    except FactorError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_factor:factor_detail", id=id)
    except Exception:
        logger.exception("factor_delete failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در حذف")
        return redirect("app_factor:factor_detail", id=id)

    response_msg(request, messages.SUCCESS, "فاکتور حذف شد")
    return redirect("app_factor:factor_index")


# ═══════════════════════════════════════════════════════════
# APPROVE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def factor_approve_action(request, id):
    RequiredAccess(request, "FactorUpdate")
    if request.method != "POST":
        return redirect("app_factor:factor_detail", id=id)

    try:
        factor__approve(id, admin=request.user)
    except FactorError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_factor:factor_detail", id=id)
    except Exception:
        logger.exception("factor_approve failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در تأیید فاکتور")
        return redirect("app_factor:factor_detail", id=id)

    response_msg(request, messages.SUCCESS, "فاکتور تأیید شد و امتیاز اعطا شد")
    return redirect("app_factor:factor_detail", id=id)


# ═══════════════════════════════════════════════════════════
# REJECT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def factor_reject_action(request, id):
    RequiredAccess(request, "FactorUpdate")
    if request.method != "POST":
        return redirect("app_factor:factor_detail", id=id)

    cleaned, errors = reject__clean__data(request.POST)
    if errors:
        for e in errors:
            response_msg(request, messages.ERROR, e)
        return redirect("app_factor:factor_detail", id=id)

    try:
        factor__reject(id, admin=request.user, reason=cleaned["reason"])
    except FactorError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_factor:factor_detail", id=id)
    except Exception:
        logger.exception("factor_reject failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در رد فاکتور")
        return redirect("app_factor:factor_detail", id=id)

    response_msg(request, messages.SUCCESS, "فاکتور رد شد")
    return redirect("app_factor:factor_detail", id=id)