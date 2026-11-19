# Path: applications/score/views/score_rule_view.py

# applications/score/view/score_rule_view.py

import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import HttpResponse
from django.utils import timezone

from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess
from applications.core.utils import redirect_back, response_msg
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from ..clean_data import score_rule__clean__data
from ..forms import rule__filters, score_rule__form
from ..models import ScoreRule
from ..repositories import (
    score_rule__delete,
    score_rule__store,
    score_rule__toggle_active,
    seed_default_rules,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Filter helper
# ═══════════════════════════════════════════════════════════
def _filtered_rules_qs(request):
    qs = ScoreRule.objects.all()

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(Q(code__icontains=q) | Q(metadata__icontains=q))

    filter_val = (request.GET.get("filter") or "").strip()
    if filter_val in dict(ScoreRule.CalcType.choices):
        qs = qs.filter(calc_type=filter_val)

    active = (request.GET.get("is_active") or "").strip()
    if active == "1":
        qs = qs.filter(is_active=True)
    elif active == "0":
        qs = qs.filter(is_active=False)

    sort = request.GET.get("sort", "code_asc")
    if sort == "code_desc":
        qs = qs.order_by("-code")
    elif sort == "priority":
        qs = qs.order_by("priority", "code")
    elif sort == "amount_desc":
        qs = qs.order_by("-default_amount")
    else:
        qs = qs.order_by("code")

    return qs


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def rule_index(request):
    RequiredAccess(request, "ScoreRuleRead")

    qs = _filtered_rules_qs(request)

    try:
        count = int(request.GET.get("count", "30"))
    except ValueError:
        count = 30

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": "قواعد امتیاز",
        "newUrl": reverse("app_score:rule_create"),
        "searchUrl": reverse("app_score:rule_index"),
        "exportUrl": reverse("app_score:rule_export"),   # ← جدید
        "filters": rule__filters(get_data=request.GET),
        "showAdvanced": False,
        "all": page,
        "total": paginator.count,
        "has_rules": ScoreRule.objects.exists(),
    }
    return render(request, "pages/score/all_rules.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def rule_export(request):
    RequiredAccess(request, "ScoreRuleRead")

    qs = _filtered_rules_qs(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "قواعد امتیاز"
    ws.sheet_view.rightToLeft = True

    headers = [
        "#", "کد", "نمایش کد", "نوع محاسبه", "مقدار",
        "دوره محدودیت", "حداکثر تعداد", "حداکثر امتیاز دوره",
        "نیاز به مرجع", "نیاز به تأیید", "اولویت", "وضعیت",
        "معتبر از", "معتبر تا",
    ]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for cell in ws[1]:
        cell.font = head_font
        cell.fill = head_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for r in qs.iterator():
        ws.append([
            r.id,
            r.code,
            r.get_code_display(),
            r.get_calc_type_display(),
            r.default_amount,
            r.get_cap_period_display() if r.cap_period else "",
            r.cap_count or "",
            r.max_amount_per_period or "",
            "بله" if r.requires_reference else "خیر",
            "بله" if r.requires_approval else "خیر",
            r.priority,
            "فعال" if r.is_active else "غیرفعال",
            r.valid_from.strftime("%Y-%m-%d %H:%M") if r.valid_from else "",
            r.valid_until.strftime("%Y-%m-%d %H:%M") if r.valid_until else "",
        ])

    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"score_rules_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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
def rule_create(request):
    RequiredAccess(request, "ScoreRuleCreate")

    if request.method == "POST":
        cleaned, errors = score_rule__clean__data(request.POST)
        if errors:
            for err in errors:
                response_msg(request, messages.ERROR, err)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد قاعده امتیاز",
                    "backUrl": reverse("app_score:rule_index"),
                    "storeUrl": reverse("app_score:rule_create"),
                    "items": score_rule__form(raw_data=request.POST),
                }
            })

        try:
            score_rule__store(cleaned)
        except Exception:
            logger.exception("rule_create failed")
            response_msg(request, messages.ERROR, "خطا در ذخیره قاعده")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد قاعده امتیاز",
                    "backUrl": reverse("app_score:rule_index"),
                    "storeUrl": reverse("app_score:rule_create"),
                    "items": score_rule__form(raw_data=request.POST),
                }
            })

        response_msg(request, messages.SUCCESS, "قاعده امتیاز ایجاد شد")
        return redirect("app_score:rule_index")

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ایجاد قاعده امتیاز",
            "backUrl": reverse("app_score:rule_index"),
            "storeUrl": reverse("app_score:rule_create"),
            "items": score_rule__form(),
        }
    })


# ═══════════════════════════════════════════════════════════
# UPDATE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def rule_update(request, id):
    RequiredAccess(request, "ScoreRuleUpdate")
    rule = get_object_or_404(ScoreRule, id=id)

    if request.method == "POST":
        cleaned, errors = score_rule__clean__data(request.POST, current_rule=rule)
        if errors:
            for err in errors:
                response_msg(request, messages.ERROR, err)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"ویرایش قاعده «{rule.get_code_display()}»",
                    "backUrl": reverse("app_score:rule_index"),
                    "storeUrl": reverse("app_score:rule_update", kwargs={"id": rule.id}),
                    "items": score_rule__form(rule=rule, raw_data=request.POST),
                }
            })

        try:
            score_rule__store(cleaned, item=rule)
        except Exception:
            logger.exception("rule_update failed id=%s", id)
            response_msg(request, messages.ERROR, "خطا در ذخیره تغییرات")
            return redirect("app_score:rule_index")

        response_msg(request, messages.SUCCESS, "قاعده به‌روزرسانی شد")
        return redirect("app_score:rule_index")

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": f"ویرایش قاعده «{rule.get_code_display()}»",
            "backUrl": reverse("app_score:rule_index"),
            "storeUrl": reverse("app_score:rule_update", kwargs={"id": rule.id}),
            "items": score_rule__form(rule=rule),
        }
    })


# ═══════════════════════════════════════════════════════════
# DELETE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def rule_delete(request, id):
    RequiredAccess(request, "ScoreRuleDelete")
    if request.method != "POST":
        response_msg(request, messages.ERROR, "درخواست نامعتبر")
        return redirect("app_score:rule_index")

    rule = get_object_or_404(ScoreRule, id=id)
    try:
        score_rule__delete(rule)
    except Exception:
        logger.exception("rule_delete failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در حذف قاعده")
        return redirect_back(request)

    response_msg(request, messages.SUCCESS, "قاعده حذف شد")
    return redirect("app_score:rule_index")


# ═══════════════════════════════════════════════════════════
# TOGGLE ACTIVE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def rule_toggle_active(request, id):
    RequiredAccess(request, "ScoreRuleUpdate")
    if request.method != "POST":
        return redirect("app_score:rule_index")

    rule = get_object_or_404(ScoreRule, id=id)
    is_active = score_rule__toggle_active(rule)
    response_msg(
        request, messages.SUCCESS,
        "قاعده فعال شد" if is_active else "قاعده غیرفعال شد",
    )
    return redirect("app_score:rule_index")


# ═══════════════════════════════════════════════════════════
# SEED DEFAULTS
# ═══════════════════════════════════════════════════════════
@is_admin_required
def rule_seed_defaults(request):
    RequiredAccess(request, "ScoreRuleCreate")
    if request.method != "POST":
        return redirect("app_score:rule_index")

    try:
        created = seed_default_rules()
    except Exception:
        logger.exception("rule_seed_defaults failed")
        response_msg(request, messages.ERROR, "خطا در ایجاد قواعد پیش‌فرض")
        return redirect("app_score:rule_index")

    if created:
        response_msg(request, messages.SUCCESS, f"{created} قاعده پیش‌فرض ایجاد شد")
    else:
        response_msg(request, messages.INFO, "همه‌ی قواعد از قبل وجود دارند")
    return redirect("app_score:rule_index")