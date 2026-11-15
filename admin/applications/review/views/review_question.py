# applications/review/views/review_question.py

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

from ..clean_data import question__clean__data
from ..forms import question__filters, question__form
from ..models import ReviewAnswer, ReviewQuestion
from ..repositories import (
    question__delete,
    question__store,
    question__toggle_active,
)

logger = logging.getLogger(__name__)

# نقشه امتیاز برای نمایش میانگین
SCORE_MAP = {
    "very_little": 1,
    "little": 2,
    "average": 3,
    "a_lot": 4,
    "very_much": 5,
}


# ═══════════════════════════════════════════════════════════
# Helpers — آمار
# ═══════════════════════════════════════════════════════════
def _annotate_question_counts(qs):
    """افزودن count هر پاسخ به هر سوال (یک query)."""
    return qs.annotate(
        total_answers=Count("answers", distinct=True),
        cnt_very_little=Count(
            "answers", filter=Q(answers__answer="very_little"), distinct=True,
        ),
        cnt_little=Count(
            "answers", filter=Q(answers__answer="little"), distinct=True,
        ),
        cnt_average=Count(
            "answers", filter=Q(answers__answer="average"), distinct=True,
        ),
        cnt_a_lot=Count(
            "answers", filter=Q(answers__answer="a_lot"), distinct=True,
        ),
        cnt_very_much=Count(
            "answers", filter=Q(answers__answer="very_much"), distinct=True,
        ),
    )


def _compute_question_stats(q):
    """محاسبه آمار یک سوال از annotate ها."""
    total = q.total_answers or 0
    if total == 0:
        return {
            "total": 0,
            "average": 0,
            "distribution": [
                {"value": val, "label": label, "count": 0, "percent": 0}
                for val, label in ReviewAnswer.AnswerItem.choices
            ],
        }

    total_score = (
        (q.cnt_very_little or 0) * SCORE_MAP["very_little"]
        + (q.cnt_little or 0) * SCORE_MAP["little"]
        + (q.cnt_average or 0) * SCORE_MAP["average"]
        + (q.cnt_a_lot or 0) * SCORE_MAP["a_lot"]
        + (q.cnt_very_much or 0) * SCORE_MAP["very_much"]
    )
    average = round(total_score / total, 2)

    counts_map = {
        "very_little": q.cnt_very_little or 0,
        "little": q.cnt_little or 0,
        "average": q.cnt_average or 0,
        "a_lot": q.cnt_a_lot or 0,
        "very_much": q.cnt_very_much or 0,
    }

    distribution = []
    for val, label in ReviewAnswer.AnswerItem.choices:
        c = counts_map[val]
        distribution.append({
            "value": val,
            "label": label,
            "count": c,
            "percent": round((c / total) * 100, 1),
        })

    return {
        "total": total,
        "average": average,
        "distribution": distribution,
    }


# ═══════════════════════════════════════════════════════════
# Filter helper
# ═══════════════════════════════════════════════════════════
def _filtered_questions_qs(request):
    qs = ReviewQuestion.objects.all()

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(question__icontains=q)

    is_active = (request.GET.get("is_active") or "").strip()
    if is_active == "1":
        qs = qs.filter(is_active=True)
    elif is_active == "0":
        qs = qs.filter(is_active=False)

    cf = request.GET.get("created_from")
    if cf:
        qs = qs.filter(created_at__date__gte=cf)

    qs = _annotate_question_counts(qs)

    sort = request.GET.get("sort", "desc")
    if sort == "asc":
        qs = qs.order_by("created_at")
    elif sort == "answers_desc":
        qs = qs.order_by("-total_answers", "-created_at")
    elif sort == "answers_asc":
        qs = qs.order_by("total_answers", "-created_at")
    else:
        qs = qs.order_by("-created_at")

    return qs


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def question_index(request):
    RequiredAccess(request, "ReviewRead")
    qs = _filtered_questions_qs(request)

    try:
        count = int(request.GET.get("count", "20"))
    except ValueError:
        count = 20

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    # محاسبه آمار برای هر سوال در page
    for q in page:
        q.stats = _compute_question_stats(q)

    data = {
        "pageTitle": "سوالات نظرسنجی",
        "newUrl": reverse("app_review:question_create"),
        "searchUrl": reverse("app_review:question_index"),
        "exportUrl": reverse("app_review:question_export"),
        "filters": question__filters(get_data=request.GET),
        "searchCount": count,
        "all": page,
        "total": paginator.count,
    }
    return render(request, "pages/review/all_questions.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def question_export(request):
    RequiredAccess(request, "ReviewRead")
    qs = _filtered_questions_qs(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "سوالات نظرسنجی"
    ws.sheet_view.rightToLeft = True

    headers = [
        "#", "سوال", "تعداد پاسخ", "میانگین (۱-۵)",
        "خیلی کم", "کم", "متوسط", "زیاد", "خیلی زیاد",
        "وضعیت", "تاریخ ایجاد",
    ]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for c in ws[1]:
        c.font = head_font
        c.fill = head_fill
        c.alignment = Alignment(horizontal="center", vertical="center")

    for q in qs.iterator():
        stats = _compute_question_stats(q)
        dist = {d["value"]: d["count"] for d in stats["distribution"]}

        ws.append([
            q.id,
            q.question,
            stats["total"],
            stats["average"] if stats["total"] else "—",
            dist.get("very_little", 0),
            dist.get("little", 0),
            dist.get("average", 0),
            dist.get("a_lot", 0),
            dist.get("very_much", 0),
            "فعال" if q.is_active else "غیرفعال",
            q.created_at.strftime("%Y-%m-%d %H:%M") if q.created_at else "",
        ])

    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"review_questions_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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
def question_create(request):
    RequiredAccess(request, "ReviewCreate")

    if request.method == "POST":
        cleaned, errors = question__clean__data(request.POST)
        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد سوال نظرسنجی",
                    "backUrl": reverse("app_review:question_index"),
                    "storeUrl": reverse("app_review:question_create"),
                    "items": question__form(raw_data=request.POST),
                }
            })

        try:
            q = question__store(cleaned=cleaned)
        except Exception:
            logger.exception("question_create failed")
            response_msg(request, messages.ERROR, "خطا در ذخیره سوال")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد سوال نظرسنجی",
                    "backUrl": reverse("app_review:question_index"),
                    "storeUrl": reverse("app_review:question_create"),
                    "items": question__form(raw_data=request.POST),
                }
            })

        response_msg(request, messages.SUCCESS, "سوال ایجاد شد")
        return redirect("app_review:question_detail", id=q.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ایجاد سوال نظرسنجی",
            "backUrl": reverse("app_review:question_index"),
            "storeUrl": reverse("app_review:question_create"),
            "items": question__form(),
        }
    })


# ═══════════════════════════════════════════════════════════
# UPDATE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def question_update(request, id):
    RequiredAccess(request, "ReviewUpdate")
    q = get_object_or_404(ReviewQuestion, id=id)

    if request.method == "POST":
        cleaned, errors = question__clean__data(request.POST, current_question=q)
        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"ویرایش سوال #{q.id}",
                    "backUrl": reverse("app_review:question_detail", kwargs={"id": q.id}),
                    "storeUrl": reverse("app_review:question_update", kwargs={"id": q.id}),
                    "items": question__form(question=q, raw_data=request.POST),
                }
            })

        try:
            question__store(cleaned=cleaned, item=q)
        except Exception:
            logger.exception("question_update failed id=%s", id)
            response_msg(request, messages.ERROR, "خطا در ذخیره تغییرات")
            return redirect("app_review:question_detail", id=q.id)

        response_msg(request, messages.SUCCESS, "سوال به‌روزرسانی شد")
        return redirect("app_review:question_detail", id=q.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": f"ویرایش سوال #{q.id}",
            "backUrl": reverse("app_review:question_detail", kwargs={"id": q.id}),
            "storeUrl": reverse("app_review:question_update", kwargs={"id": q.id}),
            "items": question__form(question=q),
        }
    })


# ═══════════════════════════════════════════════════════════
# DETAIL — سوال + آمار + آخرین پاسخ‌ها
# ═══════════════════════════════════════════════════════════
@is_admin_required
def question_detail(request, id):
    RequiredAccess(request, "ReviewRead")
    q = get_object_or_404(
        _annotate_question_counts(ReviewQuestion.objects.all()),
        id=id,
    )
    stats = _compute_question_stats(q)

    # آخرین ۱۰۰ پاسخ این سوال
    answers = (
        ReviewAnswer.objects
        .filter(question=q)
        .select_related("user")
        .order_by("-created_at")[:100]
    )

    return render(request, "pages/review/question_detail.html", {
        "question": q,
        "stats": stats,
        "answers": answers,
        "can_edit": True,
        "can_toggle": True,
        "can_delete": stats["total"] == 0,
    })


# ═══════════════════════════════════════════════════════════
# DELETE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def question_delete(request, id):
    RequiredAccess(request, "ReviewDelete")
    if request.method != "POST":
        return redirect("app_review:question_index")

    try:
        question__delete(id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_review:question_detail", id=id)
    except Exception:
        logger.exception("question_delete failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در حذف")
        return redirect("app_review:question_detail", id=id)

    response_msg(request, messages.SUCCESS, "سوال حذف شد")
    return redirect("app_review:question_index")


# ═══════════════════════════════════════════════════════════
# TOGGLE ACTIVE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def question_toggle_active(request, id):
    RequiredAccess(request, "ReviewUpdate")
    if request.method != "POST":
        return redirect("app_review:question_detail", id=id)

    try:
        is_active = question__toggle_active(id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_review:question_detail", id=id)

    response_msg(
        request, messages.SUCCESS,
        "سوال فعال شد" if is_active else "سوال غیرفعال شد",
    )
    return redirect("app_review:question_detail", id=id)