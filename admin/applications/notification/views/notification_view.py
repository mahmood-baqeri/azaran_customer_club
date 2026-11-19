# Path: applications/notification/views/notification_view.py

# applications/notification/views/notification_view.py

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

from ..clean_data import notification__clean__data
from ..forms import notification__form, notification__filters
from ..models import Notification, NotificationState
from ..repositories import (
    notification__cancel,
    notification__delete,
    notification__send,
    notification__store,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Filter helper — مشترک بین list و export
# ═══════════════════════════════════════════════════════════
def _filtered_notifications_qs(request):
    qs = Notification.objects.select_related("created_by")

    q = (request.GET.get("q") or "").strip()
    if q:
        cond = (
            Q(title__icontains=q)
            | Q(body__icontains=q)
            | Q(targets__user__first_name__icontains=q)
            | Q(targets__user__last_name__icontains=q)
            | Q(targets__user__mobile__icontains=q)
        )
        if q.isdigit():
            cond |= Q(id=int(q))
        qs = qs.filter(cond).distinct()

    status = (request.GET.get("status") or "").strip()
    if status in dict(Notification.Status.choices):
        qs = qs.filter(status=status)

    target_type = (request.GET.get("target_type") or "").strip()
    if target_type in dict(Notification.TargetType.choices):
        qs = qs.filter(target_type=target_type)

    notif_type = (request.GET.get("notification_type") or "").strip()
    if notif_type in dict(Notification.NotificationType.choices):
        qs = qs.filter(notification_type=notif_type)

    priority = (request.GET.get("priority") or "").strip()
    if priority in dict(Notification.Priority.choices):
        qs = qs.filter(priority=priority)

    sent_from = request.GET.get("sent_from")
    sent_to = request.GET.get("sent_to")
    if sent_from:
        qs = qs.filter(sent_at__date__gte=sent_from)
    if sent_to:
        qs = qs.filter(sent_at__date__lte=sent_to)

    created_from = request.GET.get("created_from")
    created_to = request.GET.get("created_to")
    if created_from:
        qs = qs.filter(created_at__date__gte=created_from)
    if created_to:
        qs = qs.filter(created_at__date__lte=created_to)

    sort = request.GET.get("sort", "desc")
    if sort == "asc":
        qs = qs.order_by("created_at")
    elif sort == "sent_desc":
        qs = qs.order_by("-sent_at")
    else:
        qs = qs.order_by("-created_at")

    return qs


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def notification_index(request):
    RequiredAccess(request, "NotificationRead")

    qs = _filtered_notifications_qs(request)

    try:
        count = int(request.GET.get("count", "20"))
    except ValueError:
        count = 20

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": "نوتیفیکیشن‌ها",
        "newUrl": reverse("notification:notification_create"),
        "searchUrl": reverse("notification:notification_index"),
        "exportUrl": reverse("notification:notification_export"),
        "filters": notification__filters(get_data=request.GET),
        "showAdvanced": any(
            request.GET.get(k)
            for k in ("sent_from", "sent_to", "created_from", "created_to")
        ),
        "searchCount": count,
        "all": page,
        "total": paginator.count,
    }
    return render(request, "pages/notification/all_notifications.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def notification_export(request):
    RequiredAccess(request, "NotificationRead")

    qs = _filtered_notifications_qs(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "نوتیفیکیشن‌ها"
    ws.sheet_view.rightToLeft = True

    headers = [
        "#", "عنوان", "متن", "نوع هدف‌گیری", "نوع نوتیفیکیشن",
        "اولویت", "وضعیت", "تعداد گیرندگان", "تعداد خوانده",
        "نرخ خواندن ٪", "زمان ارسال", "زمان انقضا",
        "نوع اقدام", "سازنده", "تاریخ ایجاد",
    ]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for cell in ws[1]:
        cell.font = head_font
        cell.fill = head_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for n in qs.iterator():
        rate = (
            round((n.total_reads / n.total_recipients) * 100, 1)
            if n.total_recipients else 0
        )
        ws.append([
            n.id,
            n.title,
            (n.body or "")[:200],
            n.get_target_type_display(),
            n.get_notification_type_display(),
            n.get_priority_display(),
            n.get_status_display(),
            n.total_recipients,
            n.total_reads,
            rate,
            n.sent_at.strftime("%Y-%m-%d %H:%M") if n.sent_at else "",
            n.expires_at.strftime("%Y-%m-%d %H:%M") if n.expires_at else "",
            n.action_type or "",
            (n.created_by.full_name if n.created_by else "") or "",
            n.created_at.strftime("%Y-%m-%d %H:%M") if n.created_at else "",
        ])

    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"notifications_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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
def notification_create(request):
    RequiredAccess(request, "NotificationCreate")

    if request.method == "POST":
        cleaned, errors = notification__clean__data(request.POST, request.FILES)

        if errors:
            for err in errors:
                response_msg(request, messages.ERROR, err)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد نوتیفیکیشن",
                    "backUrl": reverse("notification:notification_index"),
                    "storeUrl": reverse("notification:notification_create"),
                    "items": notification__form(raw_data=request.POST),
                    "extraJs": _target_toggle_js(),
                }
            })

        try:
            n = notification__store(request, cleaned=cleaned)
        except Exception:
            logger.exception("notification_create failed")
            response_msg(request, messages.ERROR, "خطا در ذخیره نوتیفیکیشن")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد نوتیفیکیشن",
                    "backUrl": reverse("notification:notification_index"),
                    "storeUrl": reverse("notification:notification_create"),
                    "items": notification__form(raw_data=request.POST),
                    "extraJs": _target_toggle_js(),
                }
            })

        response_msg(request, messages.SUCCESS, "نوتیفیکیشن ایجاد شد")
        return redirect("notification:notification_detail", id=n.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ایجاد نوتیفیکیشن",
            "backUrl": reverse("notification:notification_index"),
            "storeUrl": reverse("notification:notification_create"),
            "items": notification__form(),
            "extraJs": _target_toggle_js(),
        }
    })


# ═══════════════════════════════════════════════════════════
# UPDATE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def notification_update(request, id):
    RequiredAccess(request, "NotificationUpdate")
    n = get_object_or_404(Notification, id=id)

    if n.status == Notification.Status.SENT:
        response_msg(request, messages.ERROR, "نوتیفیکیشن ارسال‌شده قابل ویرایش نیست")
        return redirect("notification:notification_detail", id=n.id)

    if request.method == "POST":
        cleaned, errors = notification__clean__data(request.POST, request.FILES)

        if errors:
            for err in errors:
                response_msg(request, messages.ERROR, err)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"ویرایش «{n.title}»",
                    "backUrl": reverse("notification:notification_detail", kwargs={"id": n.id}),
                    "storeUrl": reverse("notification:notification_update", kwargs={"id": n.id}),
                    "items": notification__form(notification=n, raw_data=request.POST),
                    "extraJs": _target_toggle_js(),
                }
            })

        try:
            notification__store(request, cleaned=cleaned, item=n)
        except Exception:
            logger.exception("notification_update failed id=%s", id)
            response_msg(request, messages.ERROR, "خطا در ذخیره تغییرات")
            return redirect("notification:notification_detail", id=n.id)

        response_msg(request, messages.SUCCESS, "نوتیفیکیشن به‌روزرسانی شد")
        return redirect("notification:notification_detail", id=n.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": f"ویرایش «{n.title}»",
            "backUrl": reverse("notification:notification_detail", kwargs={"id": n.id}),
            "storeUrl": reverse("notification:notification_update", kwargs={"id": n.id}),
            "items": notification__form(notification=n),
            "extraJs": _target_toggle_js(),
        }
    })


# ═══════════════════════════════════════════════════════════
# DELETE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def notification_delete(request, id):
    RequiredAccess(request, "NotificationDelete")
    if request.method != "POST":
        response_msg(request, messages.ERROR, "درخواست نامعتبر")
        return redirect("notification:notification_index")

    n = get_object_or_404(Notification, id=id)
    try:
        notification__delete(n)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("notification:notification_detail", id=n.id)
    except Exception:
        logger.exception("notification_delete failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در حذف")
        return redirect("notification:notification_detail", id=n.id)

    response_msg(request, messages.SUCCESS, "نوتیفیکیشن حذف شد")
    return redirect("notification:notification_index")


# ═══════════════════════════════════════════════════════════
# DETAIL
# ═══════════════════════════════════════════════════════════
@is_admin_required
def notification_detail(request, id):
    RequiredAccess(request, "NotificationRead")
    n = get_object_or_404(
        Notification.objects.select_related("created_by"),
        id=id,
    )

    # گیرندگان (اگر target_type=ALL خالی است)
    targets = (
        n.targets.select_related("user").all()
        if n.target_type != Notification.TargetType.ALL
        else []
    )

    # state های خوانده‌شده این نوتیفیکیشن
    read_states = (
        NotificationState.objects
        .filter(notification=n, is_read=True)
        .select_related("user")
        .order_by("-read_at")[:50]
    )
    read_state_user_ids = set(read_states.values_list("user_id", flat=True))

    # annotate read status روی targets
    for t in targets:
        t.is_read_by_user = t.user_id in read_state_user_ids

    read_rate = (
        round((n.total_reads / n.total_recipients) * 100, 1)
        if n.total_recipients else 0
    )

    return render(request, "pages/notification/notification_detail.html", {
        "n": n,
        "targets": targets,
        "read_states": read_states,
        "read_rate": read_rate,
        "can_edit": n.status != Notification.Status.SENT,
        "can_send": n.status in (
            Notification.Status.DRAFT,
            Notification.Status.SCHEDULED,
        ),
        "can_cancel": n.status in (
            Notification.Status.DRAFT,
            Notification.Status.SCHEDULED,
        ),
        "can_delete": n.status != Notification.Status.SENT,
    })


# ═══════════════════════════════════════════════════════════
# ACTION — Send
# ═══════════════════════════════════════════════════════════
@is_admin_required
def notification_send_action(request, id):
    RequiredAccess(request, "NotificationUpdate")
    if request.method != "POST":
        return redirect("notification:notification_detail", id=id)

    n = get_object_or_404(Notification, id=id)
    try:
        notification__send(n)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("notification:notification_detail", id=id)
    except Exception:
        logger.exception("notification_send failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در ارسال")
        return redirect("notification:notification_detail", id=id)

    response_msg(request, messages.SUCCESS, f"نوتیفیکیشن به {n.total_recipients} کاربر ارسال شد")
    return redirect("notification:notification_detail", id=id)


# ═══════════════════════════════════════════════════════════
# ACTION — Cancel
# ═══════════════════════════════════════════════════════════
@is_admin_required
def notification_cancel_action(request, id):
    RequiredAccess(request, "NotificationUpdate")
    if request.method != "POST":
        return redirect("notification:notification_detail", id=id)

    n = get_object_or_404(Notification, id=id)
    try:
        notification__cancel(n)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("notification:notification_detail", id=id)

    response_msg(request, messages.SUCCESS, "نوتیفیکیشن لغو شد")
    return redirect("notification:notification_detail", id=id)


# ═══════════════════════════════════════════════════════════
# Helper — JS برای toggle کردن گیرندگان
# ═══════════════════════════════════════════════════════════
def _target_toggle_js():
    return """
        jQuery(function($) {
            function toggleTargets() {
                var val = $('#id_target_type').val();
                var $box = $('#id_target_users').closest('.form-group');
                if (val === 'all') {
                    $box.slideUp(150);
                } else {
                    $box.slideDown(150);
                }
            }
            $('#id_target_type').on('change', toggleTargets);
            toggleTargets();
        });
    """