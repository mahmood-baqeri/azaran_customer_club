# applications/learn/views/learn_view.py

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

from ..clean_data import learn__clean__data
from ..forms import learn__filters, learn__form
from ..models import Learn
from ..repositories import learn__delete, learn__store, learn__toggle_active

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Filter helper
# ═══════════════════════════════════════════════════════════
def _filtered_learns_qs(request):
    qs = Learn.objects.all()

    q = (request.GET.get("q") or "").strip()
    if q:
        cond = (
            Q(title__icontains=q)
            | Q(sub_text__icontains=q)
            | Q(caption__icontains=q)
            | Q(full_text__icontains=q)
        )
        if q.isdigit():
            cond |= Q(id=int(q))
        qs = qs.filter(cond)

    is_active = (request.GET.get("is_active") or "").strip()
    if is_active == "1":
        qs = qs.filter(is_active=True)
    elif is_active == "0":
        qs = qs.filter(is_active=False)

    size = (request.GET.get("size") or "").strip()
    if size in dict(Learn.Size.choices):
        qs = qs.filter(size=size)

    sort = request.GET.get("sort", "desc")
    if sort == "asc":
        qs = qs.order_by("created_at")
    elif sort == "title_asc":
        qs = qs.order_by("title")
    elif sort == "title_desc":
        qs = qs.order_by("-title")
    elif sort == "time_asc":
        qs = qs.order_by("time")
    elif sort == "time_desc":
        qs = qs.order_by("-time")
    else:
        qs = qs.order_by("-created_at")

    return qs


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def learn_index(request):
    RequiredAccess(request, "LearnRead")
    qs = _filtered_learns_qs(request)

    try:
        count = int(request.GET.get("count", "20"))
    except ValueError:
        count = 20

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": "آموزش‌ها",
        "newUrl": reverse("app_learn:learn_create"),
        "searchUrl": reverse("app_learn:learn_index"),
        "exportUrl": reverse("app_learn:learn_export"),
        "filters": learn__filters(get_data=request.GET),
        "searchCount": count,
        "all": page,
        "total": paginator.count,
    }
    return render(request, "pages/learn/all_learns.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def learn_export(request):
    RequiredAccess(request, "LearnRead")
    qs = _filtered_learns_qs(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "آموزش‌ها"
    ws.sheet_view.rightToLeft = True

    headers = [
        "#", "عنوان", "زیرمتن", "کپشن", "عرض", "زمان (دقیقه)",
        "وضعیت", "تاریخ ایجاد",
    ]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for c in ws[1]:
        c.font = head_font
        c.fill = head_fill
        c.alignment = Alignment(horizontal="center", vertical="center")

    for item in qs.iterator():
        ws.append([
            item.id,
            item.title,
            item.sub_text or "",
            item.caption or "",
            item.get_size_display(),
            item.time if item.time is not None else "",
            "فعال" if item.is_active else "غیرفعال",
            item.created_at.strftime("%Y-%m-%d %H:%M") if item.created_at else "",
        ])

    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"learns_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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
def learn_create(request):
    RequiredAccess(request, "LearnCreate")

    if request.method == "POST":
        cleaned, errors = learn__clean__data(request.POST, request.FILES)

        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد آموزش",
                    "backUrl": reverse("app_learn:learn_index"),
                    "storeUrl": reverse("app_learn:learn_create"),
                    "items": learn__form(raw_data=request.POST),
                }
            })

        try:
            item = learn__store(cleaned=cleaned)
        except Exception:
            logger.exception("learn_create failed")
            response_msg(request, messages.ERROR, "خطا در ذخیره آموزش")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد آموزش",
                    "backUrl": reverse("app_learn:learn_index"),
                    "storeUrl": reverse("app_learn:learn_create"),
                    "items": learn__form(raw_data=request.POST),
                }
            })

        response_msg(request, messages.SUCCESS, "آموزش ایجاد شد")
        return redirect("app_learn:learn_detail", id=item.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ایجاد آموزش",
            "backUrl": reverse("app_learn:learn_index"),
            "storeUrl": reverse("app_learn:learn_create"),
            "items": learn__form(),
        }
    })


# ═══════════════════════════════════════════════════════════
# UPDATE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def learn_update(request, id):
    RequiredAccess(request, "LearnUpdate")
    item = get_object_or_404(Learn, id=id)

    if request.method == "POST":
        cleaned, errors = learn__clean__data(
            request.POST, request.FILES, current_learn=item,
        )

        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"ویرایش «{item.title}»",
                    "backUrl": reverse("app_learn:learn_detail", kwargs={"id": item.id}),
                    "storeUrl": reverse("app_learn:learn_update", kwargs={"id": item.id}),
                    "items": learn__form(learn=item, raw_data=request.POST),
                }
            })

        try:
            learn__store(cleaned=cleaned, item=item)
        except Exception:
            logger.exception("learn_update failed id=%s", id)
            response_msg(request, messages.ERROR, "خطا در ذخیره تغییرات")
            return redirect("app_learn:learn_detail", id=item.id)

        response_msg(request, messages.SUCCESS, "آموزش به‌روزرسانی شد")
        return redirect("app_learn:learn_detail", id=item.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": f"ویرایش «{item.title}»",
            "backUrl": reverse("app_learn:learn_detail", kwargs={"id": item.id}),
            "storeUrl": reverse("app_learn:learn_update", kwargs={"id": item.id}),
            "items": learn__form(learn=item),
        }
    })


# ═══════════════════════════════════════════════════════════
# DETAIL
# ═══════════════════════════════════════════════════════════
@is_admin_required
def learn_detail(request, id):
    RequiredAccess(request, "LearnRead")
    item = get_object_or_404(Learn, id=id)
    return render(request, "pages/learn/learn_detail.html", {"learn": item})


# ═══════════════════════════════════════════════════════════
# DELETE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def learn_delete(request, id):
    RequiredAccess(request, "LearnDelete")
    if request.method != "POST":
        return redirect("app_learn:learn_index")

    try:
        learn__delete(id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_learn:learn_detail", id=id)
    except Exception:
        logger.exception("learn_delete failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در حذف")
        return redirect("app_learn:learn_detail", id=id)

    response_msg(request, messages.SUCCESS, "آموزش حذف شد")
    return redirect("app_learn:learn_index")


# ═══════════════════════════════════════════════════════════
# TOGGLE ACTIVE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def learn_toggle_active(request, id):
    RequiredAccess(request, "LearnUpdate")
    if request.method != "POST":
        return redirect("app_learn:learn_detail", id=id)

    try:
        is_active = learn__toggle_active(id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_learn:learn_detail", id=id)

    response_msg(
        request, messages.SUCCESS,
        "آموزش فعال شد" if is_active else "آموزش غیرفعال شد",
    )
    return redirect("app_learn:learn_detail", id=id)