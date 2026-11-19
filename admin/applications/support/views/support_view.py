# Path: applications/support/views/support_view.py

# applications/support/views/support_view.py

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

from ..clean_data import (
    close__clean__data,
    message__clean__data,
    support__clean__data,
    support__clean__update__data,
)
from ..forms import (
    support__filters,
    support__form,
    support__update__form,
)
from ..models import Support, SupportMessage
from ..repositories import (
    support__available_transitions,
    support__change_status,
    support__close,
    support__delete,
    support__mark_user_messages_as_read,
    support__send_admin_message,
    support__store,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Filter helper
# ═══════════════════════════════════════════════════════════
def _filtered_supports_qs(request):
    qs = (
        Support.objects
        .select_related("user", "closed_by")
        .annotate(msg_count=Count("messages", distinct=True))
    )

    q = (request.GET.get("q") or "").strip()
    if q:
        cond = (
            Q(subject__icontains=q)
            | Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__mobile__icontains=q)
            | Q(messages__text__icontains=q)
        )
        if q.isdigit():
            cond |= Q(id=int(q))
        qs = qs.filter(cond).distinct()

    status = (request.GET.get("status") or "").strip()
    if status in dict(Support.Status.choices):
        qs = qs.filter(status=status)

    category = (request.GET.get("category") or "").strip()
    if category in dict(Support.Category.choices):
        qs = qs.filter(category=category)

    priority = (request.GET.get("priority") or "").strip()
    if priority in dict(Support.Priority.choices):
        qs = qs.filter(priority=priority)

    has_unread = (request.GET.get("has_unread") or "").strip()
    if has_unread == "1":
        qs = qs.filter(messages__is_admin_reply=False, messages__is_read=False).distinct()

    cf = request.GET.get("created_from")
    ct = request.GET.get("created_to")
    if cf:
        qs = qs.filter(created_at__date__gte=cf)
    if ct:
        qs = qs.filter(created_at__date__lte=ct)

    sort = request.GET.get("sort", "last_desc")
    if sort == "last_asc":
        qs = qs.order_by("last_message_at")
    elif sort == "created_desc":
        qs = qs.order_by("-created_at")
    elif sort == "created_asc":
        qs = qs.order_by("created_at")
    else:
        qs = qs.order_by("-last_message_at")

    return qs


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def support_index(request):
    RequiredAccess(request, "SupportRead")
    qs = _filtered_supports_qs(request)

    try:
        count = int(request.GET.get("count", "20"))
    except ValueError:
        count = 20

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": "تیکت‌های پشتیبانی",
        "newUrl": reverse("app_support:support_create"),
        "searchUrl": reverse("app_support:support_index"),
        "exportUrl": reverse("app_support:support_export"),
        "filters": support__filters(get_data=request.GET),
        "showAdvanced": bool(request.GET.get("created_from") or request.GET.get("created_to")),
        "searchCount": count,
        "all": page,
        "total": paginator.count,
    }
    return render(request, "pages/support/all_supports.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def support_export(request):
    RequiredAccess(request, "SupportRead")
    qs = _filtered_supports_qs(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "تیکت‌های پشتیبانی"
    ws.sheet_view.rightToLeft = True

    headers = [
        "#", "موضوع", "کاربر", "موبایل", "دسته‌بندی",
        "اولویت", "وضعیت", "تعداد پیام", "آخرین پیام",
        "تاریخ ایجاد", "بسته‌کننده", "دلیل بستن",
    ]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for c in ws[1]:
        c.font = head_font
        c.fill = head_fill
        c.alignment = Alignment(horizontal="center", vertical="center")

    for s in qs.iterator():
        ws.append([
            s.id,
            s.subject,
            s.user.full_name if s.user else "",
            s.user.mobile if s.user else "",
            s.get_category_display(),
            s.get_priority_display(),
            s.get_status_display(),
            s._msg_count,
            s.last_message_at.strftime("%Y-%m-%d %H:%M") if s.last_message_at else "",
            s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "",
            s.closed_by.full_name if s.closed_by else "",
            s.close_reason or "",
        ])

    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"supports_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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
def support_create(request):
    RequiredAccess(request, "SupportCreate")

    if request.method == "POST":
        cleaned, errors = support__clean__data(request.POST, request.FILES)
        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد تیکت پشتیبانی",
                    "backUrl": reverse("app_support:support_index"),
                    "storeUrl": reverse("app_support:support_create"),
                    "items": support__form(raw_data=request.POST),
                }
            })

        try:
            ticket = support__store(cleaned=cleaned)
        except Exception:
            logger.exception("support_create failed")
            response_msg(request, messages.ERROR, "خطا در ذخیره تیکت")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد تیکت پشتیبانی",
                    "backUrl": reverse("app_support:support_index"),
                    "storeUrl": reverse("app_support:support_create"),
                    "items": support__form(raw_data=request.POST),
                }
            })

        response_msg(request, messages.SUCCESS, "تیکت ایجاد شد")
        return redirect("app_support:support_detail", id=ticket.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ایجاد تیکت پشتیبانی",
            "backUrl": reverse("app_support:support_index"),
            "storeUrl": reverse("app_support:support_create"),
            "items": support__form(),
        }
    })


# ═══════════════════════════════════════════════════════════
# UPDATE — فقط subject/category/priority
# ═══════════════════════════════════════════════════════════
@is_admin_required
def support_update(request, id):
    RequiredAccess(request, "SupportUpdate")
    ticket = get_object_or_404(Support, id=id)

    if ticket.status == Support.Status.CLOSED:
        response_msg(request, messages.ERROR, "تیکت بسته‌شده قابل ویرایش نیست")
        return redirect("app_support:support_detail", id=ticket.id)

    if request.method == "POST":
        cleaned, errors = support__clean__update__data(request.POST)
        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"ویرایش «{ticket.subject}»",
                    "backUrl": reverse("app_support:support_detail", kwargs={"id": ticket.id}),
                    "storeUrl": reverse("app_support:support_update", kwargs={"id": ticket.id}),
                    "items": support__update__form(ticket, raw_data=request.POST),
                }
            })

        ticket.category = cleaned["category"]
        ticket.priority = cleaned["priority"]
        ticket.subject = cleaned["subject"]
        ticket.save(update_fields=["category", "priority", "subject", "updated_at"])

        response_msg(request, messages.SUCCESS, "تیکت به‌روزرسانی شد")
        return redirect("app_support:support_detail", id=ticket.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": f"ویرایش «{ticket.subject}»",
            "backUrl": reverse("app_support:support_detail", kwargs={"id": ticket.id}),
            "storeUrl": reverse("app_support:support_update", kwargs={"id": ticket.id}),
            "items": support__update__form(ticket),
        }
    })


# ═══════════════════════════════════════════════════════════
# DETAIL — Chat view
# ═══════════════════════════════════════════════════════════
@is_admin_required
def support_detail(request, id):
    RequiredAccess(request, "SupportRead")

    ticket = get_object_or_404(
        Support.objects.select_related("user", "closed_by"),
        id=id,
    )

    # علامت خوانده‌شده برای پیام‌های کاربر
    support__mark_user_messages_as_read(ticket.id)

    # پیام‌ها — همه‌ی پیام‌ها
    chat_messages = (
        SupportMessage.objects
        .filter(ticket=ticket)
        .select_related("sender")
        .order_by("created_at")
    )

    # شمارش پیام‌های خوانده‌نشده قبلی (قبل از نشانه‌گذاری)، برای نمایش flash
    unread_count = 0  # چون همه mark شدند، صفر است — برای سازگاری نگه داشته شد

    return render(request, "pages/support/support_detail.html", {
        "ticket": ticket,
        "chat_messages": chat_messages,
        "transitions": support__available_transitions(ticket),
        "is_closed": ticket.status == Support.Status.CLOSED,
        "is_open": ticket.is_open(),
    })


# ═══════════════════════════════════════════════════════════
# DELETE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def support_delete(request, id):
    RequiredAccess(request, "SupportDelete")
    if request.method != "POST":
        return redirect("app_support:support_index")

    try:
        support__delete(id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_support:support_detail", id=id)
    except Exception:
        logger.exception("support_delete failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در حذف")
        return redirect("app_support:support_detail", id=id)

    response_msg(request, messages.SUCCESS, "تیکت حذف شد")
    return redirect("app_support:support_index")


# ═══════════════════════════════════════════════════════════
# CHANGE STATUS
# ═══════════════════════════════════════════════════════════
@is_admin_required
def support_change_status(request, id):
    RequiredAccess(request, "SupportUpdate")
    if request.method != "POST":
        return redirect("app_support:support_detail", id=id)

    new_status = (request.POST.get("new_status") or "").strip()
    if new_status not in dict(Support.Status.choices):
        response_msg(request, messages.ERROR, "وضعیت نامعتبر است")
        return redirect("app_support:support_detail", id=id)

    try:
        support__change_status(id, new_status)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_support:support_detail", id=id)
    except Exception:
        logger.exception("support_change_status failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در تغییر وضعیت")
        return redirect("app_support:support_detail", id=id)

    response_msg(request, messages.SUCCESS, "وضعیت تیکت به‌روزرسانی شد")
    return redirect("app_support:support_detail", id=id)


# ═══════════════════════════════════════════════════════════
# CLOSE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def support_close(request, id):
    RequiredAccess(request, "SupportUpdate")
    if request.method != "POST":
        return redirect("app_support:support_detail", id=id)

    cleaned, errors = close__clean__data(request.POST)
    if errors:
        for e in errors:
            response_msg(request, messages.ERROR, e)
        return redirect("app_support:support_detail", id=id)

    try:
        support__close(id, closed_by=request.user, reason=cleaned["reason"])
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_support:support_detail", id=id)
    except Exception:
        logger.exception("support_close failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در بستن تیکت")
        return redirect("app_support:support_detail", id=id)

    response_msg(request, messages.SUCCESS, "تیکت بسته شد")
    return redirect("app_support:support_detail", id=id)


# ═══════════════════════════════════════════════════════════
# SEND MESSAGE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def support_send_message(request, id):
    RequiredAccess(request, "SupportUpdate")
    if request.method != "POST":
        return redirect("app_support:support_detail", id=id)

    cleaned, errors = message__clean__data(request.POST, request.FILES)
    if errors:
        for e in errors:
            response_msg(request, messages.ERROR, e)
        return redirect("app_support:support_detail", id=id)

    try:
        support__send_admin_message(
            id, sender=request.user,
            text=cleaned["text"],
            upload=cleaned.get("file"),
        )
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_support:support_detail", id=id)
    except Exception:
        logger.exception("support_send_message failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در ارسال پیام")
        return redirect("app_support:support_detail", id=id)

    return redirect("app_support:support_detail", id=id)