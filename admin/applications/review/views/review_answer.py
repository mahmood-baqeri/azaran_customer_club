# applications/review/views/review_answer.py

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

from ..forms import answer__filters
from ..models import ReviewAnswer, ReviewQuestion
from ..repositories import answer__delete

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Filter helper
# ═══════════════════════════════════════════════════════════
def _filtered_answers_qs(request):
    qs = ReviewAnswer.objects.select_related("user", "question")

    q = (request.GET.get("q") or "").strip()
    if q:
        cond = (
            Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__mobile__icontains=q)
            | Q(question__question__icontains=q)
        )
        if q.isdigit():
            cond |= Q(id=int(q))
        qs = qs.filter(cond)

    question_id = request.GET.get("question")
    if question_id and str(question_id).isdigit():
        qs = qs.filter(question_id=int(question_id))

    answer_val = (request.GET.get("answer") or "").strip()
    if answer_val in dict(ReviewAnswer.AnswerItem.choices):
        qs = qs.filter(answer=answer_val)

    sort = request.GET.get("sort", "desc")
    qs = qs.order_by("created_at" if sort == "asc" else "-created_at")

    return qs


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def answer_index(request):
    RequiredAccess(request, "ReviewRead")
    qs = _filtered_answers_qs(request)

    try:
        count = int(request.GET.get("count", "50"))
    except ValueError:
        count = 50

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": "پاسخ‌های نظرسنجی",
        "searchUrl": reverse("app_review:answer_index"),
        "exportUrl": reverse("app_review:answer_export"),
        "filters": answer__filters(get_data=request.GET),
        "searchCount": count,
        "all": page,
        "total": paginator.count,
    }
    return render(request, "pages/review/all_answers.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def answer_export(request):
    RequiredAccess(request, "ReviewRead")
    qs = _filtered_answers_qs(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "پاسخ‌های نظرسنجی"
    ws.sheet_view.rightToLeft = True

    headers = ["#", "کاربر", "موبایل", "سوال", "پاسخ", "تاریخ پاسخ"]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for c in ws[1]:
        c.font = head_font
        c.fill = head_fill
        c.alignment = Alignment(horizontal="center", vertical="center")

    for a in qs.iterator():
        ws.append([
            a.id,
            a.user.full_name if a.user else "",
            a.user.mobile if a.user else "",
            a.question.question if a.question else "",
            a.get_answer_display(),
            a.created_at.strftime("%Y-%m-%d %H:%M") if a.created_at else "",
        ])

    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"review_answers_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    resp = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(resp)
    return resp


# ═══════════════════════════════════════════════════════════
# DELETE — اجازه‌ی تجدید نظر
# ═══════════════════════════════════════════════════════════
@is_admin_required
def answer_delete(request, id):
    RequiredAccess(request, "ReviewDelete")
    if request.method != "POST":
        return redirect("app_review:answer_index")

    try:
        answer__delete(id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_review:answer_index")
    except Exception:
        logger.exception("answer_delete failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در حذف پاسخ")
        return redirect("app_review:answer_index")

    response_msg(request, messages.SUCCESS, "پاسخ حذف شد — کاربر می‌تواند دوباره پاسخ دهد")
    return redirect("app_review:answer_index")