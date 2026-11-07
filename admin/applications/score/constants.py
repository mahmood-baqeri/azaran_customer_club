"""
ثابت‌های کمکی امتیاز — جداکننده قواعد ثابت از منطق سرویس.
"""
from applications.score.models import UserScoreLog as L


# ──────────────────────────────────────────────────────
# کدهایی که بدون reference هم قابل ثبت هستند
# ──────────────────────────────────────────────────────
ONCE_ONLY_CODES = {
    L.TransactionCode.SIGNUP,
    L.TransactionCode.PROFILE_PERSONAL_INFO,
    L.TransactionCode.PROFILE_BIRTH_DATE,
    L.TransactionCode.PROFILE_JOB_DOCUMENTS,
    L.TransactionCode.PROFILE_INTERESTS,
}

DAILY_CODES = {
    L.TransactionCode.DAILY_QUIZ,
    L.TransactionCode.TREASURE_HUNT,
    L.TransactionCode.FRIDAY_CHECKIN,
}

REFERENCE_REQUIRED_CODES = {
    L.TransactionCode.INVOICE,
    L.TransactionCode.INVOICE_PARTICIPATION,
    L.TransactionCode.PROJECT,
    L.TransactionCode.PROJECT_PARTICIPATION,
    L.TransactionCode.REFERRAL,
    L.TransactionCode.GIFT_REDEEM,
    L.TransactionCode.CUSTOM_GIFT,
    L.TransactionCode.ORDER_REFUND,
}

ADMIN_ONLY_CODES = {
    L.TransactionCode.EXPIRE,
    L.TransactionCode.ADMIN_ADJUST,
    L.TransactionCode.ORDER_REFUND,
}


# ──────────────────────────────────────────────────────
# جهت ثابت هر کد (برای استنتاج direction بدون اجبار به پاس دادن)
# ──────────────────────────────────────────────────────
FIXED_SPENT_CODES = {
    L.TransactionCode.GIFT_REDEEM,
    L.TransactionCode.CUSTOM_GIFT,
    L.TransactionCode.EXPIRE,
}

FIXED_EARNED_CODES = {
    L.TransactionCode.SIGNUP,
    L.TransactionCode.PROFILE_PERSONAL_INFO,
    L.TransactionCode.PROFILE_BIRTH_DATE,
    L.TransactionCode.PROFILE_JOB_DOCUMENTS,
    L.TransactionCode.PROFILE_INTERESTS,
    L.TransactionCode.INVOICE,
    L.TransactionCode.INVOICE_PARTICIPATION,
    L.TransactionCode.PROJECT,
    L.TransactionCode.PROJECT_PARTICIPATION,
    L.TransactionCode.REFERRAL,
    L.TransactionCode.DAILY_QUIZ,
    L.TransactionCode.TREASURE_HUNT,
    L.TransactionCode.PUZZLE,
    L.TransactionCode.FORTUNE_WHEEL,
    L.TransactionCode.LUCKY_BOX,
    L.TransactionCode.WEEKLY_STREAK,
    L.TransactionCode.SURVEY,
    L.TransactionCode.FRIDAY_CHECKIN,
    L.TransactionCode.QA_QUESTION,
    L.TransactionCode.QA_ANSWER,
    L.TransactionCode.GALLERY_TOP,
    L.TransactionCode.ORDER_REFUND,
}