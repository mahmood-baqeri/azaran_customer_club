# Path: applications/gallery/forms.py

# applications/gallery/forms.py

from applications.core.forms import (
    make_date_item,
    make_image_item,
    make_input_item,
    make_select2_item,
    pick_value,
)
from applications.user.models import User

from .models import Gallery


def _status_choices():
    return [{"id": v, "label": l} for v, l in Gallery.Status.choices]


# ═══════════════════════════════════════════════════════════
# GALLERY — Form
# ═══════════════════════════════════════════════════════════
def gallery__form(gallery=None, raw_data=None):
    items = []

    # ─── کاربر (فقط در create) ────────────────────────
    if gallery is None:
        user_choices = [
            {"id": u.pk, "label": f"{u.full_name or u.mobile} — {u.mobile}"}
            for u in User.objects.filter(is_active=True)
            .only("id", "first_name", "last_name", "mobile", "username")
            .order_by("first_name", "last_name")
        ]
        items.append(make_select2_item(
            label="کاربر (ثبت‌کننده)", name="user", input_id="id_user",
            choices=user_choices,
            value=pick_value(raw_data, None, "user"),
            required=True,
            empty_label="— انتخاب کاربر —",
            placeholder="نام یا موبایل کاربر را جستجو کنید…",
            col_class="col-md-12",
        ))

    # ─── تصویر ─────────────────────────────────────────
    items.append(make_image_item(
        label="تصویر", name="photo", input_id="id_photo",
        title="انتخاب تصویر",
        existing=gallery.photo if gallery else None,
        accept="image/jpeg,image/png,image/webp",
        required=(gallery is None),
        col_class="col-md-12",
    ))

    # ─── کپشن ──────────────────────────────────────────
    items.append(make_input_item(
        label="کپشن (اختیاری)", name="caption", input_id="id_caption",
        value=pick_value(raw_data, gallery, "caption"),
        placeholder="توضیح کوتاه درباره عکس…",
        col_class="col-md-6",
    ))

    # ─── لوکیشن ────────────────────────────────────────
    items.append(make_input_item(
        label="لوکیشن (اختیاری)", name="location", input_id="id_location",
        value=pick_value(raw_data, gallery, "location"),
        placeholder="مثلاً: تهران، خیابان ولیعصر",
        col_class="col-md-6",
    ))

    return items


# ═══════════════════════════════════════════════════════════
# FILTERS
# ═══════════════════════════════════════════════════════════
def gallery__filters(get_data=None):
    def gv(key, default=""):
        return ((get_data.get(key) if get_data else None) or default)

    sort_choices = [
        {"id": "desc",         "label": "جدیدترین"},
        {"id": "asc",          "label": "قدیمی‌ترین"},
        {"id": "likes_desc",   "label": "بیشترین لایک"},
        {"id": "likes_asc",    "label": "کمترین لایک"},
    ]
    count_choices = [
        {"id": "20",  "label": "20"},
        {"id": "50",  "label": "50"},
        {"id": "100", "label": "100"},
    ]
    has_likes_choices = [
        {"id": "1", "label": "دارای لایک"},
        {"id": "0", "label": "بدون لایک"},
    ]

    return {
        "basic": [
            make_input_item(
                label="جستجو", name="q", input_id="filter_q",
                value=gv("q"),
                placeholder="کپشن، لوکیشن، نام کاربر، موبایل…",
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
                label="وضعیت", name="status", input_id="filter_status",
                choices=_status_choices(), value=gv("status"),
                empty_label="— همه —", col_class="col-md-3",
            ),
            make_select2_item(
                label="لایک", name="has_likes", input_id="filter_has_likes",
                choices=has_likes_choices, value=gv("has_likes"),
                empty_label="— همه —", col_class="col-md-3",
            ),
            make_date_item(
                label="ایجاد از", name="created_from", input_id="filter_created_from",
                value=gv("created_from"), col_class="col-md-3",
            ),
            make_date_item(
                label="ایجاد تا", name="created_to", input_id="filter_created_to",
                value=gv("created_to"), col_class="col-md-3",
            ),
        ],
    }