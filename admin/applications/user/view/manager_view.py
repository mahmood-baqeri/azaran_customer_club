# Path: applications/user/view/manager_view.py

# applications/user/views/manager_view.py

import logging

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash 
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
from applications.role.models import Role

from ..clean_data import MOBILE_RE, manager__clean__data  
from ..forms import (                                                   # ← backend__ جدید
    backend__changePass,
    backend__profileForm,
    manager__filters,
    manager__form,
)
from ..forms import manager__filters, manager__form
from ..models import User
from ..repositories import (
    manager__delete,
    manager__store,
    manager__toggle_active,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Helper — resolve roles
# ═══════════════════════════════════════════════════════════
def _resolve_roles_for_page(page):
    """Map role_ids → role objects برای کل صفحه در یک query."""
    all_ids = set()
    for m in page:
        for rid in (m.role_ids or []):
            all_ids.add(rid)
    if not all_ids:
        return
    roles_map = {r.id: r for r in Role.objects.filter(id__in=all_ids).only("id", "title")}
    for m in page:
        m.roles_list = [
            roles_map.get(rid) for rid in (m.role_ids or []) if roles_map.get(rid)
        ]


def _resolve_roles_single(manager):
    """برای صفحه detail — یک query."""
    ids = manager.role_ids or []
    if not ids:
        manager.roles_list = []
        return
    roles_map = {r.id: r for r in Role.objects.filter(id__in=ids).only("id", "title")}
    manager.roles_list = [
        roles_map.get(rid) for rid in ids if roles_map.get(rid)
    ]


# ═══════════════════════════════════════════════════════════
# Filter helper
# ═══════════════════════════════════════════════════════════
def _filtered_managers_qs(request):
    # مدیر = staff OR superuser OR nature=manager
    qs = (
        User.objects
        .filter(
            Q(is_superuser=True) | Q(nature="manager")
        )
        .select_related("relation_profile")
    )

    q = (request.GET.get("q") or "").strip()
    if q:
        cond = (
            Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(mobile__icontains=q)
            | Q(email__icontains=q)
        )
        if q.isdigit():
            cond |= Q(id=int(q))
        qs = qs.filter(cond)

    is_active = (request.GET.get("is_active") or "").strip()
    if is_active == "1":
        qs = qs.filter(is_active=True)
    elif is_active == "0":
        qs = qs.filter(is_active=False)

    is_superuser = (request.GET.get("is_superuser") or "").strip()
    if is_superuser == "1":
        qs = qs.filter(is_superuser=True)
    elif is_superuser == "0":
        qs = qs.filter(is_superuser=False)

    is_verified = (request.GET.get("is_mobile_verified") or "").strip()
    if is_verified == "1":
        qs = qs.filter(is_mobile_verified=True)
    elif is_verified == "0":
        qs = qs.filter(is_mobile_verified=False)

    role_id = request.GET.get("role")
    if role_id and str(role_id).isdigit():
        try:
            qs = qs.filter(role_ids__contains=[int(role_id)])
        except Exception:
            logger.warning("role filter failed for role=%s", role_id)

    sort = request.GET.get("sort", "desc")
    if sort == "asc":
        qs = qs.order_by("id")
    elif sort == "name_asc":
        qs = qs.order_by("first_name", "last_name")
    elif sort == "name_desc":
        qs = qs.order_by("-first_name", "-last_name")
    else:
        qs = qs.order_by("-id")

    return qs


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def manager_index(request):
    RequiredAccess(request, "AdminRead")
    qs = _filtered_managers_qs(request)

    try:
        count = int(request.GET.get("count", "20"))
    except ValueError:
        count = 20

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    # resolve roles in bulk
    _resolve_roles_for_page(page)

    data = {
        "pageTitle": "مدیران",
        "newUrl": reverse("app_user:manager_create"),
        "searchUrl": reverse("app_user:manager_index"),
        "exportUrl": reverse("app_user:manager_export"),
        "filters": manager__filters(get_data=request.GET),
        "searchCount": count,
        "all": page,
        "total": paginator.count,
    }
    return render(request, "pages/user/all_managers.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════
@is_admin_required
def manager_export(request):
    RequiredAccess(request, "AdminRead")
    qs = _filtered_managers_qs(request)

    # For export, resolve roles per row (ok — export is not high-traffic)
    wb = Workbook()
    ws = wb.active
    ws.title = "مدیران"
    ws.sheet_view.rightToLeft = True

    headers = [
        "#", "نام", "موبایل", "ایمیل", "نقش‌ها",
        "دسترسی کامل", "وضعیت", "موبایل تایید", "تاریخ عضویت", "آخرین فعالیت",
    ]
    ws.append(headers)

    head_font = Font(bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="4472C4")
    for c in ws[1]:
        c.font = head_font
        c.fill = head_fill
        c.alignment = Alignment(horizontal="center", vertical="center")

    # Map all roles once
    all_role_ids = set()
    for m in qs.iterator():
        for rid in (m.role_ids or []):
            all_role_ids.add(rid)
    roles_map = {r.id: r.title for r in Role.objects.filter(id__in=all_role_ids)}

    # Re-query to iterate fresh (since iterator was consumed above — do it again)
    for m in qs.iterator():
        role_titles = [
            roles_map.get(rid, "") for rid in (m.role_ids or []) if roles_map.get(rid)
        ]

        ws.append([
            m.id,
            m.full_name or "",
            m.mobile or "",
            m.email or "",
            "، ".join(role_titles),
            "سوپریوزر" if m.is_superuser else "معمولی",
            "فعال" if m.is_active else "غیرفعال",
            "تایید شده" if m.is_mobile_verified else "تایید نشده",
            m.date_joined.strftime("%Y-%m-%d") if m.date_joined else "",
            m.last_active_at.strftime("%Y-%m-%d %H:%M") if m.last_active_at else "",
        ])

    for col_cells in ws.columns:
        length = max(len(str(c.value or "")) for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 60)

    filename = f"managers_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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
def manager_create(request):
    RequiredAccess(request, "AdminCreate")

    if request.method == "POST":
        cleaned_user, cleaned_profile, errors, gen_pass = manager__clean__data(
            request.POST, request.FILES, current_user=None,
        )

        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد مدیر جدید",
                    "backUrl": reverse("app_user:manager_index"),
                    "storeUrl": reverse("app_user:manager_create"),
                    "items": manager__form(raw_data=request.POST),
                }
            })

        try:
            user, generated_password = manager__store(
                request, cleaned_user, cleaned_profile, item=None,
            )
        except Exception:
            logger.exception("manager_create failed")
            response_msg(request, messages.ERROR, "خطا در ذخیره مدیر")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد مدیر جدید",
                    "backUrl": reverse("app_user:manager_index"),
                    "storeUrl": reverse("app_user:manager_create"),
                    "items": manager__form(raw_data=request.POST),
                }
            })

        msg = "مدیر با موفقیت ایجاد شد"
        if generated_password:
            msg += f" — رمز عبور موقت: {generated_password}"
        response_msg(request, messages.SUCCESS, msg)
        return redirect("app_user:manager_index")

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ایجاد مدیر جدید",
            "backUrl": reverse("app_user:manager_index"),
            "storeUrl": reverse("app_user:manager_create"),
            "items": manager__form(),
        }
    })


# ═══════════════════════════════════════════════════════════
# UPDATE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def manager_update(request, id):
    RequiredAccess(request, "AdminUpdate")
    manager = get_object_or_404(User, id=id)

    if request.method == "POST":
        cleaned_user, cleaned_profile, errors, _ = manager__clean__data(
            request.POST, request.FILES, current_user=manager,
        )

        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"ویرایش مدیر «{manager.full_name}»",
                    "backUrl": reverse("app_user:manager_detail", kwargs={"id": manager.id}),
                    "storeUrl": reverse("app_user:manager_update", kwargs={"id": manager.id}),
                    "items": manager__form(manager=manager, raw_data=request.POST),
                }
            })

        try:
            manager__store(request, cleaned_user, cleaned_profile, item=manager)
        except Exception:
            logger.exception("manager_update failed id=%s", id)
            response_msg(request, messages.ERROR, "خطا در ذخیره تغییرات")
            return redirect("app_user:manager_detail", id=manager.id)

        response_msg(request, messages.SUCCESS, "اطلاعات مدیر به‌روزرسانی شد")
        return redirect("app_user:manager_detail", id=manager.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": f"ویرایش مدیر «{manager.full_name}»",
            "backUrl": reverse("app_user:manager_detail", kwargs={"id": manager.id}),
            "storeUrl": reverse("app_user:manager_update", kwargs={"id": manager.id}),
            "items": manager__form(manager=manager),
        }
    })


# ═══════════════════════════════════════════════════════════
# DETAIL
# ═══════════════════════════════════════════════════════════
@is_admin_required
def manager_detail(request, id):
    RequiredAccess(request, "AdminRead")
    manager = get_object_or_404(
        User.objects.select_related(
            "relation_profile",
            "relation_profile__province",
            "relation_profile__city",
        ),
        id=id,
    )

    _resolve_roles_single(manager)

    return render(request, "pages/user/manager_detail.html", {
        "manager": manager,
        "profile": manager.get_profile_info,
        "is_self": request.user.id == manager.id,
    })


# ═══════════════════════════════════════════════════════════
# DELETE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def manager_delete(request, id):
    RequiredAccess(request, "AdminDelete")
    if request.method != "POST":
        return redirect("app_user:manager_index")

    try:
        manager__delete(id, current_user=request.user)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_user:manager_detail", id=id)
    except Exception:
        logger.exception("manager_delete failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در حذف مدیر")
        return redirect("app_user:manager_detail", id=id)

    response_msg(request, messages.SUCCESS, "مدیر حذف شد")
    return redirect("app_user:manager_index")


# ═══════════════════════════════════════════════════════════
# TOGGLE ACTIVE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def manager_toggle_active_action(request, id):
    RequiredAccess(request, "AdminUpdate")
    if request.method != "POST":
        return redirect("app_user:manager_detail", id=id)

    try:
        is_active = manager__toggle_active(id, current_user=request.user)
    except ValueError as e:
        response_msg(request, messages.ERROR, str(e))
        return redirect("app_user:manager_detail", id=id)
    except Exception:
        logger.exception("manager_toggle_active failed id=%s", id)
        response_msg(request, messages.ERROR, "خطا در تغییر وضعیت")
        return redirect("app_user:manager_detail", id=id)

    response_msg(
        request, messages.SUCCESS,
        "مدیر فعال شد" if is_active else "مدیر غیرفعال شد",
    )
    return redirect("app_user:manager_detail", id=id)



# ═══════════════════════════════════════════════════════════
# PROFILE — ویرایش پروفایل خود مدیر (لاگین‌شده)
# ═══════════════════════════════════════════════════════════
@is_admin_required
def manager_profile(request):
    """ویرایش پروفایل خود مدیر لاگین‌شده."""
    user = request.user

    if request.method == "POST":
        errors = []

        first_name = (request.POST.get("first_name") or "").strip()
        last_name = (request.POST.get("last_name") or "").strip()
        mobile = (request.POST.get("mobile") or "").strip()

        if not first_name:
            errors.append("نام الزامی است")
        if not last_name:
            errors.append("نام خانوادگی الزامی است")
        if not mobile:
            errors.append("شماره موبایل الزامی است")
        elif not MOBILE_RE.match(mobile):
            errors.append("شماره موبایل نامعتبر است (مثال: 09121234567)")
        else:
            if User.objects.filter(mobile=mobile).exclude(pk=user.pk).exists():
                errors.append("این شماره موبایل قبلاً ثبت شده است")

        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ویرایش پروفایل",
                    "backUrl": reverse("app_user:manager_index"),
                    "storeUrl": reverse("app_user:manager_profile"),
                    "items": backend__profileForm(user),
                }
            })

        try:
            user.first_name = first_name
            user.last_name = last_name
            user.mobile = mobile

            new_avatar = request.FILES.get("photo")
            if new_avatar:
                user.avatar = new_avatar

            user.save(update_fields=[
                "first_name", "last_name", "mobile", "avatar", "updated_at",
            ])
        except Exception:
            logger.exception("manager_profile failed user=%s", user.id)
            response_msg(request, messages.ERROR, "خطا در ذخیره تغییرات")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ویرایش پروفایل",
                    "backUrl": reverse("app_user:manager_index"),
                    "storeUrl": reverse("app_user:manager_profile"),
                    "items": backend__profileForm(user),
                }
            })

        response_msg(request, messages.SUCCESS, "پروفایل با موفقیت به‌روزرسانی شد")
        return redirect("app_user:manager_profile")

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ویرایش پروفایل",
            "backUrl": reverse("app_user:manager_index"),
            "storeUrl": reverse("app_user:manager_profile"),
            "items": backend__profileForm(user),
        }
    })


# ═══════════════════════════════════════════════════════════
# CHANGE PASSWORD — تغییر رمز خود مدیر (لاگین‌شده)
# ═══════════════════════════════════════════════════════════
@is_admin_required
def manager_change_password(request):
    """تغییر رمز خود مدیر لاگین‌شده."""
    user = request.user

    if request.method == "POST":
        errors = []

        old_password = (request.POST.get("oldPassword") or "").strip()
        new_password = (request.POST.get("newPassword") or "").strip()
        re_password = (request.POST.get("rePassword") or "").strip()

        # ─── چک رمز فعلی ─────────────────────────────
        if not old_password:
            errors.append("رمز فعلی الزامی است")
        elif not user.check_password(old_password):
            errors.append("رمز فعلی نادرست است")

        # ─── چک رمز جدید ─────────────────────────────
        if not new_password:
            errors.append("رمز جدید الزامی است")
        elif len(new_password) < 6:
            errors.append("رمز جدید باید حداقل ۶ کاراکتر باشد")
        elif new_password == old_password:
            errors.append("رمز جدید باید با رمز فعلی متفاوت باشد")

        # ─── چک تکرار ────────────────────────────────
        if new_password != re_password:
            errors.append("تکرار رمز با رمز جدید مطابقت ندارد")

        if errors:
            for e in errors:
                response_msg(request, messages.ERROR, e)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "تغییر رمز عبور",
                    "backUrl": reverse("app_user:manager_profile"),
                    "storeUrl": reverse("app_user:manager_change_password"),
                    "items": backend__changePass(),
                }
            })

        try:
            user.set_password(new_password)
            user.password_changed_at = timezone.now()
            user.save(update_fields=[
                "password", "password_changed_at", "updated_at",
            ])

            # مهم — بعد از set_password، session معتبر بماند
            update_session_auth_hash(request, user)
        except Exception:
            logger.exception("manager_change_password failed user=%s", user.id)
            response_msg(request, messages.ERROR, "خطا در تغییر رمز")
            return redirect("app_user:manager_change_password")

        response_msg(request, messages.SUCCESS, "رمز عبور با موفقیت تغییر کرد")
        return redirect("app_user:manager_profile")

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "تغییر رمز عبور",
            "backUrl": reverse("app_user:manager_profile"),
            "storeUrl": reverse("app_user:manager_change_password"),
            "forgetPass": 1,
            "items": backend__changePass(),
        }
    })