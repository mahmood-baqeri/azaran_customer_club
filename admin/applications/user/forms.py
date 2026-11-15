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

from applications.setting.models import City, Province
from applications.role.models import Role


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
            label="تصویر شخصی", name="photo", input_id="pf_avatar",
            existing=item.avatar if item else None,
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
    
    

# ═══════════════════════════════════════════════════════════
# USER FILTERS — items برای قالب user_filters.html
# ═══════════════════════════════════════════════════════════

def user__filters(get_data=None):
    """items فیلترهای صفحه‌ی لیست کاربران."""

    def gv(key, default=""):
        return ((get_data.get(key) if get_data else None) or default)

    sort_choices = [
        {"id": "desc",         "label": "جدیدترین (ID)"},
        {"id": "asc",          "label": "قدیمی‌ترین (ID)"},
        {"id": "newest",       "label": "جدیدترین عضویت"},
        {"id": "oldest",       "label": "قدیمی‌ترین عضویت"},
        {"id": "active",       "label": "فعال‌ها"},
        {"id": "deactive",     "label": "غیرفعال‌ها"},
        {"id": "balance_high", "label": "بیشترین موجودی"},
        {"id": "balance_low",  "label": "کمترین موجودی"},
        {"id": "earned_high",  "label": "بیشترین کل کسب"},
        {"id": "earned_low",   "label": "کمترین کل کسب"},
        {"id": "kardan",       "label": "سطح کاردان"},
        {"id": "ostadkar",     "label": "سطح استادکار"},
    ]
    count_choices = [
        {"id": "10",  "label": "10"},
        {"id": "20",  "label": "20"},
        {"id": "50",  "label": "50"},
        {"id": "100", "label": "100"},
        {"id": "200", "label": "200"},
        {"id": "300", "label": "300"},
        {"id": "400", "label": "400"},
        {"id": "500", "label": "500"},
        {"id": "1000", "label": "1000"},
        {"id": "2000", "label": "2000"},
        {"id": "3000", "label": "3000"},
        {"id": "4000", "label": "4000"},
        {"id": "5000", "label": "5000"},
        {"id": "10000", "label": "10000"},
    ]
    nature_choices = [{"id": v, "label": l} for v, l in User.UserNature.choices]
    level_choices  = [{"id": "kardan", "label": "کاردان"},
                      {"id": "ostadkar", "label": "استادکار"}]
    bool_active    = [{"id": "1", "label": "فعال"},       {"id": "0", "label": "غیرفعال"}]
    bool_verified  = [{"id": "1", "label": "تایید شده"},  {"id": "0", "label": "تایید نشده"}]
    bool_avatar    = [{"id": "1", "label": "دارد"},       {"id": "0", "label": "ندارد"}]
    gender_choices = [{"id": "male", "label": "مرد"},     {"id": "female", "label": "زن"}]
    bool_cert      = [{"id": "1", "label": "دارد"},       {"id": "0", "label": "ندارد"}]
    bool_invited   = [{"id": "1", "label": "دعوت‌شده"},   {"id": "0", "label": "آزاد"}]

    # role_choices = [{"id": r.pk, "label": r.title} for r in Role.objects.only("id", "title")]

    basic = [
        make_input_item(
            label="جستجو عبارت خاص", name="q", input_id="filter_q",
            value=gv("q"),
            placeholder="جستجو: نام، موبایل، ایمیل، کد معرف، کد ملی، ID",
            col_class="col-md-4",
        ),
        make_select2_item(
            label="مرتب سازی", name="sort", input_id="filter_sort",
            choices=sort_choices, value=gv("sort", "desc"),
            empty_label=None, col_class="col-md-3",
        ),
        make_select2_item(
            label="تعداد نمایش", name="count", input_id="filter_count",
            choices=count_choices, value=gv("count", "20"),
            empty_label=None, col_class="col-md-2",
        ),
    ]

    main = [
        make_select2_item(
            label="نوع کاربری", name="nature", input_id="filter_nature",
            choices=nature_choices, value=gv("nature"),
            empty_label="— نوع کاربری —", col_class="col-md-3",
        ),
        make_select2_item(
            label="سطح", name="level", input_id="filter_level",
            choices=level_choices, value=gv("level"),
            empty_label="— سطح —", col_class="col-md-3",
        ),
        make_select2_item(
            label="وضعیت", name="is_active", input_id="filter_is_active",
            choices=bool_active, value=gv("is_active"),
            empty_label="— وضعیت —", col_class="col-md-2",
        ),
        make_select2_item(
            label="موبایل", name="is_mobile_verified", input_id="filter_is_mobile_verified",
            choices=bool_verified, value=gv("is_mobile_verified"),
            empty_label="— موبایل —", col_class="col-md-2",
        ),
        make_select2_item(
            label="آواتار", name="has_avatar", input_id="filter_has_avatar",
            choices=bool_avatar, value=gv("has_avatar"),
            empty_label="— آواتار —", col_class="col-md-2",
        ),
    ]

    advanced = [
        {
            "title": "مشخصات دموگرافیک",
            "items": [
                make_select2_item(
                    label="جنسیت", name="gender", input_id="filter_gender",
                    choices=gender_choices, value=gv("gender"),
                    empty_label="— جنسیت —", col_class="col-md-3",
                ),
                make_province_city_item(
                    label="",
                    province_name="province", city_name="city",
                    province_id="filter_province", city_id="filter_city",
                    province_value=gv("province") or None,
                    city_value=gv("city") or None,
                    col_class="col-md-6",
                ),
            ],
        },
        {
            "title": "امتیاز",
            "items": [
                make_input_item(
                    label="حداقل موجودی", name="min_balance", input_id="filter_min_balance",
                    kind="number", value=gv("min_balance"),
                    placeholder="حداقل موجودی", min=0, step=1,
                    col_class="col-md-4",
                ),
                make_input_item(
                    label="حداکثر موجودی", name="max_balance", input_id="filter_max_balance",
                    kind="number", value=gv("max_balance"),
                    placeholder="حداکثر موجودی", min=0, step=1,
                    col_class="col-md-4",
                ),
                make_input_item(
                    label="حداقل کل کسب‌شده", name="min_earned", input_id="filter_min_earned",
                    kind="number", value=gv("min_earned"),
                    placeholder="حداقل کل کسب‌شده", min=0, step=1,
                    col_class="col-md-4",
                ),
            ],
        },
        {
            "title": "مدارک و دعوت",
            "items": [
                make_select2_item(
                    label="مدرک", name="has_certificate", input_id="filter_has_certificate",
                    choices=bool_cert, value=gv("has_certificate"),
                    empty_label="— مدرک —", col_class="col-md-4",
                ),
                make_select2_item(
                    label="تایید مدرک", name="cert_verified", input_id="filter_cert_verified",
                    choices=bool_verified, value=gv("cert_verified"),
                    empty_label="— تایید مدرک —", col_class="col-md-4",
                ),
                make_select2_item(
                    label="دعوت", name="invited", input_id="filter_invited",
                    choices=bool_invited, value=gv("invited"),
                    empty_label="— دعوت —", col_class="col-md-4",
                ),
            ],
        },
        {
            "title": "تاریخ‌ها",
            "items": [
                make_date_item(
                    label="عضویت از", name="joined_from", input_id="filter_joined_from",
                    value=gv("joined_from"), col_class="col-md-3",
                ),
                make_date_item(
                    label="عضویت تا", name="joined_to", input_id="filter_joined_to",
                    value=gv("joined_to"), col_class="col-md-3",
                ),
                make_date_item(
                    label="آخرین فعالیت از", name="active_from", input_id="filter_active_from",
                    value=gv("active_from"), col_class="col-md-3",
                ),
                make_date_item(
                    label="آخرین فعالیت تا", name="active_to", input_id="filter_active_to",
                    value=gv("active_to"), col_class="col-md-3",
                ),
            ],
        },
    ]

    return {"basic": basic, "main": main, "advanced": advanced}





# ═══════════════════════════════════════════════════════════
# MANAGER — Form
# ═══════════════════════════════════════════════════════════
def manager__form(manager=None, raw_data=None):
    """items فرم مدیر. شبیه user__form ولی بدون nature و با is_superuser."""
    profile = getattr(manager, "relation_profile", None) if manager else None

    role_choices = [{"id": r.pk, "label": r.title} for r in Role.objects.all()]
    gender_choices = [{"id": v, "label": l} for v, l in GENDER_CHOICES]
    roles_value = pick_multi_or_model(raw_data, "role_ids", manager, "role_ids")

    return [
        # ─── اطلاعات پایه ─────────────────────────────
        make_input_item(
            label="شماره موبایل", name="mobile", input_id="the_mobile",
            value=pick_value(raw_data, manager, "mobile"),
            required=True, col_class="col-md-4",
        ),
        make_input_item(
            label="نام", name="first_name", input_id="the_first_name",
            value=pick_value(raw_data, manager, "first_name"),
            required=True, col_class="col-md-4",
        ),
        make_input_item(
            label="نام خانوادگی", name="last_name", input_id="the_last_name",
            value=pick_value(raw_data, manager, "last_name"),
            required=True, col_class="col-md-4",
        ),
        make_input_item(
            label="ایمیل", name="email", input_id="the_email",
            kind="email",
            value=pick_value(raw_data, manager, "email"),
            col_class="col-md-6",
        ),
        make_input_item(
            label="رمز عبور" + ("" if manager else " (خالی = تولید خودکار)"),
            name="password", input_id="the_password",
            kind="password", value="", col_class="col-md-6",
        ),

        # ─── نقش‌ها و دسترسی ─────────────────────────
        make_select2_item(
            label="نقش‌ها (سطح دسترسی)", name="role_ids", input_id="the_role_ids",
            choices=role_choices, value=roles_value,
            multiple=True, required=True,
            placeholder="نقش‌ها را انتخاب کنید…",
            col_class="col-md-6",
        ),
        make_switch_item(
            label="دسترسی کامل (سوپریوزر)",
            name="is_superuser", input_id="is_superuser",
            value=pick_bool(raw_data, manager, "is_superuser", default=True),
            col_class="col-md-3",
        ),
        make_switch_item(
            label="فعال", name="is_active", input_id="is_active",
            value=pick_bool(raw_data, manager, "is_active", default=True),
            col_class="col-md-3",
        ),
        make_switch_item(
            label="موبایل تایید شده", name="is_mobile_verified",
            input_id="is_mobile_verified",
            value=pick_bool(raw_data, manager, "is_mobile_verified"),
            col_class="col-md-3",
        ),
        make_image_item(
            label="آواتار", name="avatar", input_id="the_avatar",
            existing=manager.avatar if manager else None,
            col_class="col-md-3",
        ),

        # ─── پروفایل ──────────────────────────────────
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
        make_province_city_item(
            label="",
            province_name="province", city_name="city",
            province_id="the_province", city_id="the_city",
            province_value=pick_value_any(raw_data, profile, "province_id", "province"),
            city_value=pick_value_any(raw_data, profile, "city_id", "city"),
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


# ═══════════════════════════════════════════════════════════
# MANAGER — Filters
# ═══════════════════════════════════════════════════════════
def manager__filters(get_data=None):
    def gv(key, default=""):
        return ((get_data.get(key) if get_data else None) or default)

    sort_choices = [
        {"id": "desc", "label": "جدیدترین"},
        {"id": "asc",  "label": "قدیمی‌ترین"},
        {"id": "name_asc",  "label": "نام (الفبا)"},
        {"id": "name_desc", "label": "نام (نزولی)"},
    ]
    count_choices = [
        {"id": "20",  "label": "20"},
        {"id": "50",  "label": "50"},
        {"id": "100", "label": "100"},
    ]
    active_choices = [
        {"id": "1", "label": "فعال"},
        {"id": "0", "label": "غیرفعال"},
    ]
    superuser_choices = [
        {"id": "1", "label": "سوپریوزر"},
        {"id": "0", "label": "غیرسوپریوزر"},
    ]
    verified_choices = [
        {"id": "1", "label": "تایید شده"},
        {"id": "0", "label": "تایید نشده"},
    ]
    role_choices = [
        {"id": r.pk, "label": r.title}
        for r in Role.objects.only("id", "title").order_by("title")
    ]

    return {
        "basic": [
            make_input_item(
                label="جستجو", name="q", input_id="filter_q",
                value=gv("q"),
                placeholder="نام، موبایل، ایمیل، ID",
                col_class="col-md-4",
            ),
            make_select2_item(
                label="مرتب‌سازی", name="sort", input_id="filter_sort",
                choices=sort_choices, value=gv("sort", "desc"),
                empty_label=None, col_class="col-md-3",
            ),
            make_select2_item(
                label="تعداد نمایش", name="count", input_id="filter_count",
                choices=count_choices, value=gv("count", "20"),
                empty_label=None, col_class="col-md-2",
            ),
        ],
        "main": [
            make_select2_item(
                label="وضعیت", name="is_active", input_id="filter_is_active",
                choices=active_choices, value=gv("is_active"),
                empty_label="— همه —", col_class="col-md-3",
            ),
            make_select2_item(
                label="نوع دسترسی", name="is_superuser", input_id="filter_is_superuser",
                choices=superuser_choices, value=gv("is_superuser"),
                empty_label="— همه —", col_class="col-md-3",
            ),
            make_select2_item(
                label="موبایل", name="is_mobile_verified",
                input_id="filter_is_mobile_verified",
                choices=verified_choices, value=gv("is_mobile_verified"),
                empty_label="— همه —", col_class="col-md-3",
            ),
            make_select2_item(
                label="نقش", name="role", input_id="filter_role",
                choices=role_choices, value=gv("role"),
                empty_label="— همه —", col_class="col-md-3",
            ),
        ],
    }