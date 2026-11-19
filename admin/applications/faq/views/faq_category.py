# Path: applications/faq/views/faq_category.py

# applications/faq/views/faq_category.py

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

from ..clean_data import category__clean__data
from ..forms import category__filters, category__form
from ..models import Category
from ..repositories import (
    category__delete,
    category__store,
    category__toggle_active,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Filter helper
# ═══════════════════════════════════════════════════════════
def _filtered_categories_qs(request):
    qs = Category.objects.annotate(faqs_count=Count("faqs", distinct=True))

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(title__icontains=q)

    is_active = (request.GET.get("is_active") or "").strip()
    if is_active == "1":
        qs = qs.filter(is_active=True)
    elif is_active == "0":
        qs = qs.filter(is_active=False)

    sort = request.GET.get("sort", "desc")
    if sort == "asc":
        qs = qs.order_by("created_at")
    elif sort == "title_asc":
        qs = qs.order_by("title")
    elif sort == "faqs_desc":
        qs = qs.order_by("-faqs_count", "title")
    else:
        qs = qs.order_by("-created_at")

    return qs


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def category_index(request):
    RequiredAccess(request, "FaqRead")
    qs = _filtered_categories_qs(request)

    try:
        count = int(request.GET.get("count", "20"))
    except ValueError:
        count = 20

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": "دسته‌بندی‌های پرسش و پاسخ",
        "newUrl": reverse("app_faq:category_create"),
        "searchUrl": reverse("app_faq:category_index"),
        "exportUrl": reverse("app_faq:category_export"),
        "filters": category__filters(get_data=request.GET),
        "searchCount": count,
        "all": page,
        "total": paginator.count,
    }
    return render(request, "pages/faq/all_categories.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def category_export(request):
    RequiredAccess(request, "FaqRead")
    qs = _filtered_categories_qs(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "دسته‌بندی‌ها"
    ws.sheet_view.rightToLeft = True

    headers = ["#", "عنوان", "تعداد پرسش", "وضعیت", "تاریخ ایجاد"]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for c in ws[1]:
        c.font = head_font
        c.fill = head_fill
        c.alignment = Alignment(horizontal="center", vertical="center")

    for cat in qs.iterator():
        ws.append([
            cat.id,
            cat.title,
            cat.faqs_count,
            "فعال" if cat.is_active else "غیرفعال",
            cat.created_at.strftime("%Y-%m-%d %H:%M") if cat.created_at else "",
        ])

    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"faq_categories_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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
def category_create(request):
    RequiredAccess(request, "FaqCreate")

    if request.method == "POST":
        cleaned, errors = category__clean__data(request.POST)
        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد دسته‌بندی",
                    "backUrl": reverse("app_faq:category_index"),
                    "storeUrl": reverse("app_faq:category_create"),
                    "items": category__form(raw_data=request.POST),
                }
            })

        try:
            category__store(cleaned=cleaned)
        except Exception:
            logger.exception("category_create failed")
            response_msg(request, messages.ERROR, "خطا در ذخیره دسته‌بندی")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد دسته‌بندی",
                    "backUrl": reverse("app_faq:category_index"),
                    "storeUrl": reverse("app_faq:category_create"),
                    "items": category__form(raw_data=request.POST),
                }
            })

        response_msg(request, messages.SUCCESS, "دسته‌بندی ایجاد شد")
        return redirect("app_faq:category_index")

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ایجاد دسته‌بندی",
            "backUrl": reverse("app_faq:category_index"),
            "storeUrl": reverse("app_faq:category_create"),
            "items": category__form(),
        }
    })


# ═══════════════════════════════════════════════════════════
# UPDATE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def category_update(request, id):
    RequiredAccess(request, "FaqUpdate")
    category = get_object_or_404(Category, id=id)

    if request.method == "POST":
        cleaned, errors = category__clean__data(request.POST, current_category=category)
        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"ویرایش «{category.title}»",
                    "backUrl": reverse("app_faq:category_index"),
                    "storeUrl": reverse("app_faq:category_update", kwargs={"id": category.id}),
                    "items": category__form(category=category, raw_data=request.POST),
                }
            })

        try:
            category__store(cleaned=cleaned, item=category)
        except Exception:
            logger.exception("category_update failed id=%s", id)
            response_msg(request, messages.ERROR, "خطا در ذخیره تغییرات")
            return redirect("app_faq:category_index")

        response_msg(request, messages.SUCCESS, "دسته‌بندی به‌روزرسانی شد")
        return redirect("app_faq:category_index")

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": f"ویرایش «{category.title}»",
            "backUrl": reverse("app_faq:category_index"),
            "storeUrl": reverse("app_faq:category_update", kwargs={"id": category.id}),
            "items": category__form(category=category),
        }
    })


# ═══════════════════════════════════════════════════════════
# DELETE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def category_delete(request, id):
    RequiredAccess(request, "FaqDelete")
    if request.method != "POST":
        return redirect("app_faq:category_index")

    try:
        category__delete(id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_faq:category_index")
    except Exception:
        logger.exception("category_delete failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در حذف")
        return redirect("app_faq:category_index")

    response_msg(request, messages.SUCCESS, "دسته‌بندی حذف شد")
    return redirect("app_faq:category_index")


# ═══════════════════════════════════════════════════════════
# TOGGLE ACTIVE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def category_toggle_active(request, id):
    RequiredAccess(request, "FaqUpdate")
    if request.method != "POST":
        return redirect("app_faq:category_index")

    try:
        is_active = category__toggle_active(id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_faq:category_index")

    response_msg(
        request, messages.SUCCESS,
        "دسته‌بندی فعال شد" if is_active else "دسته‌بندی غیرفعال شد",
    )
    return redirect("app_faq:category_index")