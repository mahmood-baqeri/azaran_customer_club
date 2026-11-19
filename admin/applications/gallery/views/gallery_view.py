# Path: applications/gallery/views/gallery_view.py

# applications/gallery/views/gallery_view.py

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

from ..clean_data import gallery__clean__data
from ..forms import gallery__filters, gallery__form
from ..models import Gallery, GalleryLike
from ..repositories import (
    gallery__approve,
    gallery__delete,
    gallery__reject,
    gallery__store,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Filter helper
# ═══════════════════════════════════════════════════════════
def _filtered_galleries_qs(request):
    qs = (
        Gallery.objects
        .select_related("user")
        .annotate(like_count=Count("likes", distinct=True))
    )

    q = (request.GET.get("q") or "").strip()
    if q:
        cond = (
            Q(caption__icontains=q)
            | Q(location__icontains=q)
            | Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__mobile__icontains=q)
        )
        if q.isdigit():
            cond |= Q(id=int(q))
        qs = qs.filter(cond)

    status = (request.GET.get("status") or "").strip()
    if status in dict(Gallery.Status.choices):
        qs = qs.filter(status=status)

    has_likes = (request.GET.get("has_likes") or "").strip()
    if has_likes == "1":
        qs = qs.filter(like_count__gt=0)
    elif has_likes == "0":
        qs = qs.filter(like_count=0)

    cf = request.GET.get("created_from")
    ct = request.GET.get("created_to")
    if cf:
        qs = qs.filter(created_at__date__gte=cf)
    if ct:
        qs = qs.filter(created_at__date__lte=ct)

    sort = request.GET.get("sort", "desc")
    if sort == "asc":
        qs = qs.order_by("created_at")
    elif sort == "likes_desc":
        qs = qs.order_by("-like_count", "-created_at")
    elif sort == "likes_asc":
        qs = qs.order_by("like_count", "-created_at")
    else:
        qs = qs.order_by("-created_at")

    return qs


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def gallery_index(request):
    RequiredAccess(request, "GalleryRead")
    qs = _filtered_galleries_qs(request)

    try:
        count = int(request.GET.get("count", "20"))
    except ValueError:
        count = 20

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": "گالری",
        "newUrl": reverse("app_gallery:gallery_create"),
        "searchUrl": reverse("app_gallery:gallery_index"),
        "exportUrl": reverse("app_gallery:gallery_export"),
        "filters": gallery__filters(get_data=request.GET),
        "searchCount": count,
        "all": page,
        "total": paginator.count,
    }
    return render(request, "pages/gallery/all_galleries.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def gallery_export(request):
    RequiredAccess(request, "GalleryRead")
    qs = _filtered_galleries_qs(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "گالری"
    ws.sheet_view.rightToLeft = True

    headers = [
        "#", "کاربر", "موبایل", "کپشن", "لوکیشن",
        "تعداد لایک", "وضعیت", "تاریخ ایجاد",
    ]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for c in ws[1]:
        c.font = head_font
        c.fill = head_fill
        c.alignment = Alignment(horizontal="center", vertical="center")

    for g in qs.iterator():
        ws.append([
            g.id,
            g.user.full_name if g.user else "",
            g.user.mobile if g.user else "",
            g.caption or "",
            g.location or "",
            g.like_count,
            g.get_status_display(),
            g.created_at.strftime("%Y-%m-%d %H:%M") if g.created_at else "",
        ])

    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"gallery_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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
def gallery_create(request):
    RequiredAccess(request, "GalleryCreate")

    if request.method == "POST":
        cleaned, errors = gallery__clean__data(request.POST, request.FILES)
        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد پست گالری",
                    "backUrl": reverse("app_gallery:gallery_index"),
                    "storeUrl": reverse("app_gallery:gallery_create"),
                    "items": gallery__form(raw_data=request.POST),
                }
            })

        try:
            g = gallery__store(cleaned=cleaned)
        except Exception:
            logger.exception("gallery_create failed")
            response_msg(request, messages.ERROR, "خطا در ذخیره پست")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد پست گالری",
                    "backUrl": reverse("app_gallery:gallery_index"),
                    "storeUrl": reverse("app_gallery:gallery_create"),
                    "items": gallery__form(raw_data=request.POST),
                }
            })

        response_msg(request, messages.SUCCESS, "پست ایجاد شد")
        return redirect("app_gallery:gallery_detail", id=g.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ایجاد پست گالری",
            "backUrl": reverse("app_gallery:gallery_index"),
            "storeUrl": reverse("app_gallery:gallery_create"),
            "items": gallery__form(),
        }
    })


# ═══════════════════════════════════════════════════════════
# UPDATE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def gallery_update(request, id):
    RequiredAccess(request, "GalleryUpdate")
    g = get_object_or_404(Gallery, id=id)

    if request.method == "POST":
        cleaned, errors = gallery__clean__data(
            request.POST, request.FILES, current_gallery=g,
        )
        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"ویرایش پست #{g.id}",
                    "backUrl": reverse("app_gallery:gallery_detail", kwargs={"id": g.id}),
                    "storeUrl": reverse("app_gallery:gallery_update", kwargs={"id": g.id}),
                    "items": gallery__form(gallery=g, raw_data=request.POST),
                }
            })

        try:
            gallery__store(cleaned=cleaned, item=g)
        except Exception:
            logger.exception("gallery_update failed id=%s", id)
            response_msg(request, messages.ERROR, "خطا در ذخیره تغییرات")
            return redirect("app_gallery:gallery_detail", id=g.id)

        response_msg(request, messages.SUCCESS, "پست به‌روزرسانی شد")
        return redirect("app_gallery:gallery_detail", id=g.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": f"ویرایش پست #{g.id}",
            "backUrl": reverse("app_gallery:gallery_detail", kwargs={"id": g.id}),
            "storeUrl": reverse("app_gallery:gallery_update", kwargs={"id": g.id}),
            "items": gallery__form(gallery=g),
        }
    })


# ═══════════════════════════════════════════════════════════
# DETAIL
# ═══════════════════════════════════════════════════════════
@is_admin_required
def gallery_detail(request, id):
    RequiredAccess(request, "GalleryRead")
    g = get_object_or_404(
        Gallery.objects.select_related("user"),
        id=id,
    )

    likes = (
        GalleryLike.objects
        .filter(gallery=g)
        .select_related("user")
        .order_by("-created_at")
    )

    return render(request, "pages/gallery/gallery_detail.html", {
        "gallery": g,
        "likes": likes,
        "can_approve": g.status != Gallery.Status.APPROVED,
        "can_reject": g.status != Gallery.Status.REJECTED,
        "can_delete": True,
    })


# ═══════════════════════════════════════════════════════════
# DELETE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def gallery_delete(request, id):
    RequiredAccess(request, "GalleryDelete")
    if request.method != "POST":
        return redirect("app_gallery:gallery_index")

    try:
        gallery__delete(id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_gallery:gallery_detail", id=id)
    except Exception:
        logger.exception("gallery_delete failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در حذف")
        return redirect("app_gallery:gallery_detail", id=id)

    response_msg(request, messages.SUCCESS, "پست حذف شد")
    return redirect("app_gallery:gallery_index")


# ═══════════════════════════════════════════════════════════
# APPROVE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def gallery_approve(request, id):
    RequiredAccess(request, "GalleryUpdate")
    if request.method != "POST":
        return redirect("app_gallery:gallery_detail", id=id)

    try:
        gallery__approve(id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_gallery:gallery_detail", id=id)
    except Exception:
        logger.exception("gallery_approve failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در تأیید")
        return redirect("app_gallery:gallery_detail", id=id)

    response_msg(request, messages.SUCCESS, "پست تأیید شد")
    return redirect("app_gallery:gallery_detail", id=id)


# ═══════════════════════════════════════════════════════════
# REJECT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def gallery_reject(request, id):
    RequiredAccess(request, "GalleryUpdate")
    if request.method != "POST":
        return redirect("app_gallery:gallery_detail", id=id)

    try:
        gallery__reject(id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_gallery:gallery_detail", id=id)
    except Exception:
        logger.exception("gallery_reject failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در رد")
        return redirect("app_gallery:gallery_detail", id=id)

    response_msg(request, messages.SUCCESS, "پست رد شد")
    return redirect("app_gallery:gallery_detail", id=id)