# Path: applications/score/forms.py

# applications/score/forms.py

from applications.core.forms import (
    make_date_item,
    make_input_item,
    make_select2_item,
    make_switch_item,
    pick_value,
    pick_bool,
    serialize_json,
)

from .models import ScoreRule, UserScoreLog


# ═══════════════════════════════════════════════════════════
# SCORE RULE FORM
# ═══════════════════════════════════════════════════════════
def score_rule__form(rule=None, raw_data=None):
    """items برای قالب عمومی form.html — قاعده امتیاز"""

    code_choices = [{"id": v, "label": l} for v, l in UserScoreLog.TransactionCode.choices]
    calc_type_choices  = [{"id": v, "label": l} for v, l in ScoreRule.CalcType.choices]
    cap_period_choices = [{"id": v, "label": l} for v, l in ScoreRule.CapPeriod.choices]

    is_edit = rule is not None

    return [
        # ─── کد تراکنش (در ویرایش غیرفعال) ──────────────
        make_select2_item(
            label="کد تراکنش",
            name="code",
            input_id="the_code",
            choices=code_choices,
            value=pick_value(raw_data, rule, "code"),
            required=True,
            disabled=is_edit,             # disabled → ارسال نمی‌شود
            col_class="col-md-6",
        ),

        # ─── نوع محاسبه / مقدار پیش‌فرض ──────────────────
        make_select2_item(
            label="نوع محاسبه",
            name="calc_type",
            input_id="the_calc_type",
            choices=calc_type_choices,
            value=pick_value(raw_data, rule, "calc_type",
                             ScoreRule.CalcType.FIXED),
            required=True,
            col_class="col-md-3",
        ),
        make_input_item(
            label="مقدار پیش‌فرض",
            name="default_amount",
            input_id="the_default_amount",
            kind="number",
            value=pick_value(raw_data, rule, "default_amount", 0),
            required=True,
            step=1,
            col_class="col-md-3",
        ),

        # ─── محدودیت تکرار ──────────────────────────────
        make_select2_item(
            label="دوره محدودیت",
            name="cap_period",
            input_id="the_cap_period",
            choices=cap_period_choices,
            value=pick_value(raw_data, rule, "cap_period"),
            empty_label="— بدون محدودیت —",
            col_class="col-md-4",
        ),
        make_input_item(
            label="حداکثر تعداد در دوره",
            name="cap_count",
            input_id="the_cap_count",
            kind="number",
            value=pick_value(raw_data, rule, "cap_count"),
            min=0,
            step=1,
            col_class="col-md-4",
        ),
        make_input_item(
            label="حداکثر امتیاز در دوره",
            name="max_amount_per_period",
            input_id="the_max_amount",
            kind="number",
            value=pick_value(raw_data, rule, "max_amount_per_period"),
            step=1,
            col_class="col-md-4",
        ),

        # ─── سوئیچ‌ها ───────────────────────────────────
        make_switch_item(
            label="نیاز به مرجع",
            name="requires_reference",
            input_id="is_req_ref",
            value=pick_bool(raw_data, rule, "requires_reference"),
            col_class="col-md-3",
        ),
        make_switch_item(
            label="نیاز به تأیید",
            name="requires_approval",
            input_id="is_req_appr",
            value=pick_bool(raw_data, rule, "requires_approval"),
            col_class="col-md-3",
        ),
        make_switch_item(
            label="فعال",
            name="is_active",
            input_id="is_active",
            value=pick_bool(raw_data, rule, "is_active", default=True),
            col_class="col-md-3",
        ),
        make_input_item(
            label="اولویت (کمتر = بالاتر)",
            name="priority",
            input_id="the_priority",
            kind="number",
            value=pick_value(raw_data, rule, "priority", 100),
            min=0,
            step=1,
            col_class="col-md-3",
        ),

        # ─── بازه اعتبار (datetime-local) ───────────────
        make_input_item(
            label="معتبر از",
            name="valid_from",
            input_id="the_valid_from",
            kind="datetime-local",
            value=pick_value(raw_data, rule, "valid_from"),
            col_class="col-md-6",
        ),
        make_input_item(
            label="معتبر تا",
            name="valid_until",
            input_id="the_valid_until",
            kind="datetime-local",
            value=pick_value(raw_data, rule, "valid_until"),
            col_class="col-md-6",
        ),

        # ─── metadata (JSON در textarea) ────────────────
        make_input_item(
            label="متادیتا (JSON)",
            name="metadata",
            input_id="the_metadata",
            kind="textarea",
            value=serialize_json(pick_value(raw_data, rule, "metadata")),
            placeholder='PER_LEVEL: {"level_amounts":{"kardan":10,"ostadkar":20}}  |  RANDOM: {"options":[0,1,2,5,10],"weights":[10,20,30,30,10]}',
            rows=6,
            col_class="col-md-12",
        ),
    ]


# ═══════════════════════════════════════════════════════════
# MANUAL ADJUST FORM
# ═══════════════════════════════════════════════════════════
def adjust__form(user=None, raw_data=None):
    """items برای قالب عمومی form.html — تنظیم دستی امتیاز"""

    direction_choices = [
        {"id": v, "label": l} for v, l in UserScoreLog.Direction.choices
    ]

    return [
        make_select2_item(
            label="جهت",
            name="direction",
            input_id="the_direction",
            choices=direction_choices,
            value=pick_value(raw_data, None, "direction",
                             UserScoreLog.Direction.EARNED),
            required=True,
            col_class="col-md-4",
        ),
        make_input_item(
            label="مقدار امتیاز",
            name="amount",
            input_id="the_amount",
            kind="number",
            value=pick_value(raw_data, None, "amount", 0),
            required=True,
            step=1,
            col_class="col-md-4",
        ),
        make_input_item(
            label="دلیل",
            name="reason",
            input_id="the_reason",
            kind="textarea",
            value=pick_value(raw_data, None, "reason"),
            required=True,
            rows=4,
            col_class="col-md-12",
        ),
    ]
    
    



# ═══════════════════════════════════════════════════════════
# SCORE LOG FILTERS
# ═══════════════════════════════════════════════════════════
def log__filters(get_data=None):
    def gv(key, default=""):
        return ((get_data.get(key) if get_data else None) or default)

    sort_choices = [
        {"id": "desc",        "label": "جدیدترین"},
        {"id": "asc",         "label": "قدیمی‌ترین"},
        {"id": "amount_desc", "label": "بیشترین مقدار"},
        {"id": "amount_asc",  "label": "کمترین مقدار"},
    ]
    count_choices = [
        {"id": "20",  "label": "20"},
        {"id": "30",  "label": "30"},
        {"id": "50",  "label": "50"},
        {"id": "100", "label": "100"},
        {"id": "200", "label": "200"},
        {"id": "300", "label": "300"},
        {"id": "400", "label": "400"},
        {"id": "500", "label": "500"},
        {"id": "1000", "label": "1000"},
    ]
    code_choices      = [{"id": v, "label": l} for v, l in UserScoreLog.TransactionCode.choices]
    direction_choices = [{"id": v, "label": l} for v, l in UserScoreLog.Direction.choices]
    source_choices    = [{"id": v, "label": l} for v, l in UserScoreLog.Source.choices]
    reversed_choices  = [
        {"id": "1", "label": "برگشت‌خورده"},
        {"id": "0", "label": "عادی"},
    ]

    return {
        "basic": [
            make_input_item(
                label="جستجو", name="q", input_id="log_q",
                value=gv("q"),
                placeholder="جستجو: نام، موبایل، دلیل، مرجع، ID",
                col_class="col-md-2",
            ),
            make_select2_item(
                label="مرتب سازی", name="sort", input_id="log_sort",
                choices=sort_choices, value=gv("sort", "desc"),
                empty_label=None, col_class="col-md-2",
            ),
            make_select2_item(
                label="تعداد نمایش", name="count", input_id="log_count",
                choices=count_choices, value=gv("count", "50"),
                empty_label=None, col_class="col-md-1",
            ),
            make_date_item(
                label="تاریخ شروع", name="filterDateStart", input_id="log_date_start",
                value=gv("filterDateStart"), col_class="col-md-2",
            ),
            make_date_item(
                label="تاریخ پایان", name="filterDateEnd", input_id="log_date_end",
                value=gv("filterDateEnd"), col_class="col-md-2",
            ),
        ],
        "main": [
            make_select2_item(
                label="کد تراکنش", name="filter", input_id="log_filter",
                choices=code_choices, value=gv("filter"),
                empty_label="— کد تراکنش —", col_class="col-md-5",
            ),
            make_select2_item(
                label="جهت", name="filter2", input_id="log_filter2",
                choices=direction_choices, value=gv("filter2"),
                empty_label="— جهت —", col_class="col-md-3",
            ),
            make_select2_item(
                label="منبع", name="source", input_id="log_source",
                choices=source_choices, value=gv("source"),
                empty_label="— منبع —", col_class="col-md-4",
            ),
        ],
        "advanced": [
            {
                "title": "فیلترهای بیشتر",
                "items": [
                    make_input_item(
                        label="نوع مرجع", name="reference_type", input_id="log_ref_type",
                        value=gv("reference_type"),
                        placeholder="نوع مرجع (invoice، gift_order…)",
                        col_class="col-md-4",
                    ),
                    make_select2_item(
                        label="وضعیت برگشت", name="is_reversed", input_id="log_reversed",
                        choices=reversed_choices, value=gv("is_reversed"),
                        empty_label="— وضعیت برگشت —", col_class="col-md-2",
                    ),
                    make_input_item(
                        label="حداقل مقدار", name="min_amount", input_id="log_min_amount",
                        kind="number", value=gv("min_amount"),
                        placeholder="حداقل مقدار", min=0, step=1,
                        col_class="col-md-3",
                    ),
                    make_input_item(
                        label="حداکثر مقدار", name="max_amount", input_id="log_max_amount",
                        kind="number", value=gv("max_amount"),
                        placeholder="حداکثر مقدار", min=0, step=1,
                        col_class="col-md-3",
                    ),
                ],
            },
        ],
    }


# ═══════════════════════════════════════════════════════════
# SCORE RULE FILTERS
# ═══════════════════════════════════════════════════════════
def rule__filters(get_data=None):
    def gv(key, default=""):
        return ((get_data.get(key) if get_data else None) or default)

    sort_choices = [
        {"id": "code_asc",   "label": "کد (الفبا)"},
        {"id": "code_desc",  "label": "کد (نزولی)"},
        {"id": "priority",   "label": "اولویت"},
        {"id": "amount_desc","label": "بیشترین مقدار"},
    ]
    count_choices = [
        {"id": "20",  "label": "20"},
        {"id": "30",  "label": "30"},
        {"id": "50",  "label": "50"},
        {"id": "100", "label": "100"},
        {"id": "200", "label": "200"},
        {"id": "300", "label": "300"},
        {"id": "400", "label": "400"},
        {"id": "500", "label": "500"},
        {"id": "1000", "label": "1000"},
    ]
    calc_type_choices = [{"id": v, "label": l} for v, l in ScoreRule.CalcType.choices]
    active_choices = [
        {"id": "1", "label": "فعال"},
        {"id": "0", "label": "غیرفعال"},
    ]

    return {
        "basic": [
            make_input_item(
                label="جستجو", name="q", input_id="rule_q",
                value=gv("q"),
                placeholder="جستجو: کد یا متادیتا",
                col_class="col-md-4",
            ),
            make_select2_item(
                label="مرتب سازی", name="sort", input_id="rule_sort",
                choices=sort_choices, value=gv("sort", "code_asc"),
                empty_label=None, col_class="col-md-3",
            ),
            make_select2_item(
                label="تعداد نمایش", name="count", input_id="rule_count",
                choices=count_choices, value=gv("count", "30"),
                empty_label=None, col_class="col-md-2",
            ),
        ],
        "main": [
            make_select2_item(
                label="نوع محاسبه", name="filter", input_id="rule_filter",
                choices=calc_type_choices, value=gv("filter"),
                empty_label="— نوع محاسبه —", col_class="col-md-6",
            ),
            make_select2_item(
                label="وضعیت", name="is_active", input_id="rule_active",
                choices=active_choices, value=gv("is_active"),
                empty_label="— وضعیت —", col_class="col-md-6",
            ),
        ],
    }


# ═══════════════════════════════════════════════════════════
# USER SCORE FILTERS
# ═══════════════════════════════════════════════════════════
def user_score__filters(get_data=None):
    def gv(key, default=""):
        return ((get_data.get(key) if get_data else None) or default)

    sort_choices = [
        {"id": "balance_high", "label": "بیشترین موجودی"},
        {"id": "balance_low",  "label": "کمترین موجودی"},
        {"id": "earned_high",  "label": "بیشترین کسب"},
        {"id": "earned_low",   "label": "کمترین کسب"},
        {"id": "spent_high",   "label": "بیشترین مصرف"},
    ]
    count_choices = [
        {"id": "20",  "label": "20"},
        {"id": "30",  "label": "30"},
        {"id": "50",  "label": "50"},
        {"id": "100", "label": "100"},
        {"id": "200", "label": "200"},
        {"id": "300", "label": "300"},
        {"id": "400", "label": "400"},
        {"id": "500", "label": "500"},
        {"id": "1000", "label": "1000"},
    ]

    return {
        "basic": [
            make_input_item(
                label="جستجو", name="q", input_id="us_q",
                value=gv("q"),
                placeholder="جستجو: نام، موبایل، ID",
                col_class="col-md-4",
            ),
            make_select2_item(
                label="مرتب سازی", name="sort", input_id="us_sort",
                choices=sort_choices, value=gv("sort", "balance_high"),
                empty_label=None, col_class="col-md-3",
            ),
            make_select2_item(
                label="تعداد نمایش", name="count", input_id="us_count",
                choices=count_choices, value=gv("count", "30"),
                empty_label=None, col_class="col-md-2",
            ),
        ],
        "main": [
            make_input_item(
                label="حداقل موجودی", name="min_balance", input_id="us_min_balance",
                kind="number", value=gv("min_balance"),
                placeholder="حداقل موجودی", min=0, step=1,
                col_class="col-md-6",
            ),
            make_input_item(
                label="حداکثر موجودی", name="max_balance", input_id="us_max_balance",
                kind="number", value=gv("max_balance"),
                placeholder="حداکثر موجودی", min=0, step=1,
                col_class="col-md-6",
            ),
        ],
    }