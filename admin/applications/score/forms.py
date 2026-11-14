# applications/score/forms.py

from .models import ScoreRule, UserScoreLog


# ═══════════════════════════════════════════════════════════
# SCORE RULE FORM
# ═══════════════════════════════════════════════════════════
def score_rule__form(rule=None, raw_data=None):
    """items برای قالب عمومی form.html — قاعده امتیاز"""

    def val(field, default=""):
        if raw_data is not None:
            return raw_data.get(field, default)
        if rule is not None:
            return getattr(rule, field, default)
        return default

    def bool_val(field, default=False):
        if raw_data is not None:
            return str(raw_data.get(field, "")).lower() in ("on", "true", "1")
        if rule is not None:
            return getattr(rule, field, default)
        return default

    def metadata_value():
        if raw_data is not None:
            return raw_data.get("metadata", "")
        if rule is not None and rule.metadata:
            import json
            return json.dumps(rule.metadata, indent=2, ensure_ascii=False)
        return ""

    def dt_value(field):
        if raw_data is not None:
            return raw_data.get(field, "")
        if rule is not None:
            dt = getattr(rule, field, None)
            if dt:
                return dt.strftime("%Y-%m-%dT%H:%M")
        return ""

    code_data = [
        {"id": v, "label": l}
        for v, l in UserScoreLog.TransactionCode.choices
    ]
    calc_type_data = [{"id": v, "label": l} for v, l in ScoreRule.CalcType.choices]
    cap_period_data = [{"id": v, "label": l} for v, l in ScoreRule.CapPeriod.choices]

    return [
        {
            "l": "کد تراکنش *",
            "n": "code",
            "v": val("code"),
            "id": "the_code",
            "r": True,
            "c": "col-md-6",
            "data": code_data,
            "b": "select2Single.html",
            "readonly": rule is not None,
        },
        {
            "l": "نوع محاسبه *",
            "n": "calc_type",
            "v": val("calc_type", ScoreRule.CalcType.FIXED),
            "id": "the_calc_type",
            "r": True,
            "c": "col-md-3",
            "data": calc_type_data,
            "b": "select2Single.html",
        },
        {
            "l": "مقدار پیش‌فرض *",
            "n": "default_amount",
            "v": val("default_amount", 0),
            "id": "the_default_amount",
            "r": True,
            "c": "col-md-3",
            "b": "number.html",
        },

        # ─── محدودیت تکرار ───
        {
            "l": "دوره محدودیت",
            "n": "cap_period",
            "v": val("cap_period"),
            "id": "the_cap_period",
            "r": None,
            "c": "col-md-4",
            "data": cap_period_data,
            "b": "select2Single.html",
        },
        {
            "l": "حداکثر تعداد در دوره",
            "n": "cap_count",
            "v": val("cap_count"),
            "id": "the_cap_count",
            "r": None,
            "c": "col-md-4",
            "b": "number.html",
        },
        {
            "l": "حداکثر امتیاز در دوره",
            "n": "max_amount_per_period",
            "v": val("max_amount_per_period"),
            "id": "the_max_amount",
            "r": None,
            "c": "col-md-4",
            "b": "number.html",
        },

        # ─── سوئیچ‌ها ───
        {
            "l": "نیاز به مرجع",
            "n": "requires_reference",
            "v": 1 if bool_val("requires_reference") else 0,
            "id": "is_req_ref",
            "r": None,
            "c": "col-md-3",
            "b": "switch.html",
        },
        {
            "l": "نیاز به تأیید",
            "n": "requires_approval",
            "v": 1 if bool_val("requires_approval") else 0,
            "id": "is_req_appr",
            "r": None,
            "c": "col-md-3",
            "b": "switch.html",
        },
        {
            "l": "فعال",
            "n": "is_active",
            "v": 1 if bool_val("is_active", True) else 0,
            "id": "is_active",
            "r": None,
            "c": "col-md-3",
            "b": "switch.html",
        },
        {
            "l": "اولویت (کمتر = بالاتر)",
            "n": "priority",
            "v": val("priority", 100),
            "id": "the_priority",
            "r": None,
            "c": "col-md-3",
            "b": "number.html",
        },

        # ─── بازه اعتبار ───
        {
            "l": "معتبر از (YYYY-MM-DDTHH:MM)",
            "n": "valid_from",
            "v": dt_value("valid_from"),
            "id": "the_valid_from",
            "r": None,
            "c": "col-md-6",
            "b": "textBox.html",
        },
        {
            "l": "معتبر تا (YYYY-MM-DDTHH:MM)",
            "n": "valid_until",
            "v": dt_value("valid_until"),
            "id": "the_valid_until",
            "r": None,
            "c": "col-md-6",
            "b": "textBox.html",
        },

        # ─── metadata JSON ───
        {
            "l": "متادیتا (JSON) — نمونه‌ها:\nPER_LEVEL: {\"level_amounts\":{\"kardan\":10,\"ostadkar\":20}}\nRANDOM: {\"options\":[0,1,2,5,10],\"weights\":[10,20,30,30,10]}",
            "n": "metadata",
            "v": metadata_value(),
            "id": "the_metadata",
            "r": None,
            "c": "col-md-12",
            "b": "textarea.html",
        },
    ]


# ═══════════════════════════════════════════════════════════
# MANUAL ADJUST FORM
# ═══════════════════════════════════════════════════════════
def adjust__form(user=None, raw_data=None):
    """items برای قالب عمومی form.html — تنظیم دستی امتیاز"""

    def val(field, default=""):
        if raw_data is not None:
            return raw_data.get(field, default)
        return default

    direction_data = [{"id": v, "label": l} for v, l in UserScoreLog.Direction.choices]

    return [
        {
            "l": "جهت *",
            "n": "direction",
            "v": val("direction", UserScoreLog.Direction.EARNED),
            "id": "the_direction",
            "r": True,
            "c": "col-md-4",
            "data": direction_data,
            "b": "select2Single.html",
        },
        {
            "l": "مقدار امتیاز *",
            "n": "amount",
            "v": val("amount", 0),
            "id": "the_amount",
            "r": True,
            "c": "col-md-4",
            "b": "number.html",
        },
        {
            "l": "دلیل *",
            "n": "reason",
            "v": val("reason"),
            "id": "the_reason",
            "r": True,
            "c": "col-md-12",
            "b": "textarea.html",
        },
    ]