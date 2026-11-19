# Path: applications/dashboard/views/reports.py

# applications/dashboard/views/reports.py

import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess

from ..repositories import (
    report_factors,
    report_gift_orders,
    report_projects,
    report_promotion_orders,
    report_scores,
    report_support,
    report_users,
    report_visit_requests,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Registry — هر گزارش با متادیتا
# ═══════════════════════════════════════════════════════════
REPORTS = {
    "users": {
        "title": "گزارش کاربران",
        "icon": "fe-users",
        "repo": report_users,
        "columns": [
            ("id", "شناسه"),
            ("full_name", "نام"),
            ("mobile", "موبایل"),
            ("nature_display", "نوع"),
            ("score_balance", "موجودی"),
            ("score_earned", "کل کسب"),
            ("is_active_display", "وضعیت"),
            ("verified_display", "موبایل"),
            ("date_joined_display", "تاریخ عضویت"),
        ],
        "row_builder": lambda u: [
            u.id,
            u.full_name or "",
            u.mobile or "",
            u.get_nature_display(),
            getattr(getattr(u, "relation_score", None), "current_balance", 0) or 0,
            getattr(getattr(u, "relation_score", None), "total_earned", 0) or 0,
            "فعال" if u.is_active else "غیرفعال",
            "تایید" if u.is_mobile_verified else "تایید نشده",
            u.date_joined.strftime("%Y-%m-%d") if u.date_joined else "",
        ],
        "template": "pages/dashboard/reports/users.html",
        "filters": ["q", "date_from", "date_to"],
        "date_field": "تاریخ عضویت",
    },
    "scores": {
        "title": "گزارش امتیازات",
        "icon": "fe-star",
        "repo": report_scores,
        "columns": [
            ("id", "#"),
            ("user", "کاربر"),
            ("code", "کد"),
            ("direction", "جهت"),
            ("amount", "مقدار"),
            ("balance", "قبل → بعد"),
            ("reason", "دلیل"),
            ("created_at", "تاریخ"),
        ],
        "row_builder": lambda r: [
            r.id,
            f"{r.user.full_name} ({r.user.mobile})" if r.user else "",
            r.get_transaction_code_display(),
            r.get_direction_display(),
            r.amount,
            f"{r.balance_before} → {r.balance_after}",
            r.reason or "",
            r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "",
        ],
        "template": "pages/dashboard/reports/scores.html",
        "filters": ["q", "direction", "date_from", "date_to"],
        "date_field": "تاریخ تراکنش",
    },
    "gift_orders": {
        "title": "گزارش سفارشات هدیه",
        "icon": "fe-gift",
        "repo": report_gift_orders,
        "columns": [
            ("id", "#"),
            ("user", "کاربر"),
            ("gift", "هدیه"),
            ("quantity", "تعداد"),
            ("azar_value", "ارزش آذری"),
            ("receiver", "گیرنده"),
            ("status", "وضعیت"),
            ("created_at", "تاریخ"),
        ],
        "row_builder": lambda o: [
            o.id,
            f"{o.user.full_name} ({o.user.mobile})" if o.user else "",
            o.gift.title if o.gift else "",
            o.quantity,
            o.total_azar_value,
            f"{o.receiver_name} — {o.receiver_phone}",
            o.get_status_display(),
            o.created_at.strftime("%Y-%m-%d %H:%M") if o.created_at else "",
        ],
        "template": "pages/dashboard/reports/gift_orders.html",
        "filters": ["q", "status", "date_from", "date_to"],
        "date_field": "تاریخ ثبت",
    },
    "promotion_orders": {
        "title": "گزارش سفارشات اقلام تبلیغاتی",
        "icon": "fe-package",
        "repo": report_promotion_orders,
        "columns": [
            ("id", "#"),
            ("user", "کاربر"),
            ("promotion", "پک"),
            ("receiver", "گیرنده"),
            ("status", "وضعیت"),
            ("tracking", "رهگیری"),
            ("created_at", "تاریخ"),
        ],
        "row_builder": lambda o: [
            o.id,
            f"{o.user.full_name} ({o.user.mobile})" if o.user else "",
            o.promotion.title if o.promotion else "",
            f"{o.receiver_name} — {o.receiver_phone}",
            o.get_status_display(),
            o.tracking_code or "—",
            o.created_at.strftime("%Y-%m-%d %H:%M") if o.created_at else "",
        ],
        "template": "pages/dashboard/reports/promotion_orders.html",
        "filters": ["q", "status", "date_from", "date_to"],
        "date_field": "تاریخ ثبت",
    },
    "projects": {
        "title": "گزارش پروژه‌ها",
        "icon": "fe-briefcase",
        "repo": report_projects,
        "columns": [
            ("id", "#"),
            ("type", "نوع"),
            ("title", "عنوان"),
            ("user", "صاحب"),
            ("status", "وضعیت"),
            ("address", "آدرس"),
            ("created_at", "تاریخ"),
        ],
        "row_builder": lambda p: [
            p.id,
            p.get_type_display(),
            p.title or "—",
            f"{p.user.full_name} ({p.user.mobile})" if p.user else "",
            p.get_status_display(),
            p.address or "",
            p.created_at.strftime("%Y-%m-%d %H:%M") if p.created_at else "",
        ],
        "template": "pages/dashboard/reports/projects.html",
        "filters": ["q", "status", "date_from", "date_to"],
        "date_field": "تاریخ ایجاد",
    },
    "factors": {
        "title": "گزارش فاکتورها",
        "icon": "fe-file-text",
        "repo": report_factors,
        "columns": [
            ("id", "#"),
            ("invoice_number", "شماره"),
            ("user", "کاربر"),
            ("amount", "مبلغ (ریال)"),
            ("shop", "فروشگاه"),
            ("status", "وضعیت"),
            ("created_at", "تاریخ"),
        ],
        "row_builder": lambda f: [
            f.id,
            f.invoice_number or "",
            f"{f.user.full_name} ({f.user.mobile})" if f.user else "",
            f.amount or 0,
            f.shop_name or "",
            f.get_status_display(),
            f.created_at.strftime("%Y-%m-%d %H:%M") if f.created_at else "",
        ],
        "template": "pages/dashboard/reports/factors.html",
        "filters": ["q", "status", "date_from", "date_to"],
        "date_field": "تاریخ ثبت",
    },
    "visit_requests": {
        "title": "گزارش درخواست‌های بازدید",
        "icon": "fe-calendar",
        "repo": report_visit_requests,
        "columns": [
            ("id", "#"),
            ("user", "کاربر"),
            ("visit", "بازدید"),
            ("companion", "همراه"),
            ("status", "وضعیت"),
            ("created_at", "تاریخ"),
        ],
        "row_builder": lambda v: [
            v.id,
            f"{v.user.full_name} ({v.user.mobile})" if v.user else "",
            f"#{v.visit.id} — {v.visit.date.strftime('%Y-%m-%d')}" if v.visit else "",
            "با همراه" if v.have_companion else "بدون همراه",
            v.get_status_display(),
            v.created_at.strftime("%Y-%m-%d %H:%M") if v.created_at else "",
        ],
        "template": "pages/dashboard/reports/visit_requests.html",
        "filters": ["q", "status", "date_from", "date_to"],
        "date_field": "تاریخ درخواست",
    },
    "support": {
        "title": "گزارش تیکت‌های پشتیبانی",
        "icon": "fe-life-buoy",
        "repo": report_support,
        "columns": [
            ("id", "#"),
            ("subject", "موضوع"),
            ("user", "کاربر"),
            ("category", "دسته"),
            ("priority", "اولویت"),
            ("status", "وضعیت"),
            ("created_at", "تاریخ"),
        ],
        "row_builder": lambda s: [
            s.id,
            s.subject,
            f"{s.user.full_name} ({s.user.mobile})" if s.user else "",
            s.get_category_display(),
            s.get_priority_display(),
            s.get_status_display(),
            s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "",
        ],
        "template": "pages/dashboard/reports/support.html",
        "filters": ["q", "status", "date_from", "date_to"],
        "date_field": "تاریخ ایجاد",
    },
}


# ═══════════════════════════════════════════════════════════
# REPORT VIEW
# ═══════════════════════════════════════════════════════════
@is_admin_required
def report_view(request, report_type):
    # RequiredAccess(request, "ReportRead")

    meta = REPORTS.get(report_type)
    if not meta:
        from django.http import Http404
        raise Http404("گزارش یافت نشد")

    qs = meta["repo"](request)

    # Pagination
    from django.core.paginator import Paginator
    try:
        count = int(request.GET.get("count", "50"))
    except ValueError:
        count = 50
    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": meta["title"],
        "reportType": report_type,
        "reportTitle": meta["title"],
        "icon": meta["icon"],
        "columns": meta["columns"],
        "page": page,
        "total": paginator.count,
        "searchCount": count,
        "request_get": request.GET,
        "template": meta["template"],
        "filters": meta["filters"],
        "dateField": meta["date_field"],
        "exportUrl": reverse("app_dashboard:report_export", args=[report_type]),
        "reports_list": [
            {"key": k, "title": v["title"], "icon": v["icon"]}
            for k, v in REPORTS.items()
        ],
    }
    return render(request, "pages/dashboard/reports/report.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def report_export(request, report_type):
    # RequiredAccess(request, "ReportRead")

    meta = REPORTS.get(report_type)
    if not meta:
        from django.http import Http404
        raise Http404("گزارش یافت نشد")

    qs = meta["repo"](request)

    wb = Workbook()
    ws = wb.active
    ws.title = meta["title"][:30]
    ws.sheet_view.rightToLeft = True

    # Headers
    headers = [label for _key, label in meta["columns"]]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for c in ws[1]:
        c.font = head_font
        c.fill = head_fill
        c.alignment = Alignment(horizontal="center", vertical="center")

    # Rows
    for obj in qs.iterator():
        ws.append(meta["row_builder"](obj))

    # Column widths
    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"{report_type}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    resp = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(resp)
    return resp