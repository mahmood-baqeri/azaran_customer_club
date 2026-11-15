# applications/project/views/project_view.py

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
    attachment__clean__data,
    colleague__clean__data,
    project__clean__data,
    reject__clean__data,
)
from ..forms import (
    attachment__form,
    colleague__form,
    project__filters,
    project__form,
    reject__form,
)
from ..models import Project
from ..repositories import (
    project__add_colleague,
    project__approve,
    project__delete,
    project__reject,
    project__remove_attachment,
    project__remove_colleague,
    project__store,
    project__upload_attachment,
)
from ..services import ProjectError

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Filter helper
# ═══════════════════════════════════════════════════════════
def _filtered_projects_qs(request):
    qs = (
        Project.objects
        .select_related("user", "approved_by")
        .prefetch_related("colleagues")
    )

    q = (request.GET.get("q") or "").strip()
    if q:
        cond = Q(title__icontains=q) | Q(address__icontains=q) | Q(owner_mobile__icontains=q)
        if q.isdigit():
            cond |= Q(id=int(q))
        qs = qs.filter(cond)

    status = (request.GET.get("status") or "").strip()
    if status in dict(Project.Status.choices):
        qs = qs.filter(status=status)

    type_val = (request.GET.get("type") or "").strip()
    if type_val in dict(Project.Type.choices):
        qs = qs.filter(type=type_val)

    cf = request.GET.get("created_from")
    ct = request.GET.get("created_to")
    if cf:
        qs = qs.filter(created_at__date__gte=cf)
    if ct:
        qs = qs.filter(created_at__date__lte=ct)

    sort = request.GET.get("sort", "desc")
    return qs.order_by("created_at" if sort == "asc" else "-created_at")


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def project_index(request):
    RequiredAccess(request, "ProjectRead")
    qs = _filtered_projects_qs(request)

    try:
        count = int(request.GET.get("count", "20"))
    except ValueError:
        count = 20

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": "پروژه‌ها",
        "newUrl": reverse("project:project_create"),
        "searchUrl": reverse("project:project_index"),
        "exportUrl": reverse("project:project_export"),
        "filters": project__filters(get_data=request.GET),
        "searchCount": count,
        "all": page,
        "total": paginator.count,
    }
    return render(request, "pages/project/all_projects.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def project_export(request):
    RequiredAccess(request, "ProjectRead")
    qs = _filtered_projects_qs(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "پروژه‌ها"
    ws.sheet_view.rightToLeft = True

    headers = [
        "#", "نوع", "عنوان", "صاحب پروژه", "موبایل",
        "آدرس", "وضعیت", "تعداد واحد", "شیرآبی", "شیرگازی",
        "اتصالات", "متراژ لوله", "تأییدکننده",
        "تاریخ ایجاد", "تاریخ اتمام",
    ]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for c in ws[1]:
        c.font = head_font
        c.fill = head_fill
        c.alignment = Alignment(horizontal="center", vertical="center")

    for p in qs.iterator():
        ws.append([
            p.id, p.get_type_display(), p.title or "",
            p.user.full_name if p.user else "",
            p.user.mobile if p.user else "",
            p.address or "",
            p.get_status_display(),
            p.unit_count or 0, p.number_water_taps or 0,
            p.number_gas_taps or 0, p.number_connections or 0,
            p.pipe_length or 0,
            p.approved_by.full_name if p.approved_by else "",
            p.created_at.strftime("%Y-%m-%d %H:%M") if p.created_at else "",
            p.completion_at.strftime("%Y-%m-%d") if p.completion_at else "",
        ])

    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"projects_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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
def project_create(request):
    RequiredAccess(request, "ProjectCreate")

    if request.method == "POST":
        cleaned, errors = project__clean__data(request.POST)
        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد پروژه",
                    "backUrl": reverse("project:project_index"),
                    "storeUrl": reverse("project:project_create"),
                    "items": project__form(raw_data=request.POST),
                }
            })

        try:
            project = project__store(cleaned, user=request.user)
        except ProjectError as e:
            response_msg(request, messages.ERROR, str(e))
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد پروژه",
                    "backUrl": reverse("project:project_index"),
                    "storeUrl": reverse("project:project_create"),
                    "items": project__form(raw_data=request.POST),
                }
            })

        response_msg(request, messages.SUCCESS, "پروژه ایجاد شد. اکنون همکاران و پیوست‌ها را اضافه کنید.")
        return redirect("project:project_detail", id=project.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ایجاد پروژه",
            "backUrl": reverse("project:project_index"),
            "storeUrl": reverse("project:project_create"),
            "items": project__form(),
        }
    })


# ═══════════════════════════════════════════════════════════
# UPDATE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def project_update(request, id):
    RequiredAccess(request, "ProjectUpdate")
    project = get_object_or_404(Project, id=id)

    if project.status != Project.Status.PENDING:
        response_msg(request, messages.ERROR, "فقط پروژه‌های در انتظار قابل ویرایش هستند")
        return redirect("project:project_detail", id=project.id)

    if request.method == "POST":
        cleaned, errors = project__clean__data(request.POST, current_project=project)
        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"ویرایش «{project}»",
                    "backUrl": reverse("project:project_detail", kwargs={"id": project.id}),
                    "storeUrl": reverse("project:project_update", kwargs={"id": project.id}),
                    "items": project__form(project=project, raw_data=request.POST),
                }
            })

        try:
            project__store(cleaned, user=request.user, item=project)
        except ProjectError as e:
            response_msg(request, messages.ERROR, str(e))
            return redirect("project:project_detail", id=project.id)

        response_msg(request, messages.SUCCESS, "پروژه به‌روزرسانی شد")
        return redirect("project:project_detail", id=project.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": f"ویرایش «{project}»",
            "backUrl": reverse("project:project_detail", kwargs={"id": project.id}),
            "storeUrl": reverse("project:project_update", kwargs={"id": project.id}),
            "items": project__form(project=project),
        }
    })


# ═══════════════════════════════════════════════════════════
# DETAIL
# ═══════════════════════════════════════════════════════════
@is_admin_required
def project_detail(request, id):
    RequiredAccess(request, "ProjectRead")
    project = get_object_or_404(
        Project.objects.select_related("user", "approved_by"),
        id=id,
    )
    colleagues = project.colleagues.select_related("user").all()
    attachments = project.attachments.all()

    total_percent = project.colleagues.aggregate(t=__import__("django.db.models", fromlist=["Sum"]).Sum("percent"))["t"] or 0

    return render(request, "pages/project/project_detail.html", {
        "project": project,
        "colleagues": colleagues,
        "attachments": attachments,
        "total_percent": total_percent,
        "can_edit": project.status == Project.Status.PENDING,
        "can_approve": project.status == Project.Status.PENDING,
        "can_delete": project.status != Project.Status.APPROVED,
    })


# ═══════════════════════════════════════════════════════════
# DELETE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def project_delete(request, id):
    RequiredAccess(request, "ProjectDelete")
    if request.method != "POST":
        return redirect("project:project_index")

    try:
        project__delete(id, user=request.user, as_admin=True)
    except ProjectError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("project:project_detail", id=id)
    except Exception:
        logger.exception("project_delete failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در حذف")
        return redirect("project:project_detail", id=id)

    response_msg(request, messages.SUCCESS, "پروژه حذف شد")
    return redirect("project:project_index")


# ═══════════════════════════════════════════════════════════
# APPROVE / REJECT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def project_approve_action(request, id):
    RequiredAccess(request, "ProjectUpdate")
    if request.method != "POST":
        return redirect("project:project_detail", id=id)

    try:
        project__approve(id, admin=request.user)
    except ProjectError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("project:project_detail", id=id)
    except Exception:
        logger.exception("project_approve failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در تأیید")
        return redirect("project:project_detail", id=id)

    response_msg(request, messages.SUCCESS, "پروژه تأیید شد و امتیازها اعطا شدند")
    return redirect("project:project_detail", id=id)


@is_admin_required
def project_reject_action(request, id):
    RequiredAccess(request, "ProjectUpdate")
    if request.method != "POST":
        return redirect("project:project_detail", id=id)

    cleaned, errors = reject__clean__data(request.POST)
    if errors:
        for e in errors:
            response_msg(request, messages.ERROR, e)
        return redirect("project:project_detail", id=id)

    try:
        project__reject(id, admin=request.user, reason=cleaned["reason"])
    except ProjectError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("project:project_detail", id=id)
    except Exception:
        logger.exception("project_reject failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در رد")
        return redirect("project:project_detail", id=id)

    response_msg(request, messages.SUCCESS, "پروژه رد شد")
    return redirect("project:project_detail", id=id)


# ═══════════════════════════════════════════════════════════
# COLLEAGUE — Add / Delete
# ═══════════════════════════════════════════════════════════
@is_admin_required
def project_colleague_add(request, id):
    RequiredAccess(request, "ProjectUpdate")
    project = get_object_or_404(Project, id=id)

    if request.method == "POST":
        cleaned, errors = colleague__clean__data(request.POST)
        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"افزودن همکار به «{project}»",
                    "backUrl": reverse("project:project_detail", kwargs={"id": project.id}),
                    "storeUrl": reverse("project:project_colleague_add", kwargs={"id": project.id}),
                    "items": colleague__form(raw_data=request.POST),
                }
            })

        try:
            project__add_colleague(
                project.id, cleaned["user_mobile"], cleaned["percent"], as_admin=True,
            )
        except ProjectError as e:
            response_msg(request, messages.ERROR, str(e))
            return redirect("project:project_detail", id=project.id)

        response_msg(request, messages.SUCCESS, "همکار اضافه شد")
        return redirect("project:project_detail", id=project.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": f"افزودن همکار به «{project}»",
            "backUrl": reverse("project:project_detail", kwargs={"id": project.id}),
            "storeUrl": reverse("project:project_colleague_add", kwargs={"id": project.id}),
            "items": colleague__form(),
        }
    })


@is_admin_required
def project_colleague_delete(request, id, colleague_id):
    RequiredAccess(request, "ProjectUpdate")
    if request.method != "POST":
        return redirect("project:project_detail", id=id)

    try:
        project__remove_colleague(id, colleague_id, as_admin=True)
    except ProjectError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("project:project_detail", id=id)

    response_msg(request, messages.SUCCESS, "همکار حذف شد")
    return redirect("project:project_detail", id=id)


# ═══════════════════════════════════════════════════════════
# ATTACHMENT — Upload / Delete
# ═══════════════════════════════════════════════════════════
@is_admin_required
def project_attachment_upload(request, id):
    RequiredAccess(request, "ProjectUpdate")
    project = get_object_or_404(Project, id=id)

    if request.method == "POST":
        cleaned, errors = attachment__clean__data(request.POST, request.FILES)
        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"افزودن پیوست به «{project}»",
                    "backUrl": reverse("project:project_detail", kwargs={"id": project.id}),
                    "storeUrl": reverse("project:project_attachment_upload", kwargs={"id": project.id}),
                    "items": attachment__form(raw_data=request.POST),
                }
            })

        try:
            project__upload_attachment(
                project.id, request.user,
                file_type=cleaned["file_type"],
                upload=cleaned["file"],
                file_size=cleaned["file_size"],
                mime_type=cleaned["mime_type"],
                as_admin=True,
            )
        except ProjectError as e:
            response_msg(request, messages.ERROR, str(e))
            return redirect("project:project_detail", id=project.id)
        except Exception:
            logger.exception("attachment_upload failed id=%s", id)
            response_msg(request, messages.ERROR, "خطا در آپلود فایل")
            return redirect("project:project_detail", id=project.id)

        response_msg(request, messages.SUCCESS, "پیوست اضافه شد")
        return redirect("project:project_detail", id=project.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": f"افزودن پیوست به «{project}»",
            "backUrl": reverse("project:project_detail", kwargs={"id": project.id}),
            "storeUrl": reverse("project:project_attachment_upload", kwargs={"id": project.id}),
            "items": attachment__form(),
        }
    })


@is_admin_required
def project_attachment_delete(request, id, attachment_id):
    RequiredAccess(request, "ProjectUpdate")
    if request.method != "POST":
        return redirect("project:project_detail", id=id)

    try:
        project__remove_attachment(id, attachment_id, as_admin=True)
    except ProjectError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("project:project_detail", id=id)

    response_msg(request, messages.SUCCESS, "پیوست حذف شد")
    return redirect("project:project_detail", id=id)