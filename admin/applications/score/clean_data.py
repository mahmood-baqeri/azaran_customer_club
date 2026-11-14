# applications/score/clean_data.py

import json

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import ScoreRule, UserScoreLog


def _parse_dt(value):
    """تبدیل رشته به datetime آگاه به timezone. None برای خالی."""
    value = (value or "").strip()
    if not value:
        return None
    dt = parse_datetime(value)
    if dt is None:
        # تاریخ خالص
        try:
            from datetime import datetime
            dt = datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt)
    return dt


# ═══════════════════════════════════════════════════════════
# SCORE RULE
# ═══════════════════════════════════════════════════════════
def score_rule__clean__data(post, current_rule=None):
    """اعتبارسنجی فرم قاعده امتیاز.

    خروجی: (cleaned, errors)
    """
    errors = []

    code = (post.get("code") or "").strip()
    if not code or code not in dict(UserScoreLog.TransactionCode.choices):
        errors.append("کد تراکنش معتبر نیست")
    elif current_rule is None:
        if ScoreRule.objects.filter(code=code).exists():
            errors.append("این کد قبلاً قاعده دارد — به‌جای ایجاد، ویرایش کنید")

    calc_type = (post.get("calc_type") or "fixed").strip()
    if calc_type not in dict(ScoreRule.CalcType.choices):
        errors.append("نوع محاسبه نامعتبر است")

    # مقدار پیش‌فرض
    default_amount_raw = (post.get("default_amount") or "0").strip()
    if not default_amount_raw.isdigit():
        errors.append("مقدار پیش‌فرض باید عدد نامنفی باشد")
        default_amount_raw = "0"

    # cap_period
    cap_period = (post.get("cap_period") or "").strip() or None
    if cap_period and cap_period not in dict(ScoreRule.CapPeriod.choices):
        errors.append("دوره محدودیت نامعتبر است")

    cap_count = (post.get("cap_count") or "").strip()
    if cap_count and not cap_count.isdigit():
        errors.append("حداکثر تعداد در دوره باید عدد باشد")
        cap_count = ""

    max_amount = (post.get("max_amount_per_period") or "").strip()
    if max_amount and not max_amount.isdigit():
        errors.append("حداکثر امتیاز در دوره باید عدد باشد")
        max_amount = ""

    priority_raw = (post.get("priority") or "100").strip()
    if not priority_raw.isdigit():
        errors.append("اولویت باید عدد باشد")
        priority_raw = "100"

    # metadata JSON
    metadata_raw = (post.get("metadata") or "").strip()
    metadata = {}
    if metadata_raw:
        try:
            metadata = json.loads(metadata_raw)
            if not isinstance(metadata, dict):
                errors.append("metadata باید یک object JSON باشد (با {})")
                metadata = {}
        except json.JSONDecodeError as e:
            errors.append(f"metadata معتبر نیست: {e}")
            metadata = {}

    # بازه اعتبار
    valid_from = _parse_dt(post.get("valid_from"))
    valid_until = _parse_dt(post.get("valid_until"))
    if valid_from and valid_until and valid_until < valid_from:
        errors.append("«معتبر تا» نمی‌تواند قبل از «معتبر از» باشد")

    if errors:
        return {}, errors

    return {
        "code": code,
        "calc_type": calc_type,
        "default_amount": int(default_amount_raw),
        "cap_period": cap_period,
        "cap_count": int(cap_count) if cap_count else None,
        "max_amount_per_period": int(max_amount) if max_amount else None,
        "requires_reference": str(post.get("requires_reference", "")).lower() in ("on", "true", "1"),
        "requires_approval": str(post.get("requires_approval", "")).lower() in ("on", "true", "1"),
        "is_active": str(post.get("is_active", "")).lower() in ("on", "true", "1"),
        "priority": int(priority_raw),
        "metadata": metadata,
        "valid_from": valid_from,
        "valid_until": valid_until,
    }, []


# ═══════════════════════════════════════════════════════════
# MANUAL ADJUST (تنظیم دستی توسط ادمین)
# ═══════════════════════════════════════════════════════════
def score_adjust__clean__data(post):
    """اعتبارسنجی فرم تنظیم دستی امتیاز.

    خروجی: (cleaned, errors)
    """
    errors = []

    direction = (post.get("direction") or "").strip()
    if direction not in dict(UserScoreLog.Direction.choices):
        errors.append("جهت تراکنش معتبر نیست")

    amount_raw = (post.get("amount") or "").strip()
    if not amount_raw.isdigit() or int(amount_raw) <= 0:
        errors.append("مقدار باید عدد صحیح مثبت باشد")
        amount_raw = "0"

    reason = (post.get("reason") or "").strip()
    if not reason:
        errors.append("دلیل الزامی است")
    elif len(reason) > 255:
        errors.append("دلیل حداکثر ۲۵۵ کاراکتر")

    if errors:
        return {}, errors

    return {
        "direction": direction,
        "amount": int(amount_raw),
        "reason": reason,
    }, []