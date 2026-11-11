# applications/core/jalali_period.py

"""
ابزارهای بازه‌های شمسی
"""

from datetime import datetime, date
from django.utils import timezone
import jdatetime


def get_current_jalali_year_range() -> tuple[datetime, datetime]:
    """
    بازه‌ی سال شمسی جاری را برمی‌گرداند.
    خروجی: (اول فروردین ۰۰:۰۰:۰۰ تا آخر اسفند ۲۳:۵۹:۵۹) به صورت datetime aware (تهران).
    """
    now_local = timezone.localtime(timezone.now())
    now_j = jdatetime.datetime.fromgregorian(datetime=now_local)
    year = now_j.year

    start_j = jdatetime.datetime(year, 1, 1, 0, 0, 0)
    end_j = jdatetime.datetime(year + 1, 1, 1, 0, 0, 0)

    start_g = start_j.togregorian()
    end_g = end_j.togregorian()

    tz = timezone.get_current_timezone()
    return (
        timezone.make_aware(start_g, tz),
        timezone.make_aware(end_g, tz),
    )


def get_current_jalali_year() -> int:
    """سال شمسی جاری"""
    now_local = timezone.localtime(timezone.now())
    return jdatetime.datetime.fromgregorian(datetime=now_local).year