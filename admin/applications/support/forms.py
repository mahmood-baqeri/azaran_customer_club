# applications/support/forms.py

from applications.core.forms import (
    make_date_item,
    make_file_item,
    make_input_item,
    make_select2_item,
    pick_value,
)
from applications.user.models import User

from .models import Support


def _category_choices():
    return [{"id": v, "label": l} for v, l in Support.Category.choices]


def _priority_choices():
    return [{"id": v, "label": l} for v, l in Support.Priority.choices]


def _status_choices():
    return [{"id": v, "label": l} for v, l in Support.Status.choices]


# ═══════════════════════════════════════════════════════════
# SUPPORT — Create form
# ═══════════════════════════════════════════════════════════
def support__form(support=None, raw_data=None):
    user_choices = [
        {"id": u.pk, "label": f"{u.full_name or u.mobile} — {u.mobile}"}
        for u in User.objects.filter(is_active=True)
        .only("id", "first_name", "last_name", "mobile", "username")
        .order_by("first_name", "last_name")
    ]

    return [
        make_select2_item(
            label="کاربر (ثبت‌کننده تیکت)", name="user", input_id="id_user",
            choices=user_choices,
            value=pick_value(raw_data, None, "user"),
            required=True,
            empty_label="— انتخاب کاربر —",
            placeholder="نام یا موبایل کاربر را جستجو کنید…",
            col_class="col-md-12",
        ),
        make_input_item(
            label="موضوع", name="subject", input_id="id_subject",
            value=pick_value(raw_data, support, "subject"),
            required=True, col_class="col-md-12",
        ),
        make_select2_item(
            label="دسته‌بندی", name="category", input_id="id_category",
            choices=_category_choices(),
            value=pick_value(raw_data, support, "category", Support.Category.OTHER),
            required=True, empty_label=None, col_class="col-md-6",
        ),
        make_select2_item(
            label="اولویت", name="priority", input_id="id_priority",
            choices=_priority_choices(),
            value=pick_value(raw_data, support, "priority", Support.Priority.NORMAL),
            required=True, empty_label=None, col_class="col-md-6",
        ),
        # ─── پیام اول (فقط در ایجاد) ─────────────────
        make_input_item(
            label="متن پیام اول", name="first_message_text", input_id="id_first_message_text",
            kind="textarea", rows=5,
            value=pick_value(raw_data, None, "first_message_text"),
            placeholder="شرح مشکل یا درخواست…",
            col_class="col-md-12",
        ),
        make_file_item(
            label="فایل پیوست (اختیاری)", name="first_message_file", input_id="id_first_message_file",
            accept=".jpg,.jpeg,.png,.webp,.pdf,.zip,.rar",
            col_class="col-md-12",
        ),
    ]


# ═══════════════════════════════════════════════════════════
# SUPPORT — Update form (بدون پیام اول)
# ═══════════════════════════════════════════════════════════
def support__update__form(support, raw_data=None):
    return [
        make_input_item(
            label="موضوع", name="subject", input_id="id_subject",
            value=pick_value(raw_data, support, "subject"),
            required=True, col_class="col-md-12",
        ),
        make_select2_item(
            label="دسته‌بندی", name="category", input_id="id_category",
            choices=_category_choices(),
            value=pick_value(raw_data, support, "category"),
            required=True, empty_label=None, col_class="col-md-6",
        ),
        make_select2_item(
            label="اولویت", name="priority", input_id="id_priority",
            choices=_priority_choices(),
            value=pick_value(raw_data, support, "priority"),
            required=True, empty_label=None, col_class="col-md-6",
        ),
    ]


# ═══════════════════════════════════════════════════════════
# FILTERS
# ═══════════════════════════════════════════════════════════
def support__filters(get_data=None):
    def gv(key, default=""):
        return ((get_data.get(key) if get_data else None) or default)

    sort_choices = [
        {"id": "last_desc", "label": "آخرین پیام (جدید)"},
        {"id": "last_asc",  "label": "آخرین پیام (قدیم)"},
        {"id": "created_desc", "label": "تاریخ ایجاد (جدید)"},
        {"id": "created_asc",  "label": "تاریخ ایجاد (قدیم)"},
    ]
    count_choices = [
        {"id": "20",  "label": "20"},
        {"id": "50",  "label": "50"},
        {"id": "100", "label": "100"},
    ]
    unread_choices = [
        {"id": "1", "label": "فقط نخوانده‌ها"},
    ]

    return {
        "basic": [
            make_input_item(
                label="جستجو", name="q", input_id="filter_q",
                value=gv("q"),
                placeholder="موضوع، نام کاربر، موبایل، پیام…",
                col_class="col-md-4",
            ),
            make_select2_item(
                label="مرتب‌سازی", name="sort", input_id="filter_sort",
                choices=sort_choices, value=gv("sort", "last_desc"),
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
                label="وضعیت", name="status", input_id="filter_status",
                choices=_status_choices(), value=gv("status"),
                empty_label="— همه —", col_class="col-md-3",
            ),
            make_select2_item(
                label="دسته‌بندی", name="category", input_id="filter_category",
                choices=_category_choices(), value=gv("category"),
                empty_label="— همه —", col_class="col-md-3",
            ),
            make_select2_item(
                label="اولویت", name="priority", input_id="filter_priority",
                choices=_priority_choices(), value=gv("priority"),
                empty_label="— همه —", col_class="col-md-3",
            ),
            make_select2_item(
                label="نخوانده", name="has_unread", input_id="filter_has_unread",
                choices=unread_choices, value=gv("has_unread"),
                empty_label="— همه —", col_class="col-md-3",
            ),
        ],
        "advanced": [
            {
                "title": "فیلترهای بیشتر",
                "items": [
                    make_date_item(
                        label="ایجاد از", name="created_from", input_id="filter_created_from",
                        value=gv("created_from"), col_class="col-md-6",
                    ),
                    make_date_item(
                        label="ایجاد تا", name="created_to", input_id="filter_created_to",
                        value=gv("created_to"), col_class="col-md-6",
                    ),
                ],
            },
        ],
    }