# Path: applications/faq/views/faq.py

# applications/faq/views/faq.py

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

from ..clean_data import answer__clean__data
from ..forms import answer__form, faq__filters
from ..models import Answer, AnswerReaction, Category, FAQ
from ..repositories import (
    answer__delete,
    answer__store,
    answer__toggle_active,
    faq__delete,
    faq__toggle_active,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Filter helper
# ═══════════════════════════════════════════════════════════
def _filtered_faqs_qs(request):
    qs = (
        FAQ.objects
        .select_related("category", "user")
        .annotate(
            answers_count=Count("answers", distinct=True),
            active_answers_count=Count(
                "answers", filter=Q(answers__is_active=True), distinct=True,
            ),
        )
    )

    q = (request.GET.get("q") or "").strip()
    if q:
        cond = (
            Q(question__icontains=q)
            | Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__mobile__icontains=q)
        )
        if q.isdigit():
            cond |= Q(id=int(q))
        qs = qs.filter(cond)

    category_id = request.GET.get("category")
    if category_id and str(category_id).isdigit():
        qs = qs.filter(category_id=int(category_id))

    is_active = (request.GET.get("is_active") or "").strip()
    if is_active == "1":
        qs = qs.filter(is_active=True)
    elif is_active == "0":
        qs = qs.filter(is_active=False)

    has_answer = (request.GET.get("has_answer") or "").strip()
    if has_answer == "1":
        qs = qs.filter(answers_count__gt=0)
    elif has_answer == "0":
        qs = qs.filter(answers_count=0)

    cf = request.GET.get("created_from")
    if cf:
        qs = qs.filter(created_at__date__gte=cf)

    sort = request.GET.get("sort", "desc")
    if sort == "asc":
        qs = qs.order_by("created_at")
    elif sort == "answers_desc":
        qs = qs.order_by("-answers_count", "-created_at")
    elif sort == "answers_asc":
        qs = qs.order_by("answers_count", "-created_at")
    else:
        qs = qs.order_by("-created_at")

    return qs


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def faq_index(request):
    RequiredAccess(request, "FaqRead")
    qs = _filtered_faqs_qs(request)

    try:
        count = int(request.GET.get("count", "20"))
    except ValueError:
        count = 20

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": "پرسش و پاسخ",
        "searchUrl": reverse("app_faq:faq_index"),
        "exportUrl": reverse("app_faq:faq_export"),
        "filters": faq__filters(get_data=request.GET),
        "searchCount": count,
        "all": page,
        "total": paginator.count,
    }
    return render(request, "pages/faq/all_faqs.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def faq_export(request):
    RequiredAccess(request, "FaqRead")
    qs = _filtered_faqs_qs(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "پرسش و پاسخ"
    ws.sheet_view.rightToLeft = True

    headers = [
        "#", "دسته‌بندی", "کاربر", "موبایل", "متن پرسش",
        "تعداد پاسخ", "پاسخ فعال", "وضعیت", "تاریخ ایجاد",
    ]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for c in ws[1]:
        c.font = head_font
        c.fill = head_fill
        c.alignment = Alignment(horizontal="center", vertical="center")

    for f in qs.iterator():
        ws.append([
            f.id,
            f.category.title if f.category else "",
            f.user.full_name if f.user else "",
            f.user.mobile if f.user else "",
            (f.question or "")[:200],
            f.answers_count,
            f.active_answers_count,
            "فعال" if f.is_active else "غیرفعال",
            f.created_at.strftime("%Y-%m-%d %H:%M") if f.created_at else "",
        ])

    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"faqs_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    resp = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(resp)
    return resp


# ═══════════════════════════════════════════════════════════
# DETAIL — پرسش + پاسخ‌ها + واکنش‌ها
# ═══════════════════════════════════════════════════════════
@is_admin_required
def faq_detail(request, id):
    RequiredAccess(request, "FaqRead")
    faq = get_object_or_404(
        FAQ.objects.select_related("category", "user"),
        id=id,
    )

    # پاسخ‌ها با آمار واکنش‌ها
    answers = (
        Answer.objects
        .filter(faq=faq)
        .select_related("user")
        .annotate(
            like_count=Count(
                "reactions",
                filter=Q(reactions__reaction=AnswerReaction.ReactionType.LIKE),
                distinct=True,
            ),
            dislike_count=Count(
                "reactions",
                filter=Q(reactions__reaction=AnswerReaction.ReactionType.DISLIKE),
                distinct=True,
            ),
        )
        .order_by("created_at")
    )

    return render(request, "pages/faq/faq_detail.html", {
        "faq": faq,
        "answers": answers,
        "can_toggle": True,
        "can_delete": True,
    })


# ═══════════════════════════════════════════════════════════
# DELETE Faq
# ═══════════════════════════════════════════════════════════
@is_admin_required
def faq_delete(request, id):
    RequiredAccess(request, "FaqDelete")
    if request.method != "POST":
        return redirect("app_faq:faq_index")

    try:
        faq__delete(id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_faq:faq_detail", id=id)
    except Exception:
        logger.exception("faq_delete failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در حذف پرسش")
        return redirect("app_faq:faq_detail", id=id)

    response_msg(request, messages.SUCCESS, "پرسش حذف شد")
    return redirect("app_faq:faq_index")


# ═══════════════════════════════════════════════════════════
# TOGGLE Faq ACTIVE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def faq_toggle_active(request, id):
    RequiredAccess(request, "FaqUpdate")
    if request.method != "POST":
        return redirect("app_faq:faq_detail", id=id)

    try:
        is_active = faq__toggle_active(id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_faq:faq_detail", id=id)

    response_msg(
        request, messages.SUCCESS,
        "پرسش تأیید و فعال شد" if is_active else "پرسش غیرفعال شد (از دید کاربران پنهان شد)",
    )
    return redirect("app_faq:faq_detail", id=id)


# ═══════════════════════════════════════════════════════════
# ANSWER — Create
# ═══════════════════════════════════════════════════════════
@is_admin_required
def answer_create(request, id):
    RequiredAccess(request, "FaqUpdate")
    faq = get_object_or_404(FAQ, id=id)

    if request.method == "POST":
        cleaned, errors = answer__clean__data(request.POST)
        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"افزودن پاسخ به پرسش #{faq.id}",
                    "backUrl": reverse("app_faq:faq_detail", kwargs={"id": faq.id}),
                    "storeUrl": reverse("app_faq:answer_create", kwargs={"id": faq.id}),
                    "items": answer__form(raw_data=request.POST),
                }
            })

        try:
            answer__store(cleaned=cleaned, faq_id=faq.id, user=request.user)
        except Exception:
            logger.exception("answer_create failed faq=%s", id)
            response_msg(request, messages.ERROR, "خطا در ذخیره پاسخ")
            return redirect("app_faq:faq_detail", id=faq.id)

        response_msg(request, messages.SUCCESS, "پاسخ اضافه شد")
        return redirect("app_faq:faq_detail", id=faq.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": f"افزودن پاسخ به پرسش #{faq.id}",
            "backUrl": reverse("app_faq:faq_detail", kwargs={"id": faq.id}),
            "storeUrl": reverse("app_faq:answer_create", kwargs={"id": faq.id}),
            "items": answer__form(),
        }
    })


# ═══════════════════════════════════════════════════════════
# ANSWER — Toggle active
# ═══════════════════════════════════════════════════════════
@is_admin_required
def answer_toggle_active(request, answer_id):
    RequiredAccess(request, "FaqUpdate")
    if request.method != "POST":
        return redirect("app_faq:faq_index")

    answer = Answer.objects.filter(id=answer_id).first()
    if not answer:
        response_msg(request, messages.ERROR, "پاسخ یافت نشد")
        return redirect("app_faq:faq_index")

    faq_id = answer.faq_id

    try:
        is_active = answer__toggle_active(answer_id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_faq:faq_detail", id=faq_id)

    response_msg(
        request, messages.SUCCESS,
        "پاسخ فعال شد" if is_active else "پاسخ غیرفعال شد",
    )
    return redirect("app_faq:faq_detail", id=faq_id)


# ═══════════════════════════════════════════════════════════
# ANSWER — Delete
# ═══════════════════════════════════════════════════════════
@is_admin_required
def answer_delete(request, answer_id):
    RequiredAccess(request, "FaqDelete")
    if request.method != "POST":
        return redirect("app_faq:faq_index")

    answer = Answer.objects.filter(id=answer_id).first()
    if not answer:
        response_msg(request, messages.ERROR, "پاسخ یافت نشد")
        return redirect("app_faq:faq_index")

    faq_id = answer.faq_id

    try:
        answer__delete(answer_id)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_faq:faq_detail", id=faq_id)
    except Exception:
        logger.exception("answer_delete failed id=%s", answer_id)
        response_msg(request, messages.ERROR, "خطا در حذف پاسخ")
        return redirect("app_faq:faq_detail", id=faq_id)

    response_msg(request, messages.SUCCESS, "پاسخ حذف شد")
    return redirect("app_faq:faq_detail", id=faq_id)