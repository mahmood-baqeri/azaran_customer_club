# applications/user/views/user_view.py

import json
import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Exists, F, OuterRef, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from applications.core.validators import is_valid_date
from applications.core.constant import LEVEL_THRESHOLD
from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess
from applications.core.utils import redirect_back, response_msg

from ..clean_data import user__clean__data
from ..forms import user__form, user__filters
from ..models import JobCertificate, User
from ..repositories import (
    certificate__approve,
    certificate__reject,
    user__delete,
    user__store,
    user__toggle_active,
    user__verify_mobile,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Filter helper — بین لیست و اکسل مشترک
# ═══════════════════════════════════════════════════════════
def _filtered_users_qs(request):
    qs = (
        User.objects
        .select_related(
            "relation_score",
            "relation_profile",
            "relation_profile__province",
            "relation_profile__city",
            "relation_received_invitation",
            "relation_received_invitation__inviter",
        )
    )

    # ── q ───────────────────────────────────────────────
    q = (request.GET.get("q") or "").strip()
    if q:
        cond = (
            Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(mobile__icontains=q)
            | Q(email__icontains=q)
            | Q(referral_code__icontains=q)
            | Q(relation_profile__national_code__icontains=q)
            | Q(relation_profile__job_title__icontains=q)
            | Q(relation_profile__company_name__icontains=q)
        )
        if q.isdigit():
            cond |= Q(id=int(q))
        qs = qs.filter(cond)

    # ── nature ─────────────────────────────────────────
    nature = (request.GET.get("nature") or "").strip()
    if nature in dict(User.UserNature.choices):
        qs = qs.filter(nature=nature)

    # ── level ──────────────────────────────────────────
    level = (request.GET.get("level") or "").strip()
    if level == "kardan":
        qs = qs.filter(
            Q(relation_score__total_earned__lt=LEVEL_THRESHOLD)
            | Q(relation_score__isnull=True)
        )
    elif level == "ostadkar":
        qs = qs.filter(relation_score__total_earned__gte=LEVEL_THRESHOLD)

    # ── is_active / verified / avatar ──────────────────
    is_active = (request.GET.get("is_active") or "").strip()
    if is_active == "1":
        qs = qs.filter(is_active=True)
    elif is_active == "0":
        qs = qs.filter(is_active=False)

    is_verified = (request.GET.get("is_mobile_verified") or "").strip()
    if is_verified == "1":
        qs = qs.filter(is_mobile_verified=True)
    elif is_verified == "0":
        qs = qs.filter(is_mobile_verified=False)

    has_avatar = (request.GET.get("has_avatar") or "").strip()
    if has_avatar == "1":
        qs = qs.exclude(avatar="").exclude(avatar__isnull=True)
    elif has_avatar == "0":
        qs = qs.filter(Q(avatar="") | Q(avatar__isnull=True))

    # ── gender / province / city ───────────────────────
    gender = (request.GET.get("gender") or "").strip()
    if gender in ("male", "female"):
        qs = qs.filter(relation_profile__gender=gender)

    province_id = request.GET.get("province")
    if province_id and str(province_id).isdigit():
        qs = qs.filter(relation_profile__province_id=int(province_id))

    city_id = request.GET.get("city")
    if city_id and str(city_id).isdigit():
        qs = qs.filter(relation_profile__city_id=int(city_id))

    # ── balances ───────────────────────────────────────
    min_balance = request.GET.get("min_balance")
    if min_balance and str(min_balance).isdigit():
        qs = qs.filter(relation_score__current_balance__gte=int(min_balance))

    max_balance = request.GET.get("max_balance")
    if max_balance and str(max_balance).isdigit():
        qs = qs.filter(relation_score__current_balance__lte=int(max_balance))

    min_earned = request.GET.get("min_earned")
    if min_earned and str(min_earned).isdigit():
        qs = qs.filter(relation_score__total_earned__gte=int(min_earned))

    # ── certificates (با Exists — بهینه‌تر از distinct) ──
    has_cert = (request.GET.get("has_certificate") or "").strip()
    cert_subquery = JobCertificate.objects.filter(user=OuterRef("pk"))
    if has_cert == "1":
        qs = qs.filter(Exists(cert_subquery))
    elif has_cert == "0":
        qs = qs.filter(~Exists(cert_subquery))

    cert_verified = (request.GET.get("cert_verified") or "").strip()
    if cert_verified == "1":
        qs = qs.filter(Exists(cert_subquery.filter(is_verified=True)))
    elif cert_verified == "0":
        qs = qs.filter(Exists(cert_subquery.filter(is_verified=False)))

    # ── invited ────────────────────────────────────────
    invited = (request.GET.get("invited") or "").strip()
    if invited == "1":
        qs = qs.filter(relation_received_invitation__isnull=False)
    elif invited == "0":
        qs = qs.filter(relation_received_invitation__isnull=True)

    # ── dates ──────────────────────────────────────────
    joined_from = request.GET.get("joined_from")
    joined_to = request.GET.get("joined_to")
    if joined_from and is_valid_date(joined_from):
        qs = qs.filter(date_joined__date__gte=joined_from)
    if joined_to and is_valid_date(joined_to):
        qs = qs.filter(date_joined__date__lte=joined_to)

    active_from = request.GET.get("active_from")
    active_to = request.GET.get("active_to")
    if active_from and is_valid_date(active_from):
        qs = qs.filter(last_active_at__date__gte=active_from)
    if active_to and is_valid_date(active_to):
        qs = qs.filter(last_active_at__date__lte=active_to)

    # ── role (JSON contains) ──────────────────────────
    role_id = request.GET.get("role")
    if role_id and str(role_id).isdigit():
        try:
            qs = qs.filter(role_ids__contains=[int(role_id)])
        except Exception:
            logger.warning("role JSON contains failed for role=%s", role_id)

    # ── sort ───────────────────────────────────────────
    sort = request.GET.get("sort", "desc")
    if sort == "asc":
        qs = qs.order_by("id")
    elif sort == "newest":
        qs = qs.order_by("-date_joined")
    elif sort == "oldest":
        qs = qs.order_by("date_joined")
    elif sort == "active":
        qs = qs.filter(is_active=True).order_by("-id")
    elif sort == "deactive":
        qs = qs.filter(is_active=False).order_by("-id")
    elif sort == "balance_high":
        qs = qs.order_by(F("relation_score__current_balance").desc(nulls_last=True))
    elif sort == "balance_low":
        qs = qs.order_by(F("relation_score__current_balance").asc(nulls_last=True))
    elif sort == "earned_high":
        qs = qs.order_by(F("relation_score__total_earned").desc(nulls_last=True))
    elif sort == "earned_low":
        qs = qs.order_by(F("relation_score__total_earned").asc(nulls_last=True))
    elif sort == "kardan":
        qs = qs.filter(
            Q(relation_score__total_earned__lt=LEVEL_THRESHOLD)
            | Q(relation_score__isnull=True)
        ).order_by("-id")
    elif sort == "ostadkar":
        qs = qs.filter(relation_score__total_earned__gte=LEVEL_THRESHOLD).order_by("-id")
    else:
        qs = qs.order_by("-id")

    return qs


def _advanced_filter_keys():
    return (
        "gender", "province", "city", "role",
        "min_balance", "max_balance", "min_earned",
        "has_certificate", "cert_verified", "invited",
        "joined_from", "joined_to", "active_from", "active_to",
    )


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def user_index(request):
    RequiredAccess(request, "UserRead")

    qs = _filtered_users_qs(request)

    try:
        count = int(request.GET.get("count", "20"))
    except ValueError:
        count = 20

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    show_advanced = any(request.GET.get(k) for k in _advanced_filter_keys())

    data = {
        "pageTitle": "لیست کاربران",
        "newUrl": reverse("app_user:user_index"),
        "searchUrl": reverse("app_user:user_index"),
        "exportUrl": reverse("app_user:user_export"),   # ← جدید
        "searchText": (request.GET.get("q") or "").strip(),
        "searchSort": request.GET.get("sort", "desc"),
        "searchCount": count,
        "all": page,
        "total": paginator.count,
        "filters": user__filters(get_data=request.GET),
        "showAdvanced": show_advanced,
    }
    return render(request, "pages/user/all_users.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT — خروجی اکسل با تمام فیلترهای فعال
# ═══════════════════════════════════════════════════════════
@is_admin_required
def user_export(request):
    RequiredAccess(request, "UserRead")

    qs = _filtered_users_qs(request)

    wb = Workbook()
    ws = wb.active
    ws.title = "کاربران"
    ws.sheet_view.rightToLeft = True

    headers = [
        "#", "نام", "موبایل", "ایمیل", "نوع کاربری", "سطح",
        "کد معرف", "وضعیت", "موبایل تایید", "کد ملی", "جنسیت",
        "استان", "شهر", "امتیاز فعلی", "کل کسب", "کل خرج",
        "تاریخ عضویت", "آخرین فعالیت",
    ]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for cell in ws[1]:
        cell.font = head_font
        cell.fill = head_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for u in qs.iterator():
        profile = getattr(u, "relation_profile", None)
        score = getattr(u, "relation_score", None)
        level_label = "استادکار" if getattr(u, "is_ostadkar", False) else "کاردان"

        ws.append([
            u.id,
            u.full_name or u.username or "",
            u.mobile or "",
            u.email or "",
            u.get_nature_display(),
            level_label,
            u.referral_code or "",
            "فعال" if u.is_active else "غیرفعال",
            "تایید شده" if u.is_mobile_verified else "تایید نشده",
            (profile.national_code if profile else "") or "",
            (profile.get_gender_display() if profile and profile.gender else "") or "",
            (profile.province.name if profile and profile.province else "") or "",
            (profile.city.name if profile and profile.city else "") or "",
            score.current_balance if score else 0,
            score.total_earned if score else 0,
            score.total_spent if score else 0,
            u.date_joined.strftime("%Y-%m-%d %H:%M") if u.date_joined else "",
            u.last_active_at.strftime("%Y-%m-%d %H:%M") if u.last_active_at else "",
        ])

    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"users_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    resp = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(resp)
    return resp


# ═══════════════════════════════════════════════════════════
# CREATE — بدون تغییر
# ═══════════════════════════════════════════════════════════
@is_admin_required
def user_create(request):
    RequiredAccess(request, "UserCreate")

    if request.method == "POST":
        cleaned_user, cleaned_profile, errors, gen_pass = user__clean__data(
            request.POST, request.FILES, current_user=None
        )

        if errors:
            for err in errors:
                response_msg(request, messages.ERROR, err)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد کاربر جدید",
                    "backUrl": reverse("app_user:user_index"),
                    "storeUrl": reverse("app_user:user_create"),
                    "items": user__form(raw_data=request.POST),
                }
            })

        try:
            user, generated_password = user__store(
                request, cleaned_user, cleaned_profile, item=None
            )
        except Exception:
            logger.exception("user_create failed")
            response_msg(request, messages.ERROR, "خطا در ذخیره کاربر")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد کاربر جدید",
                    "backUrl": reverse("app_user:user_index"),
                    "storeUrl": reverse("app_user:user_create"),
                    "items": user__form(raw_data=request.POST),
                }
            })

        msg = "کاربر با موفقیت ایجاد شد"
        if generated_password:
            msg += f" — رمز عبور موقت: {generated_password}"
        response_msg(request, messages.SUCCESS, msg)
        return redirect("app_user:user_index")

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ایجاد کاربر جدید",
            "backUrl": reverse("app_user:user_index"),
            "storeUrl": reverse("app_user:user_create"),
            "items": user__form(),
        }
    })


# ═══════════════════════════════════════════════════════════
# UPDATE — بدون تغییر
# ═══════════════════════════════════════════════════════════
@is_admin_required
def user_update(request, id):
    RequiredAccess(request, "UserUpdate")
    user = get_object_or_404(User, id=id)

    if request.method == "POST":
        cleaned_user, cleaned_profile, errors, _ = user__clean__data(
            request.POST, request.FILES, current_user=user
        )

        if errors:
            for err in errors:
                response_msg(request, messages.ERROR, err)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"ویرایش کاربر «{user.full_name}»",
                    "backUrl": reverse("app_user:user_index"),
                    "storeUrl": reverse("app_user:user_update", kwargs={"id": user.id}),
                    "items": user__form(user=user, raw_data=request.POST),
                }
            })

        try:
            user__store(request, cleaned_user, cleaned_profile, item=user)
        except Exception:
            logger.exception("user_update failed id=%s", id)
            response_msg(request, messages.ERROR, "خطا در ذخیره تغییرات")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"ویرایش کاربر «{user.full_name}»",
                    "backUrl": reverse("app_user:user_index"),
                    "storeUrl": reverse("app_user:user_update", kwargs={"id": user.id}),
                    "items": user__form(user=user, raw_data=request.POST),
                }
            })

        response_msg(request, messages.SUCCESS, "اطلاعات کاربر به‌روزرسانی شد")
        return redirect("app_user:user_index")

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": f"ویرایش کاربر «{user.full_name}»",
            "backUrl": reverse("app_user:user_index"),
            "storeUrl": reverse("app_user:user_update", kwargs={"id": user.id}),
            "items": user__form(user=user),
        }
    })


# ═══════════════════════════════════════════════════════════
# DELETE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def user_delete(request, id):
    RequiredAccess(request, "UserDelete")
    if request.method != "POST":
        response_msg(request, messages.ERROR, "درخواست نامعتبر")
        return redirect("app_user:user_index")

    user = get_object_or_404(User, id=id)

    # جلوگیری از حذف خود ادمین
    if request.user.id == user.id:
        response_msg(request, messages.ERROR, "نمی‌توانید حساب خودتان را حذف کنید")
        return redirect_back(request)

    try:
        user__delete(user)
    except Exception:
        logger.exception("user_delete failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در حذف کاربر")
        return redirect_back(request)

    response_msg(request, messages.SUCCESS, "کاربر حذف شد")
    return redirect("app_user:user_index")


# ═══════════════════════════════════════════════════════════
# DETAIL
# ═══════════════════════════════════════════════════════════
@is_admin_required
def user_detail(request, id):
    RequiredAccess(request, "UserRead")

    user = get_object_or_404(
        User.objects
        .select_related(
            "relation_profile",
            "relation_profile__province",
            "relation_profile__city",
            "relation_score",
        )
        .prefetch_related(
            "user_job_certificates",
            "devices",
        ),
        id=id,
    )

    return render(request, "pages/user/user_detail.html", {
        "user": user,
        "profile": user.get_profile_info,
        "score": user.get_score,
        "certificates": user.user_job_certificates.all(),
        "devices": user.devices.filter(is_active=True),
    })


# ═══════════════════════════════════════════════════════════
# ACTION — Verify mobile
# ═══════════════════════════════════════════════════════════
@is_admin_required
def user_verify_mobile_action(request, id):
    RequiredAccess(request, "UserUpdate")
    if request.method != "POST":
        return redirect("app_user:user_detail", id=id)

    user = get_object_or_404(User, id=id)
    changed = user__verify_mobile(user)
    if changed:
        response_msg(request, messages.SUCCESS, "موبایل کاربر تایید شد")
    else:
        response_msg(request, messages.INFO, "موبایل از قبل تایید شده بود")
    return redirect("app_user:user_detail", id=id)


# ═══════════════════════════════════════════════════════════
# ACTION — Toggle active
# ═══════════════════════════════════════════════════════════
@is_admin_required
def user_toggle_active_action(request, id):
    RequiredAccess(request, "UserUpdate")
    if request.method != "POST":
        return redirect("app_user:user_detail", id=id)

    user = get_object_or_404(User, id=id)
    if request.user.id == user.id:
        response_msg(request, messages.ERROR, "نمی‌توانید وضعیت حساب خودتان را تغییر دهید")
        return redirect("app_user:user_detail", id=id)

    is_active = user__toggle_active(user)
    response_msg(request, messages.SUCCESS, "کاربر فعال شد" if is_active else "کاربر غیرفعال شد")
    return redirect("app_user:user_detail", id=id)


# ═══════════════════════════════════════════════════════════
# ACTION — Certificate approve / reject
# ═══════════════════════════════════════════════════════════
@is_admin_required
def user_certificate_approve(request, id, cert_id):
    RequiredAccess(request, "UserUpdate")
    if request.method != "POST":
        return redirect("app_user:user_detail", id=id)

    cert = get_object_or_404(JobCertificate, id=cert_id, user_id=id)
    changed = certificate__approve(cert)
    response_msg(
        request,
        messages.SUCCESS if changed else messages.INFO,
        "مدرک تایید شد" if changed else "مدرک از قبل تایید شده بود",
    )
    return redirect("app_user:user_detail", id=id)


@is_admin_required
def user_certificate_reject(request, id, cert_id):
    RequiredAccess(request, "UserUpdate")
    if request.method != "POST":
        return redirect("app_user:user_detail", id=id)

    cert = get_object_or_404(JobCertificate, id=cert_id, user_id=id)
    changed = certificate__reject(cert)
    response_msg(
        request,
        messages.SUCCESS if changed else messages.INFO,
        "مدرک رد شد" if changed else "مدرک از قبل رد شده بود",
    )
    return redirect("app_user:user_detail", id=id)