# applications/score/forms.py

from applications.core.forms import (
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