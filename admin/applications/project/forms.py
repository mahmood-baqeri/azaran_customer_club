# applications/project/forms.py

from applications.core.forms import (
    make_date_item,
    make_file_item,
    make_input_item,
    make_select2_item,
    pick_value,
)

from .models import Attachment, Project


def _type_choices():
    return [{"id": v, "label": l} for v, l in Project.Type.choices]


def _status_choices():
    return [{"id": v, "label": l} for v, l in Project.Status.choices]


# ═══════════════════════════════════════════════════════════
# PROJECT — Form
# ═══════════════════════════════════════════════════════════
def project__form(project=None, raw_data=None):
    return [
        make_select2_item(
            label="نوع پروژه", name="type", input_id="id_type",
            choices=_type_choices(),
            value=pick_value(raw_data, project, "type", Project.Type.WATER),
            required=True, empty_label=None, col_class="col-md-4",
        ),
        make_input_item(
            label="عنوان", name="title", input_id="id_title",
            value=pick_value(raw_data, project, "title"),
            required=True, col_class="col-md-8",
        ),
        make_input_item(
            label="موبایل مالک", name="owner_mobile", input_id="id_owner_mobile",
            kind="tel",
            value=pick_value(raw_data, project, "owner_mobile"),
            placeholder="09xxxxxxxxx", col_class="col-md-4",
        ),
        make_date_item(
            label="تاریخ اتمام پروژه",
            name="completion_at", input_id="id_completion_at",
            value=pick_value(raw_data, project, "completion_at"),
            col_class="col-md-4",
        ),
        make_input_item(
            label="آدرس", name="address", input_id="id_address",
            value=pick_value(raw_data, project, "address"),
            placeholder="استان، شهر، خیابان، کوچه، پلاک",
            col_class="col-md-4",
        ),
        make_input_item(
            label="تعداد واحد", name="unit_count", input_id="id_unit_count",
            kind="number", value=pick_value(raw_data, project, "unit_count"),
            min=0, step=1, col_class="col-md-3",
        ),
        make_input_item(
            label="تعداد شیرآبی", name="number_water_taps", input_id="id_number_water_taps",
            kind="number", value=pick_value(raw_data, project, "number_water_taps"),
            min=0, step=1, col_class="col-md-3",
        ),
        make_input_item(
            label="تعداد شیرگازی", name="number_gas_taps", input_id="id_number_gas_taps",
            kind="number", value=pick_value(raw_data, project, "number_gas_taps"),
            min=0, step=1, col_class="col-md-3",
        ),
        make_input_item(
            label="تعداد اتصالات", name="number_connections", input_id="id_number_connections",
            kind="number", value=pick_value(raw_data, project, "number_connections"),
            min=0, step=1, col_class="col-md-3",
        ),
        make_input_item(
            label="متراژ لوله", name="pipe_length", input_id="id_pipe_length",
            kind="number", value=pick_value(raw_data, project, "pipe_length"),
            min=0, step=1, col_class="col-md-4",
        ),
    ]


# ═══════════════════════════════════════════════════════════
# COLLEAGUE — Form
# ═══════════════════════════════════════════════════════════
def colleague__form(raw_data=None):
    return [
        make_input_item(
            label="شماره موبایل همکار", name="user_mobile", input_id="id_user_mobile",
            kind="tel", value=pick_value(raw_data, None, "user_mobile"),
            placeholder="09xxxxxxxxx", required=True, col_class="col-md-6",
        ),
        make_input_item(
            label="درصد مشارکت", name="percent", input_id="id_percent",
            kind="number", value=pick_value(raw_data, None, "percent", 10),
            min=1, max=100, step=1, required=True, col_class="col-md-6",
        ),
    ]


# ═══════════════════════════════════════════════════════════
# ATTACHMENT — Form
# ═══════════════════════════════════════════════════════════
def attachment__form(raw_data=None):
    return [
        make_select2_item(
            label="نوع فایل", name="type", input_id="id_type",
            choices=[{"id": v, "label": l} for v, l in Attachment.FileType.choices],
            value=pick_value(raw_data, None, "type"),
            required=True, empty_label=None, col_class="col-md-6",
        ),
        make_file_item(
            label="فایل", name="file", input_id="id_file",
            required=True, col_class="col-md-6",
        ),
    ]


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
def project__filters(get_data=None):
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

    return {
        "basic": [
            make_input_item(
                label="جستجو", name="q", input_id="filter_q",
                value=gv("q"),
                placeholder="عنوان، موبایل، آدرس، ID",
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
                label="نوع", name="type", input_id="filter_type",
                choices=_type_choices(), value=gv("type"),
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