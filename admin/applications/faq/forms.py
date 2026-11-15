# applications/faq/forms.py

from applications.core.forms import (
    make_date_item,
    make_input_item,
    make_select2_item,
    make_switch_item,
    pick_bool,
    pick_value,
)

from .models import Answer, Category, FAQ


# ═══════════════════════════════════════════════════════════
# CATEGORY — Form
# ═══════════════════════════════════════════════════════════
def category__form(category=None, raw_data=None):
    return [
        make_input_item(
            label="عنوان دسته‌بندی", name="title", input_id="id_title",
            value=pick_value(raw_data, category, "title"),
            placeholder="مثلاً: سوالات عمومی، مشکلات فنی…",
            required=True, col_class="col-md-12",
        ),
        make_switch_item(
            label="فعال", name="is_active", input_id="id_is_active",
            value=pick_bool(raw_data, category, "is_active", default=True),
            col_class="col-md-6",
        ),
    ]


# ═══════════════════════════════════════════════════════════
# ANSWER — Form
# ═══════════════════════════════════════════════════════════
def answer__form(answer=None, raw_data=None):
    return [
        make_input_item(
            label="متن پاسخ", name="answer", input_id="id_answer",
            kind="textarea", rows=6,
            value=pick_value(raw_data, answer, "answer"),
            placeholder="پاسخ کامل و جامع به این پرسش…",
            required=True, col_class="col-md-12",
        ),
        make_switch_item(
            label="نمایش به کاربران (فعال)", name="is_active", input_id="id_is_active",
            value=pick_bool(raw_data, answer, "is_active"),
            col_class="col-md-6",
        ),
    ]


# ═══════════════════════════════════════════════════════════
# FILTERS — Category
# ═══════════════════════════════════════════════════════════
def category__filters(get_data=None):
    def gv(key, default=""):
        return ((get_data.get(key) if get_data else None) or default)

    sort_choices = [
        {"id": "desc",         "label": "جدیدترین"},
        {"id": "asc",          "label": "قدیمی‌ترین"},
        {"id": "title_asc",    "label": "عنوان (الفبا)"},
        {"id": "faqs_desc",    "label": "بیشترین پرسش"},
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
                placeholder="عنوان دسته…",
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
                empty_label="— همه —", col_class="col-md-6",
            ),
        ],
    }


# ═══════════════════════════════════════════════════════════
# FILTERS — FAQ
# ═══════════════════════════════════════════════════════════
def faq__filters(get_data=None):
    def gv(key, default=""):
        return ((get_data.get(key) if get_data else None) or default)

    sort_choices = [
        {"id": "desc",          "label": "جدیدترین"},
        {"id": "asc",           "label": "قدیمی‌ترین"},
        {"id": "answers_desc",  "label": "بیشترین پاسخ"},
        {"id": "answers_asc",   "label": "بدون/کمترین پاسخ"},
    ]
    count_choices = [
        {"id": "20",  "label": "20"},
        {"id": "50",  "label": "50"},
        {"id": "100", "label": "100"},
    ]
    active_choices = [
        {"id": "1", "label": "فعال (تأیید شده)"},
        {"id": "0", "label": "غیرفعال (در انتظار)"},
    ]
    has_answer_choices = [
        {"id": "1", "label": "دارای پاسخ"},
        {"id": "0", "label": "بدون پاسخ"},
    ]

    category_choices = [
        {"id": c.pk, "label": c.title}
        for c in Category.objects.only("id", "title").order_by("title")
    ]

    return {
        "basic": [
            make_input_item(
                label="جستجو", name="q", input_id="filter_q",
                value=gv("q"),
                placeholder="متن پرسش، نام کاربر، موبایل…",
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
                label="دسته‌بندی", name="category", input_id="filter_category",
                choices=category_choices, value=gv("category"),
                empty_label="— همه —", col_class="col-md-3",
            ),
            make_select2_item(
                label="وضعیت", name="is_active", input_id="filter_is_active",
                choices=active_choices, value=gv("is_active"),
                empty_label="— همه —", col_class="col-md-3",
            ),
            make_select2_item(
                label="پاسخ", name="has_answer", input_id="filter_has_answer",
                choices=has_answer_choices, value=gv("has_answer"),
                empty_label="— همه —", col_class="col-md-3",
            ),
            make_date_item(
                label="ایجاد از", name="created_from", input_id="filter_created_from",
                value=gv("created_from"), col_class="col-md-3",
            ),
        ],
    }