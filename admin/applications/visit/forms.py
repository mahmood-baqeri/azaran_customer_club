# applications/visit/forms.py

from applications.core.forms import (
    make_date_item,
    make_input_item,
    make_select2_item,
    make_switch_item,
    pick_bool,
    pick_value,
)
from applications.user.models import User

from .models import RequestVisit, Visit


# ═══════════════════════════════════════════════════════════
# VISIT — Form
# ═══════════════════════════════════════════════════════════
def visit__form(visit=None, raw_data=None):
    return [
        make_date_item(
            label="تاریخ بازدید", name="date", input_id="id_date",
            value=pick_value(raw_data, visit, "date"),
            required=True, col_class="col-md-6",
        ),
        make_input_item(
            label="ظرفیت (خالی = نامحدود)",
            name="capacity", input_id="id_capacity",
            kind="number",
            value=pick_value(raw_data, visit, "capacity"),
            placeholder="مثلاً: 30",
            min=1, step=1,
            col_class="col-md-4",
        ),
        make_switch_item(
            label="فعال", name="is_active", input_id="id_is_active",
            value=pick_bool(raw_data, visit, "is_active", default=True),
            col_class="col-md-2",
        ),
    ]


# ═══════════════════════════════════════════════════════════
# REQUEST — Form (admin create/edit)
# ═══════════════════════════════════════════════════════════
def request__form(request_item=None, raw_data=None, visit_fixed=None):
    """visit_fixed: اگر از صفحه detail یک Visit بیاییم، این فیلد قفل می‌شود."""
    items = []

    # ─── انتخاب کاربر ────────────────────────────────
    user_choices = [
        {"id": u.pk, "label": f"{u.full_name or u.mobile} — {u.mobile}"}
        for u in User.objects.filter(is_active=True)
        .only("id", "first_name", "last_name", "mobile", "username")
        .order_by("first_name", "last_name")
    ]
    items.append(make_select2_item(
        label="کاربر", name="user", input_id="id_user",
        choices=user_choices,
        value=pick_value(raw_data, request_item, "user_id"),
        required=True,
        empty_label="— انتخاب کاربر —",
        placeholder="نام یا موبایل کاربر را جستجو کنید…",
        col_class="col-md-12",
    ))

    # ─── انتخاب بازدید ───────────────────────────────
    if visit_fixed is not None:
        # قفل روی بازدید فعلی
        items.append(make_select2_item(
            label="بازدید", name="visit", input_id="id_visit",
            choices=[{
                "id": visit_fixed.pk,
                "label": f"{visit_fixed.date:%Y/%m/%d} — ظرفیت: {visit_fixed.capacity or 'نامحدود'}",
            }],
            value=visit_fixed.pk,
            required=True, empty_label=None,
            disabled=True,  # disabled → ارسال نمی‌شود، ولی در clean_data از request.POST می‌خوانیم
            col_class="col-md-12",
        ))
    else:
        visit_choices = [
            {
                "id": v.pk,
                "label": f"{v.date:%Y/%m/%d} — ظرفیت: {v.capacity or 'نامحدود'} — "
                        f"{'فعال' if v.is_active else 'غیرفعال'}",
            }
            for v in Visit.objects.filter(is_active=True).order_by("-date")
        ]
        items.append(make_select2_item(
            label="بازدید", name="visit", input_id="id_visit",
            choices=visit_choices,
            value=pick_value(raw_data, request_item, "visit_id"),
            required=True,
            empty_label="— انتخاب بازدید —",
            col_class="col-md-12",
        ))

    # ─── همراه ───────────────────────────────────────
    items.append(make_switch_item(
        label="همراه دارم", name="have_companion", input_id="id_have_companion",
        value=pick_bool(raw_data, request_item, "have_companion"),
        col_class="col-md-12",
    ))
    items.append(make_input_item(
        label="نام همراه", name="companion_name", input_id="id_companion_name",
        value=pick_value(raw_data, request_item, "companion_name"),
        col_class="col-md-4",
    ))
    items.append(make_input_item(
        label="نام خانوادگی همراه", name="companion_family", input_id="id_companion_family",
        value=pick_value(raw_data, request_item, "companion_family"),
        col_class="col-md-4",
    ))
    items.append(make_input_item(
        label="موبایل همراه", name="companion_mobile", input_id="id_companion_mobile",
        kind="tel",
        value=pick_value(raw_data, request_item, "companion_mobile"),
        placeholder="09xxxxxxxxx",
        col_class="col-md-4",
    ))

    return items


# ═══════════════════════════════════════════════════════════
# FILTERS — Visit
# ═══════════════════════════════════════════════════════════
def visit__filters(get_data=None):
    def gv(key, default=""):
        return ((get_data.get(key) if get_data else None) or default)

    sort_choices = [
        {"id": "date_desc",    "label": "تاریخ بازدید (جدید)"},
        {"id": "date_asc",     "label": "تاریخ بازدید (قدیم)"},
        {"id": "created_desc", "label": "تاریخ ایجاد (جدید)"},
        {"id": "created_asc",  "label": "تاریخ ایجاد (قدیم)"},
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

    return {
        "basic": [
            make_input_item(
                label="جستجو", name="q", input_id="filter_q",
                value=gv("q"),
                placeholder="شناسه بازدید…",
                col_class="col-md-4",
            ),
            make_select2_item(
                label="مرتب‌سازی", name="sort", input_id="filter_sort",
                choices=sort_choices, value=gv("sort", "date_desc"),
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
                empty_label="— همه —", col_class="col-md-6",
            ),
            make_date_item(
                label="از تاریخ", name="date_from", input_id="filter_date_from",
                value=gv("date_from"), col_class="col-md-6",
            ),
        ],
    }


# ═══════════════════════════════════════════════════════════
# FILTERS — RequestVisit
# ═══════════════════════════════════════════════════════════
def request__filters(get_data=None):
    def gv(key, default=""):
        return ((get_data.get(key) if get_data else None) or default)

    sort_choices = [
        {"id": "desc", "label": "جدیدترین"},
        {"id": "asc",  "label": "قدیمی‌ترین"},
    ]
    count_choices = [
        {"id": "20",  "label": "20"},
        {"id": "50",  "label": "50"},
        {"id": "100", "label": "100"},
    ]
    status_choices = [
        {"id": v, "label": l} for v, l in RequestVisit.Status.choices
    ]
    companion_choices = [
        {"id": "1", "label": "با همراه"},
        {"id": "0", "label": "بدون همراه"},
    ]

    # لیست بازدیدها برای فیلتر
    visit_choices = [
        {"id": v.pk, "label": f"{v.date:%Y/%m/%d} — ظرفیت: {v.capacity or 'نامحدود'}"}
        for v in Visit.objects.order_by("-date")[:200]
    ]

    return {
        "basic": [
            make_input_item(
                label="جستجو", name="q", input_id="rf_q",
                value=gv("q"),
                placeholder="نام یا موبایل کاربر / همراه / شناسه…",
                col_class="col-md-4",
            ),
            make_select2_item(
                label="مرتب‌سازی", name="sort", input_id="rf_sort",
                choices=sort_choices, value=gv("sort", "desc"),
                empty_label=None, col_class="col-md-3",
            ),
            make_select2_item(
                label="تعداد نمایش", name="count", input_id="rf_count",
                choices=count_choices, value=gv("count", "20"),
                empty_label=None, col_class="col-md-2",
            ),
        ],
        "main": [
            make_select2_item(
                label="وضعیت", name="status", input_id="rf_status",
                choices=status_choices, value=gv("status"),
                empty_label="— همه —", col_class="col-md-3",
            ),
            make_select2_item(
                label="بازدید", name="visit", input_id="rf_visit",
                choices=visit_choices, value=gv("visit"),
                empty_label="— همه —", col_class="col-md-5",
            ),
            make_select2_item(
                label="همراه", name="has_companion", input_id="rf_has_companion",
                choices=companion_choices, value=gv("has_companion"),
                empty_label="— همه —", col_class="col-md-4",
            ),
        ],
    }