# admin/applications/user/view/user_view.py

import json
import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from applications.core.validators import is_valid_date
from applications.setting.models import City, Province
from applications.core.constant import LEVEL_THRESHOLD
from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess
from applications.core.utils import redirect_back, response_msg

from ..clean_data import user__clean__data
from ..forms import user__form
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
# LIST
# ═══════════════════════════════════════════════════════════


@is_admin_required
def user_index(request):
    RequiredAccess(request, "UserRead")

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

    # ═══════════════════════════════════════════════════════
    # جستجو (q)
    # ═══════════════════════════════════════════════════════
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

    # ═══════════════════════════════════════════════════════
    # نوع کاربری (nature)
    # ═══════════════════════════════════════════════════════
    nature = (request.GET.get("nature") or "").strip()
    if nature in dict(User.UserNature.choices):
        qs = qs.filter(nature=nature)

    # ═══════════════════════════════════════════════════════
    # سطح (level)
    # ═══════════════════════════════════════════════════════
    level = (request.GET.get("level") or "").strip()
    if level == "kardan":
        qs = qs.filter(
            Q(relation_score__total_earned__lt=LEVEL_THRESHOLD)
            | Q(relation_score__isnull=True)
        )
    elif level == "ostadkar":
        qs = qs.filter(relation_score__total_earned__gte=LEVEL_THRESHOLD)

    # ═══════════════════════════════════════════════════════
    # وضعیت‌ها
    # ═══════════════════════════════════════════════════════
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

    # ═══════════════════════════════════════════════════════
    # جنسیت / استان / شهر
    # ═══════════════════════════════════════════════════════
    gender = (request.GET.get("gender") or "").strip()
    if gender in ("male", "female"):
        qs = qs.filter(relation_profile__gender=gender)

    province_id = request.GET.get("province")
    if province_id and str(province_id).isdigit():
        qs = qs.filter(relation_profile__province_id=int(province_id))

    city_id = request.GET.get("city")
    if city_id and str(city_id).isdigit():
        qs = qs.filter(relation_profile__city_id=int(city_id))

    # ═══════════════════════════════════════════════════════
    # بازه امتیاز
    # ═══════════════════════════════════════════════════════
    min_balance = request.GET.get("min_balance")
    if min_balance and str(min_balance).isdigit():
        qs = qs.filter(relation_score__current_balance__gte=int(min_balance))

    max_balance = request.GET.get("max_balance")
    if max_balance and str(max_balance).isdigit():
        qs = qs.filter(relation_score__current_balance__lte=int(max_balance))

    min_earned = request.GET.get("min_earned")
    if min_earned and str(min_earned).isdigit():
        qs = qs.filter(relation_score__total_earned__gte=int(min_earned))

    # ═══════════════════════════════════════════════════════
    # مدرک شغلی
    # ═══════════════════════════════════════════════════════
    has_cert = (request.GET.get("has_certificate") or "").strip()
    if has_cert == "1":
        qs = qs.filter(user_job_certificates__isnull=False).distinct()
    elif has_cert == "0":
        qs = qs.filter(user_job_certificates__isnull=True)

    cert_verified = (request.GET.get("cert_verified") or "").strip()
    if cert_verified == "1":
        qs = qs.filter(user_job_certificates__is_verified=True).distinct()
    elif cert_verified == "0":
        qs = qs.filter(user_job_certificates__is_verified=False).distinct()

    # ═══════════════════════════════════════════════════════
    # دعوت‌شده
    # ═══════════════════════════════════════════════════════
    invited = (request.GET.get("invited") or "").strip()
    if invited == "1":
        qs = qs.filter(relation_received_invitation__isnull=False)
    elif invited == "0":
        qs = qs.filter(relation_received_invitation__isnull=True)

    # ═══════════════════════════════════════════════════════
    # بازه تاریخ عضویت / آخرین فعالیت
    # ═══════════════════════════════════════════════════════
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

    # ═══════════════════════════════════════════════════════
    # نقش (role)
    # ═══════════════════════════════════════════════════════
    role_id = request.GET.get("role")
    if role_id and str(role_id).isdigit():
        role_id_int = int(role_id)
        try:
            qs = qs.filter(role_ids__contains=[role_id_int])
        except Exception:
            # فالبک برای دیتابیس‌هایی که از JSON contains پشتیبانی نمی‌کنند
            logger.warning("role JSON contains failed for role=%s", role_id_int)

    # ═══════════════════════════════════════════════════════
    # مرتب‌سازی
    # ═══════════════════════════════════════════════════════
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

    try:
        count = int(request.GET.get("count", "20"))
    except ValueError:
        count = 20

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    # ═══════════════════════════════════════════════════════
    # داده‌های context
    # ═══════════════════════════════════════════════════════
    data = {
        "pageTitle": "لیست کاربران",
        "newUrl": reverse("app_user:user_index"),
        "searchUrl": reverse("app_user:user_index"),
        "searchText": q,
        "searchSort": sort,
        "searchCount": count,
        "all": page,
        "total": paginator.count,
        "request_get": request.GET,
        
        # 👇 داده‌های مورد نیاز فیلترهای پیشرفته
        "nature_choices": list(User.UserNature.choices),
        "provinces": list(Province.objects.all().only("id", "name").order_by("name")),
        "cities": list(
            City.objects.select_related("province")
                        .only("id", "name", "province_id")
                        .order_by("name")
        ),        
    }
    return render(request, "pages/user/all_users.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# CREATE
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
# UPDATE
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