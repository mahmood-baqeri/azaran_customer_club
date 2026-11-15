# applications/factor/forms.py

from applications.core.forms import (
    make_date_item,
    make_file_item,
    make_input_item,
    make_select2_item,
    pick_value,
)
from applications.user.models import User

from .models import Factor


def _status_choices():
    return [{"id": v, "label": l} for v, l in Factor.Status.choices]


# ═══════════════════════════════════════════════════════════
# FACTOR — Form
# ═══════════════════════════════════════════════════════════
def factor__form(factor=None, raw_data=None, show_user=True):
    """items فرم فاکتور. show_user فقط در ایجاد True است."""
    items = []

    # ─── انتخاب کاربر (فقط ایجاد) ──────────────────────
    if show_user:
        user_choices = [
            {"id": u.pk, "label": f"{u.full_name or u.mobile} — {u.mobile}"}
            for u in User.objects.filter(is_active=True)
            .only("id", "first_name", "last_name", "mobile", "username")
            .order_by("first_name", "last_name")
        ]
        items.append(make_select2_item(
            label="کاربر (ثبت‌کننده فاکتور)",
            name="user", input_id="id_user",
            choices=user_choices,
            value=pick_value(raw_data, None, "user"),
            required=True,
            empty_label="— انتخاب کاربر —",
            placeholder="نام یا موبایل کاربر را جستجو کنید…",
            col_class="col-md-12",
        ))

    # ─── فایل فاکتور ───────────────────────────────────
    items.append(make_file_item(
        label="فایل فاکتور (jpg / png / webp / pdf)",
        name="photo", input_id="id_photo",
        files=[factor.photo] if factor and factor.photo else None,
        accept=".jpg,.jpeg,.png,.webp,.pdf",
        required=(factor is None or not factor.photo),
        col_class="col-md-6",
    ))

    # ─── شماره فاکتور ──────────────────────────────────
    items.append(make_input_item(
        label="شماره فاکتور (اختیاری)",
        name="invoice_number", input_id="id_invoice_number",
        value=pick_value(raw_data, factor, "invoice_number"),
        placeholder="مثلاً: 14040001",
        col_class="col-md-6",
    ))

    # ─── مبلغ ──────────────────────────────────────────
    items.append(make_input_item(
        label="مبلغ فاکتور (ریال)",
        name="amount", input_id="id_amount",
        kind="number",
        value=pick_value(raw_data, factor, "amount"),
        placeholder="مثلاً: 2500000",
        min=1, step=1,
        col_class="col-md-6",
    ))

    # ─── تاریخ صدور ────────────────────────────────────
    items.append(make_date_item(
        label="تاریخ صدور فاکتور",
        name="invoice_issue_at", input_id="id_invoice_issue_at",
        value=pick_value(raw_data, factor, "invoice_issue_at"),
        col_class="col-md-6",
    ))

    # ─── متره (اختیاری) ────────────────────────────────
    items.append(make_input_item(
        label="تعداد شیر", name="number_water_taps", input_id="id_number_water_taps",
        kind="number", value=pick_value(raw_data, factor, "number_water_taps"),
        min=0, step=1, col_class="col-md-4",
    ))
    items.append(make_input_item(
        label="تعداد اتصالات", name="number_connections", input_id="id_number_connections",
        kind="number", value=pick_value(raw_data, factor, "number_connections"),
        min=0, step=1, col_class="col-md-4",
    ))
    items.append(make_input_item(
        label="متراژ لوله", name="pipe_length", input_id="id_pipe_length",
        kind="number", value=pick_value(raw_data, factor, "pipe_length"),
        min=0, step=1, col_class="col-md-4",
    ))

    # ─── اطلاعات فروشگاه ──────────────────────────────
    items.append(make_input_item(
        label="نام فروشگاه", name="shop_name", input_id="id_shop_name",
        value=pick_value(raw_data, factor, "shop_name"),
        col_class="col-md-4",
    ))
    items.append(make_input_item(
        label="تلفن فروشنده", name="seller_phone", input_id="id_seller_phone",
        kind="tel", value=pick_value(raw_data, factor, "seller_phone"),
        placeholder="09123456789 یا 02112345678",
        col_class="col-md-4",
    ))
    items.append(make_input_item(
        label="آدرس فروشنده", name="seller_address", input_id="id_seller_address",
        value=pick_value(raw_data, factor, "seller_address"),
        col_class="col-md-4",
    ))

    return items


# ═══════════════════════════════════════════════════════════
# REJECT — Form
# ═══════════════════════════════════════════════════════════
def reject__form(raw_data=None):
    return [
        make_input_item(
            label="دلیل رد", name="reason", input_id="id_reason",
            kind="textarea", rows=4,
            value=pick_value(raw_data, None, "reason"),
            required=True, col_class="col-md-12",
        ),
    ]


# ═══════════════════════════════════════════════════════════
# FILTERS
# ═══════════════════════════════════════════════════════════
def factor__filters(get_data=None):
    def gv(key, default=""):
        return ((get_data.get(key) if get_data else None) or default)

    sort_choices = [
        {"id": "desc",         "label": "جدیدترین"},
        {"id": "asc",          "label": "قدیمی‌ترین"},
        {"id": "amount_desc",  "label": "بیشترین مبلغ"},
        {"id": "amount_asc",   "label": "کمترین مبلغ"},
    ]
    count_choices = [
        {"id": "20",  "label": "20"},
        {"id": "50",  "label": "50"},
        {"id": "100", "label": "100"},
    ]

    return {
        "basic": [
            make_input_item(
                label="جستجو", name="q", input_id="filter_q",
                value=gv("q"),
                placeholder="شماره فاکتور، نام کاربر، موبایل، فروشگاه…",
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
            make_input_item(
                label="حداقل مبلغ", name="amount_min", input_id="filter_amount_min",
                kind="number", value=gv("amount_min"),
                min=0, step=1, col_class="col-md-3",
            ),
            make_input_item(
                label="حداکثر مبلغ", name="amount_max", input_id="filter_amount_max",
                kind="number", value=gv("amount_max"),
                min=0, step=1, col_class="col-md-3",
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