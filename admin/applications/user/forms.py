
from applications.role.models import Role


def backend__userForm(item):
    is_active = 0
    if item:
        if item.is_active:
            is_active = 1

    data = [
        {
            'l': 'نام',
            'n': 'first_name',
            'v': item.first_name if item else '',
            'id': 'thefirst_name',
            'r': 1,
            'c': 'col-md-3',
            'b': 'textBox.html'
        }, {
            'l': 'نام خانوادگی',
            'n': 'last_name',
            'v': item.last_name if item else '',
            'id': 'thelast_name',
            'r': 1,
            'c': 'col-md-3',
            'b': 'textBox.html'
        }, {
            'l': 'تلفن همراه',
            'n': 'mobile',
            'v': item.mobile if item else '',
            'id': 'mobile',
            'r': 1,
            'c': 'col-md-3',
            'b': 'number.html'
        }, {
            'l': 'رمز عبور جدید',
            'n': 'password',
            'v': '',
            'id': 'thePassEl2',
            'r': None,
            'c': 'col-md-3',
            'b': 'textBox.html'
        },

              {'b': 'hr.html'},
        {
            'l': 'فعال',
            'n': 'active',
            'v': is_active,
            'id': 'theActiveEl',
            'r': None,
            'c': 'col-md-2',
            'b': 'switch.html'
        },
    ]
    return data


def backend__adminForm(item):
    is_active = 0
    if item:
        if item.is_active:
            is_active = 1

    select2 = []
    for role in Role.objects.all():
        select2.append({'label': role.title, 'id': role.id})

    data = [
        {
            'l': 'نام',
            'n': 'first_name',
            'v': item.first_name if item else '',
            'id': 'first_name',
            'r': 1,
            'c': 'col-md-3',
            'b': 'textBox.html'
        },
        {
            'l': 'نام خانوادگی',
            'n': 'last_name',
            'v': item.last_name if item else '',
            'id': 'last_name',
            'r': 1,
            'c': 'col-md-3',
            'b': 'textBox.html'
        }, {
            'l': 'تلفن همراه',
            'n': 'mobile',
            'v': item.mobile if item else '',
            'id': 'mobile',
            'r': 1,
            'c': 'col-md-3',
            'b': 'number.html'
        },
        {
            'l': 'تصویر شخصی',
            'n': 'photo',
            'v': item.photo if item else '',
            'id': 'photo',
            'r': None,
            'c': 'col-md-3',
            'b': 'photo.html'
        },
       
        {'b': 'hr.html'},

        {
            'l': 'سطح دسترسی',
            'n': 'roles',
            'v': item.role_ids if item else [],
            'id': 'theRolesElement',
            'r': 1,
            'c': 'col-md-3',
            'data': select2,
            'b': 'select2Multi.html'
        },
        {
            'l': 'فعال',
            'n': 'active',
            'v': is_active,
            'id': 'active',
            'r': None,
            'c': 'col-md-3',
            'b': 'switch.html'
        },

        {'b': 'hr.html'},

    ]
    return data


def backend__profileForm(item):
    data = [
        {'l': 'نام', 'n': 'first_name', 'v': item.first_name if item else '', 'id': 1, 'r': 1, 'c': 'col-md-4',
         'b': 'textBox.html'},
        {'l': 'نام خانوادگی', 'n': 'last_name', 'v': item.last_name if item else '', 'id': 1, 'r': 1, 'c': 'col-md-4',
         'b': 'textBox.html'},
        {'l': 'تلفن همراه', 'n': 'mobile', 'v': item.mobile if item else '', 'id': 1, 'r': 1, 'c': 'col-md-4',
         'b': 'number.html'},
        {'l': 'آدرس', 'n': 'address', 'v': item.address if item else '', 'id': 1, 'r': None, 'c': 'col-md-4',
         'b': 'textBox.html'},
        {'l': 'تصویر شخصی', 'n': 'photo', 'v': item.photo if item else '', 'id': 1, 'r': None, 'c': 'col-md-4',
         'b': 'photo.html'},
    ]
    return data


def backend__changePass():
    return [
        {'l': 'رمز عبور فعلی', 'n': 'oldPassword', 'v': '', 'id': 'thePassEl1', 'r': 1, 'c': 'col-6 offset-r-3', 'b': 'password.html'},
        {'l': 'رمز عبور جدید', 'n': 'newPassword', 'v': '', 'id': 'thePassEl2', 'r': 1, 'c': 'col-6 offset-r-3', 'b': 'password.html'},
        {'l': 'تکرار رمز عبور', 'n': 'rePassword', 'v': '', 'id': 'thePassEl3', 'r': 1, 'c': 'col-6 offset-r-3', 'b': 'password.html'},
    ]








#####################################################
#####################################################
#####################################################
#####################################################
#####################################################
#####################################################
# applications/user/forms.py
# applications/user/forms.py

from applications.role.models import Role
from applications.setting.models import Province, City

from .models import User


GENDER_CHOICES = [("male", "مرد"), ("female", "زن")]


def user__form(user=None, raw_data=None):
    """items برای قالب عمومی form.html — کاربر + پروفایل"""

    profile = getattr(user, "relation_profile", None) if user else None

    def val(obj, field, default=""):
        if raw_data is not None:
            return raw_data.get(field, default)
        if obj is not None:
            return getattr(obj, field, default)
        return default

    def bool_val(field, default=False):
        if raw_data is not None:
            return str(raw_data.get(field, "")).lower() in ("on", "true", "1")
        if user is not None:
            return getattr(user, field, default)
        return default

    def role_ids_value():
        if raw_data is not None:
            ids = raw_data.getlist("role_ids[]") or raw_data.getlist("role_ids") or []
            return [int(i) for i in ids if str(i).isdigit()]
        if user is not None:
            return list(user.role_ids or [])
        return []

    def province_value():
        if raw_data is not None:
            v = raw_data.get("province") or raw_data.get("province_id")
            return int(v) if v and str(v).isdigit() else ""
        if profile and profile.province_id:
            return profile.province_id
        return ""

    def city_value():
        if raw_data is not None:
            v = raw_data.get("city") or raw_data.get("city_id")
            return int(v) if v and str(v).isdigit() else ""
        if profile and profile.city_id:
            return profile.city_id
        return ""

    def birth_date_miladi():
        """تاریخ میلادی YYYY-MM-DD — برای name در hidden"""
        if raw_data is not None:
            return raw_data.get("birth_date", "")
        if profile and profile.birth_date:
            return profile.birth_date.strftime("%Y-%m-%d")
        return ""

    def birth_date_jalali():
        """تاریخ شمسی YYYY/MM/DD — برای نمایش"""
        iso = birth_date_miladi()
        if not iso:
            return ""
        try:
            import datetime
            from persiantools.jdatetime import JalaliDate
            d = datetime.datetime.strptime(iso, "%Y-%m-%d").date()
            return JalaliDate(d).strftime("%Y/%m/%d")
        except Exception:
            return ""

    def avatar_url():
        if user and user.avatar:
            try:
                return user.avatar.url
            except ValueError:
                return ""
        return ""

    # ── داده‌های select2 ──
    province_data = [
        {"id": p.id, "label": p.name}
        for p in Province.objects.all().only("id", "name").order_by("name")
    ]
    city_data = [
        {"id": c.id, "label": c.name, "province": c.province_id}
        for c in City.objects.all().only("id", "name", "province_id").order_by("name")
    ]
    role_data = [
        {"id": r.id, "label": r.title}
        for r in Role.objects.all().only("id", "title").order_by("title")
    ]
    gender_data = [{"id": v, "label": l} for v, l in GENDER_CHOICES]
    nature_data = [{"id": v, "label": l} for v, l in User.UserNature.choices]

    # ── اسکریپت وابستگی استان → شهر ──
    dependency_script = """
<script>
(function () {
    function initProvinceCity() {
        var provinceEl = document.querySelector('select[name="province"]');
        var cityEl = document.querySelector('select[name="city"]');
        if (!provinceEl || !cityEl) return;

        var allCityOptions = Array.from(cityEl.querySelectorAll('option[data-province]'));
        var currentCity = cityEl.value;
        var placeholderCity = cityEl.querySelector('option[value=""]');

        function filterCities(reset) {
            var pid = provinceEl.value;
            cityEl.innerHTML = '';
            if (placeholderCity) cityEl.appendChild(placeholderCity.cloneNode(true));

            allCityOptions.forEach(function (opt) {
                if (!pid || opt.dataset.province === pid) {
                    var clone = opt.cloneNode(true);
                    if (!reset && clone.value === currentCity) clone.selected = true;
                    cityEl.appendChild(clone);
                }
            });

            // اگر select2 فعال است، باید refresh شود
            if (window.jQuery && jQuery(cityEl).data('select2')) {
                jQuery(cityEl).trigger('change.select2');
            }
        }

        provinceEl.addEventListener('change', function () {
            currentCity = '';
            filterCities(true);
        });

        if (provinceEl.value) filterCities(false);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initProvinceCity);
    } else {
        initProvinceCity();
    }
    setTimeout(initProvinceCity, 300);
})();
</script>
"""

    return [
        # ═══════════ کاربر پایه ═══════════
        {
            "l": "شماره موبایل *",
            "n": "mobile",
            "v": val(user, "mobile"),
            "id": "the_mobile",
            "r": True,
            "c": "col-md-4",
            "b": "textBox.html",
        },
        {
            "l": "نام *",
            "n": "first_name",
            "v": val(user, "first_name"),
            "id": "the_first_name",
            "r": True,
            "c": "col-md-4",
            "b": "textBox.html",
        },
        {
            "l": "نام خانوادگی *",
            "n": "last_name",
            "v": val(user, "last_name"),
            "id": "the_last_name",
            "r": True,
            "c": "col-md-4",
            "b": "textBox.html",
        },
        {
            "l": "ایمیل",
            "n": "email",
            "v": val(user, "email"),
            "id": "the_email",
            "r": None,
            "c": "col-md-6",
            "b": "textBox.html",
        },
        {
            "l": "رمز عبور" + ("" if user else " (خالی = تولید خودکار)"),
            "n": "password",
            "v": "",
            "id": "the_password",
            "r": None,
            "c": "col-md-6",
            "b": "password.html",
        },
        {
            "l": "نوع کاربری *",
            "n": "nature",
            "v": val(user, "nature", User.UserNature.USER),
            "id": "the_nature",
            "r": True,
            "c": "col-md-4",
            "data": nature_data,
            "b": "select2Single.html",
        },
        {
            "l": "سطح دسترسی",
            "n": "role_ids",
            "v": role_ids_value(),
            "id": "the_role_ids",
            "r": None,
            "c": "col-md-4",
            "data": role_data,
            "b": "select2Multi.html",
        },
        {
            "l": "موبایل تایید شده",
            "n": "is_mobile_verified",
            "v": 1 if bool_val("is_mobile_verified") else 0,
            "id": "is_mobile_verified",
            "r": None,
            "c": "col-md-2",
            "b": "switch.html",
        },
        {
            "l": "فعال",
            "n": "is_active",
            "v": 1 if bool_val("is_active", True) else 0,
            "id": "is_active",
            "r": None,
            "c": "col-md-2",
            "b": "switch.html",
        },
        {
            "l": "آواتار",
            "n": "avatar",
            "v": avatar_url(),
            "id": "the_avatar",
            "r": None,
            "c": "col-md-4",
            "b": "photo.html",
        },

        # ═══════════ پروفایل ═══════════
        {
            "l": "کد ملی",
            "n": "national_code",
            "v": val(profile, "national_code") if profile else val(None, "national_code"),
            "id": "the_national_code",
            "r": None,
            "c": "col-md-4",
            "b": "textBox.html",
        },
        {
            # ✅ استفاده از کامپوننت آماده‌ی date.html
            "l": "تاریخ تولد",
            "n": "birth_date",
            "v": birth_date_jalali(),        # نمایش شمسی
            "v_miladi": birth_date_miladi(), # hidden میلادی
            "id": "the_birth_date",
            "r": None,
            "c": "col-md-4",
            "b": "date.html",
        },
        {
            "l": "جنسیت",
            "n": "gender",
            "v": val(profile, "gender") if profile else val(None, "gender"),
            "id": "the_gender",
            "r": None,
            "c": "col-md-4",
            "data": gender_data,
            "b": "select2Single.html",
        },
        {
            "l": "استان",
            "n": "province",
            "v": province_value(),
            "id": "the_province",
            "r": None,
            "c": "col-md-6",
            "data": province_data,
            "b": "select2Single.html",
        },
        {
            "l": "شهر",
            "n": "city",
            "v": city_value(),
            "id": "the_city",
            "r": None,
            "c": "col-md-6",
            "data": city_data,
            "b": "select2Single.html",
        },
        {
            "l": "آدرس",
            "n": "address",
            "v": val(profile, "address") if profile else val(None, "address"),
            "id": "the_address",
            "r": None,
            "c": "col-md-12",
            "b": "textarea.html",
        },
        {
            "l": "کد پستی",
            "n": "post_code",
            "v": val(profile, "post_code") if profile else val(None, "post_code"),
            "id": "the_post_code",
            "r": None,
            "c": "col-md-6",
            "b": "textBox.html",
        },
        {
            "l": "عنوان شغلی",
            "n": "job_title",
            "v": val(profile, "job_title") if profile else val(None, "job_title"),
            "id": "the_job_title",
            "r": None,
            "c": "col-md-6",
            "b": "textBox.html",
        },
        {
            "l": "نام شرکت",
            "n": "company_name",
            "v": val(profile, "company_name") if profile else val(None, "company_name"),
            "id": "the_company_name",
            "r": None,
            "c": "col-md-12",
            "b": "textBox.html",
        },

        # ═══════════ اسکریپت وابستگی استان → شهر ═══════════
        {
            "b": "script.html",
            "script": dependency_script,
        },
    ]