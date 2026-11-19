# Path: applications/learn/forms.py

# applications/review/forms.py

from applications.core.forms import (
    make_image_item,
    make_input_item,
    make_select2_item,
    make_switch_item,
    pick_bool,
    pick_value,
)

from .models import Learn


# ═══════════════════════════════════════════════════════════
# LEARN — Form
# ═══════════════════════════════════════════════════════════
def learn__form(learn=None, raw_data=None):
    size_choices = [{"id": v, "label": l} for v, l in Learn.Size.choices]

    return [
        # ─── عنوان و عرض ────────────────────────────────
        make_input_item(
            label="عنوان", name="title", input_id="id_title",
            value=pick_value(raw_data, learn, "title"),
            required=True, col_class="col-md-8",
        ),
        make_select2_item(
            label="عرض صفحه", name="size", input_id="id_size",
            choices=size_choices,
            value=pick_value(raw_data, learn, "size", Learn.Size.HALF),
            required=True, empty_label=None, col_class="col-md-4",
        ),

        # ─── زیرمتن و کپشن ──────────────────────────────
        make_input_item(
            label="زیرمتن (اختیاری)", name="sub_text", input_id="id_sub_text",
            value=pick_value(raw_data, learn, "sub_text"),
            placeholder="توضیح کوتاه زیر عنوان",
            col_class="col-md-6",
        ),
        make_input_item(
            label="کپشن (اختیاری)", name="caption", input_id="id_caption",
            value=pick_value(raw_data, learn, "caption"),
            placeholder="کپشن نمایش در کارت",
            col_class="col-md-6",
        ),

        # ─── متن کامل ──────────────────────────────────
        make_input_item(
            label="متن کامل", name="full_text", input_id="id_full_text",
            kind="textarea", rows=10,
            value=pick_value(raw_data, learn, "full_text"),
            placeholder="متن کامل آموزش…",
            required=True, col_class="col-md-12",
        ),

        # ─── زمان مطالعه ────────────────────────────────
        make_input_item(
            label="زمان مطالعه (دقیقه)", name="time", input_id="id_time",
            kind="number",
            value=pick_value(raw_data, learn, "time"),
            placeholder="مثلاً: 5",
            min=0, step=1,
            col_class="col-md-4",
        ),

        # ─── فعال ─────────────────────────────────────
        make_switch_item(
            label="فعال", name="is_active", input_id="id_is_active",
            value=pick_bool(raw_data, learn, "is_active", default=True),
            col_class="col-md-4",
        ),

        # ─── تصویر ─────────────────────────────────────
        make_image_item(
            label="تصویر آموزش", name="photo", input_id="id_photo",
            title="انتخاب تصویر",
            existing=learn.photo if learn else None,
            accept="image/jpeg,image/png,image/webp",
            required=(learn is None),
            col_class="col-md-12",
        ),
    ]


# ═══════════════════════════════════════════════════════════
# FILTERS
# ═══════════════════════════════════════════════════════════
def learn__filters(get_data=None):
    def gv(key, default=""):
        return ((get_data.get(key) if get_data else None) or default)

    sort_choices = [
        {"id": "desc",       "label": "جدیدترین"},
        {"id": "asc",        "label": "قدیمی‌ترین"},
        {"id": "title_asc",  "label": "عنوان (الفبا)"},
        {"id": "title_desc", "label": "عنوان (نزولی)"},
        {"id": "time_asc",   "label": "کمترین زمان مطالعه"},
        {"id": "time_desc",  "label": "بیشترین زمان مطالعه"},
    ]
    count_choices = [
        {"id": "20",  "label": "20"},
        {"id": "50",  "label": "50"},
        {"id": "100", "label": "100"},
    ]
    size_choices = [
        {"id": v, "label": l} for v, l in Learn.Size.choices
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
                placeholder="عنوان، زیرمتن، کپشن، متن…",
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
            make_select2_item(
                label="عرض صفحه", name="size", input_id="filter_size",
                choices=size_choices, value=gv("size"),
                empty_label="— همه —", col_class="col-md-6",
            ),
        ],
    }