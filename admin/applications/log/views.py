import json
from urllib.parse import urlencode
from datetime import timedelta

from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse

from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess
from applications.log.models import RequestLog


METHOD_FA = {
    "GET": "مشاهده",
    "POST": "ایجاد",
    "PUT": "ویرایش",
    "PATCH": "ویرایش",
    "DELETE": "حذف",
}

DEVICE_FA = {
    "Desktop": "دسکتاپ",
    "Mobile": "موبایل",
    "Tablet": "تبلت",
}

STATUS_FA = {
    range(200, 300): ("موفق", "success"),
    range(300, 400): ("تغییر مسیر", "info"),
    range(400, 500): ("خطای کلاینت", "warning"),
    range(500, 600): ("خطای سرور", "danger"),
}

COUNT_OPTIONS = [10, 20, 50, 100]


def _status_meta(code):
    if code is None:
        return ("نامشخص", "secondary")
    for rng, meta in STATUS_FA.items():
        if code in rng:
            return meta
    return ("نامشخص", "secondary")


def _build_paginate_url(params: dict) -> str:
    clean = {k: v for k, v in params.items() if v not in (None, "")}
    if not clean:
        return ""
    return urlencode(clean) + "&"


@is_admin_required
def index(request):
    RequiredAccess(request, "LogRead")

    data = {}
    data["pageTitle"] = "لاگ سیستم"
    data["newUrl"] = ""
    data["searchUrl"] = reverse("log:index")

    qs = RequestLog.objects.select_related("user").all()

    q = (request.GET.get("q") or "").strip()
    method = (request.GET.get("method") or "").strip()
    module = (request.GET.get("module") or "").strip()
    success = request.GET.get("success")
    date_from = request.GET.get("from") or ""
    date_to = request.GET.get("to") or ""
    sort = request.GET.get("sort") or "desc"
    count = request.GET.get("count")
    data["searchCount"] = int(count) if (count and count.isnumeric()) else 10
    if data["searchCount"] not in COUNT_OPTIONS:
        data["searchCount"] = 10

    if q:
        qs = qs.filter(
            Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__mobile__icontains=q)
            | Q(ip__icontains=q)
            | Q(path__icontains=q)
            | Q(view_name__icontains=q)
            | Q(module__icontains=q)
            | Q(action__icontains=q)
            | Q(os__icontains=q)
            | Q(device__icontains=q)
            | Q(browser__icontains=q)
            | Q(error_message__icontains=q)
        )

    if method:
        qs = qs.filter(method=method.upper())

    if module:
        qs = qs.filter(module=module)

    if success in ("0", "1"):
        qs = qs.filter(success=(success == "1"))

    if date_from:
        qs = qs.filter(created__date__gte=date_from)

    if date_to:
        qs = qs.filter(created__date__lte=date_to)

    qs = qs.order_by("id") if sort == "asc" else qs.order_by("-id")

    data["paginateUrl"] = _build_paginate_url({
        "q": q,
        "method": method,
        "module": module,
        "success": success,
        "from": date_from,
        "to": date_to,
        "sort": sort,
        "count": data["searchCount"],
    })

    paginator = Paginator(qs, data["searchCount"])
    page = paginator.get_page(request.GET.get("page"))
    data["all"] = page  # 👈 رفع باگ: page به data.all وصل شود

    rows = []
    for log in page:
        fa_status, status_cls = _status_meta(log.status_code)
        rows.append({
            "obj": log,
            "user": str(log.user) if log.user else "مهمان",
            "user_id": log.user_id,
            "is_authenticated": log.is_authenticated,
            "method": log.method,
            "methodFa": METHOD_FA.get(log.method, log.method),
            "path": log.path,
            "full_path": log.full_path,
            "view_name": log.view_name or "-",
            "module": log.module or "-",
            "action": log.action or "-",
            "status": log.status_code,
            "statusFa": fa_status,
            "statusCls": status_cls,
            "success": log.success,
            "error": log.error_message,
            "ip": log.ip or "-",
            "os": log.os or "-",
            "device": DEVICE_FA.get(log.device, log.device) if log.device else "-",
            "browser": log.browser or "-",
            "duration": log.duration_ms,
            "created": log.created,
            "is_api": log.is_api,
            "is_ajax": log.is_ajax,
            "query": log.query_params,
            "body": log.body_params,
            "referer": log.referer,
        })

    data["rows"] = rows
    data["total"] = qs.count()
    data["searchText"] = q
    data["searchSort"] = sort
    data["searchMethod"] = method
    data["searchModule"] = module
    data["searchSuccess"] = success or ""
    data["searchFrom"] = date_from
    data["searchTo"] = date_to

    data["methods"] = list(
        RequestLog.objects.values_list("method", flat=True).distinct().order_by("method")
    )
    data["modules"] = list(
        RequestLog.objects.exclude(module__isnull=True)
        .exclude(module="")
        .values_list("module", flat=True)
        .distinct()
        .order_by("module")
    )
    data["countOptions"] = COUNT_OPTIONS  # 👈 رفع باگ: split در قالب

    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    data["stats"] = {
        "total": RequestLog.objects.count(),
        "today": RequestLog.objects.filter(created__date=today).count(),
        "week": RequestLog.objects.filter(created__date__gte=week_ago).count(),
        "errors": RequestLog.objects.filter(success=False).count(),
        "guests": RequestLog.objects.filter(is_authenticated=False).count(),
    }

    return render(request, "pages/logs.html", {"data": data})


@is_admin_required
def details(request, id):
    RequiredAccess(request, "LogRead")
    log = get_object_or_404(RequestLog, pk=id)
    return JsonResponse({
        "id": log.id,
        "user": str(log.user) if log.user else "مهمان",
        "user_id": log.user_id,
        "is_authenticated": log.is_authenticated,
        "method": log.method,
        "path": log.path,
        "full_path": log.full_path,
        "view_name": log.view_name,
        "module": log.module,
        "action": log.action,
        "status_code": log.status_code,
        "success": log.success,
        "error_message": log.error_message,
        "ip": log.ip,
        "browser": log.browser,
        "os": log.os,
        "device": log.device,
        "is_ajax": log.is_ajax,
        "is_api": log.is_api,
        "referer": log.referer,
        "session_key": log.session_key,
        "created": log.created.strftime("%Y/%m/%d %H:%M:%S") if log.created else "",
        "duration_ms": log.duration_ms,
        "query_params": log.query_params,
        "body_params": log.body_params,
    })