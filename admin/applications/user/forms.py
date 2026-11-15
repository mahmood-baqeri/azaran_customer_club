# applications/user/forms.py

from applications.core.forms import (
    make_input_item,
    make_select2_item,
    make_switch_item,
    make_image_item,
    make_date_item,
    make_province_city_item,
    make_divider_item,
    pick_value,
    pick_value_any,
    pick_bool,
    pick_multi,
       pick_multi_or_model,
)
from applications.role.models import Role

from .models import User


GENDER_CHOICES = [("male", "مرد"), ("female", "زن")]


# ═══════════════════════════════════════════════════════════
# SIMPLE ADMIN FORMS
# ═══════════════════════════════════════════════════════════
def backend__userForm(item):
    return [
        make_input_item(
            label="نام", name="first_name", input_id="thefirst_name",
            value=pick_value(None, item, "first_name"),
            required=True, col_class="col-md-3",
        ),
        make_input_item(
            label="نام خانوادگی", name="last_name", input_id="thelast_name",
            value=pick_value(None, item, "last_name"),
            required=True, col_class="col-md-3",
        ),
        make_input_item(
            label="تلفن همراه", name="mobile", input_id="mobile",
            kind="number",
            value=pick_value(None, item, "mobile"),
            required=True, col_class="col-md-3",
        ),
        make_input_item(
            label="رمز عبور جدید", name="password", input_id="thePassEl2",
            kind="password", value="", col_class="col-md-3",
        ),
        make_divider_item(),
        make_switch_item(
            label="فعال", name="active", input_id="theActiveEl",
            value=pick_bool(None, item, "is_active"),
            col_class="col-md-2",
        ),
    ]


def backend__adminForm(item):
    role_choices = [{"id": r.pk, "label": r.title} for r in Role.objects.all()]

    return [
        make_input_item(
            label="نام", name="first_name", input_id="first_name",
            value=pick_value(None, item, "first_name"),
            required=True, col_class="col-md-3",
        ),
        make_input_item(
            label="نام خانوادگی", name="last_name", input_id="last_name",
            value=pick_value(None, item, "last_name"),
            required=True, col_class="col-md-3",
        ),
        make_input_item(
            label="تلفن همراه", name="mobile", input_id="mobile",
            kind="number",
            value=pick_value(None, item, "mobile"),
            required=True, col_class="col-md-3",
        ),
        make_image_item(
            label="تصویر شخصی", name="photo", input_id="photo",
            existing=item.photo if item else None,
            col_class="col-md-3",
        ),
        make_divider_item(),
        make_select2_item(
            label="سطح دسترسی", name="roles", input_id="theRolesElement",
            choices=role_choices,
            value=item.role_ids if item else [],
            multiple=True, required=True, col_class="col-md-3",
        ),
        make_switch_item(
            label="فعال", name="active", input_id="active",
            value=pick_bool(None, item, "is_active"),
            col_class="col-md-3",
        ),
        make_divider_item(),
    ]


def backend__profileForm(item):
    # ✅ رفع باگ قبلی: همه‌ی فیلدها id یکسان «1» داشتند
    return [
        make_input_item(
            label="نام", name="first_name", input_id="pf_first_name",
            value=pick_value(None, item, "first_name"),
            required=True, col_class="col-md-4",
        ),
        make_input_item(
            label="نام خانوادگی", name="last_name", input_id="pf_last_name",
            value=pick_value(None, item, "last_name"),
            required=True, col_class="col-md-4",
        ),
        make_input_item(
            label="تلفن همراه", name="mobile", input_id="pf_mobile",
            kind="number",
            value=pick_value(None, item, "mobile"),
            required=True, col_class="col-md-4",
        ),
        make_input_item(
            label="آدرس", name="address", input_id="pf_address",
            value=pick_value(None, item, "address"),
            col_class="col-md-4",
        ),
        make_image_item(
            label="تصویر شخصی", name="photo", input_id="pf_photo",
            existing=item.photo if item else None,
            col_class="col-md-4",
        ),
    ]


def backend__changePass():
    return [
        make_input_item(
            label="رمز عبور فعلی", name="oldPassword", input_id="thePassEl1",
            kind="password", required=True,
            col_class="col-6 offset-r-3",
        ),
        make_input_item(
            label="رمز عبور جدید", name="newPassword", input_id="thePassEl2",
            kind="password", required=True,
            col_class="col-6 offset-r-3",
        ),
        make_input_item(
            label="تکرار رمز عبور", name="rePassword", input_id="thePassEl3",
            kind="password", required=True,
            col_class="col-6 offset-r-3",
        ),
    ]


# ═══════════════════════════════════════════════════════════
# COMPREHENSIVE USER FORM
# ═══════════════════════════════════════════════════════════
def user__form(user=None, raw_data=None):
    """items برای قالب عمومی form.html — کاربر + پروفایل"""
    profile = getattr(user, "relation_profile", None) if user else None

    role_choices = [{"id": r.pk, "label": r.title} for r in Role.objects.all()]
    nature_choices = [{"id": v, "label": l} for v, l in User.UserNature.choices]
    gender_choices = [{"id": v, "label": l} for v, l in GENDER_CHOICES]
    roles_value = pick_multi_or_model(raw_data, "role_ids", user, "role_ids")

    return [
        # ─── کاربر پایه ─────────────────────────────────
        make_input_item(
            label="شماره موبایل", name="mobile", input_id="the_mobile",
            value=pick_value(raw_data, user, "mobile"),
            required=True, col_class="col-md-4",
        ),
        make_input_item(
            label="نام", name="first_name", input_id="the_first_name",
            value=pick_value(raw_data, user, "first_name"),
            required=True, col_class="col-md-4",
        ),
        make_input_item(
            label="نام خانوادگی", name="last_name", input_id="the_last_name",
            value=pick_value(raw_data, user, "last_name"),
            required=True, col_class="col-md-4",
        ),
        make_input_item(
            label="ایمیل", name="email", input_id="the_email",
            kind="email",
            value=pick_value(raw_data, user, "email"),
            col_class="col-md-6",
        ),
        make_input_item(
            label="رمز عبور" + ("" if user else " (خالی = تولید خودکار)"),
            name="password", input_id="the_password",
            kind="password", value="", col_class="col-md-6",
        ),
        make_select2_item(
            label="نوع کاربری", name="nature", input_id="the_nature",
            choices=nature_choices,
            value=pick_value(raw_data, user, "nature", User.UserNature.USER),
            required=True, col_class="col-md-4",
        ),
        make_select2_item(
            label="سطح دسترسی", name="role_ids", input_id="the_role_ids",
            choices=role_choices, value=roles_value,
            multiple=True, col_class="col-md-4",
        ),
        make_switch_item(
            label="موبایل تایید شده", name="is_mobile_verified",
            input_id="is_mobile_verified",
            value=pick_bool(raw_data, user, "is_mobile_verified"),
            col_class="col-md-2",
        ),
        make_switch_item(
            label="فعال", name="is_active", input_id="is_active",
            value=pick_bool(raw_data, user, "is_active", default=True),
            col_class="col-md-2",
        ),
        make_image_item(
            label="آواتار", name="avatar", input_id="the_avatar",
            existing=user.avatar if user else None,
            col_class="col-md-4",
        ),

        # ─── پروفایل ─────────────────────────────────────
        make_input_item(
            label="کد ملی", name="national_code", input_id="the_national_code",
            value=pick_value(raw_data, profile, "national_code"),
            col_class="col-md-4",
        ),
        make_date_item(
            label="تاریخ تولد", name="birth_date", input_id="the_birth_date",
            value=pick_value(raw_data, profile, "birth_date"),
            col_class="col-md-4",
        ),
        make_select2_item(
            label="جنسیت", name="gender", input_id="the_gender",
            choices=gender_choices,
            value=pick_value(raw_data, profile, "gender"),
            empty_label="— انتخاب کنید —",
            col_class="col-md-4",
        ),

        # ✅ استان/شهر — کامپوننت خودش AJAX و preload را دارد
        # raw_data از input با name="province" می‌آید، مدل با province_id
        make_province_city_item(
            label="",
            province_name="province", city_name="city",
            province_id="the_province", city_id="the_city",
            province_value=pick_value_any(
                raw_data, profile, "province_id", "province"
            ),
            city_value=pick_value_any(
                raw_data, profile, "city_id", "city"
            ),
            col_class="col-md-12",
        ),

        make_input_item(
            label="آدرس", name="address", input_id="the_address",
            kind="textarea",
            value=pick_value(raw_data, profile, "address"),
            rows=3, col_class="col-md-12",
        ),
        make_input_item(
            label="کد پستی", name="post_code", input_id="the_post_code",
            value=pick_value(raw_data, profile, "post_code"),
            col_class="col-md-6",
        ),
        make_input_item(
            label="عنوان شغلی", name="job_title", input_id="the_job_title",
            value=pick_value(raw_data, profile, "job_title"),
            col_class="col-md-6",
        ),
        make_input_item(
            label="نام شرکت", name="company_name", input_id="the_company_name",
            value=pick_value(raw_data, profile, "company_name"),
            col_class="col-md-12",
        ),
    ]