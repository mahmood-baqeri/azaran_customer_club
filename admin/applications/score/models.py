# admin/applications/score/models.py

from django.db import models
from applications.core.baseModel import BaseModel
# ⚠️ User را از اپ user می‌گیریم — این FK تنها نقطه اتصال دو اپ است
from applications.user.models import User


#######################################
# User Score (خلاصه امتیازات)
#######################################
class UserScore(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='relation_score', verbose_name="کاربر")
    
    # موجودی فعلی
    current_balance = models.IntegerField(default=0, verbose_name="موجودی فعلی")
    
    # جمع کل
    total_earned = models.IntegerField(default=0, verbose_name="جمع کل دریافتی")
    total_spent = models.IntegerField(default=0, verbose_name="جمع کل مصرفی")

    class Meta:
        db_table = 'score_score'
        verbose_name = 'امتیاز کاربر'
        verbose_name_plural = 'امتیازات کاربران'

    def __str__(self):
        return f"{self.user.mobile} - Balance: {self.current_balance}"
      

#######################################
# User Score Log (تاریخچه امتیازات)
#######################################
class UserScoreLog(BaseModel):
    # ──────────────────────────────────────────────────────
    # جهت تراکنش (فقط همین دو تا؛ جدا از کد)
    # ──────────────────────────────────────────────────────
    class Direction(models.TextChoices):
        EARNED = "earned", "دریافت"
        SPENT  = "spent",  "مصرف"

    # ──────────────────────────────────────────────────────
    # کدهای ۲۶گانه طبق اکسل باشگاه مشتریان آذران
    # ──────────────────────────────────────────────────────
    class TransactionCode(models.TextChoices):
        # ── EARN ──
        SIGNUP                  = "SIGNUP",                  "ثبت‌نام"
        PROFILE_PERSONAL_INFO   = "PROFILE_PERSONAL_INFO",   "تکمیل مشخصات فردی"
        PROFILE_BIRTH_DATE      = "PROFILE_BIRTH_DATE",      "ثبت تاریخ تولد"
        PROFILE_JOB_DOCUMENTS   = "PROFILE_JOB_DOCUMENTS",   "بارگذاری مدارک شغلی"
        PROFILE_INTERESTS       = "PROFILE_INTERESTS",       "تکمیل علایق و سلایق"
        INVOICE                 = "INVOICE",                 "ثبت فاکتور"
        INVOICE_PARTICIPATION   = "INVOICE_PARTICIPATION",   "مشارکت در فاکتور"
        PROJECT                 = "PROJECT",                 "ثبت پروژه"
        PROJECT_PARTICIPATION   = "PROJECT_PARTICIPATION",   "مشارکت در پروژه"
        REFERRAL                = "REFERRAL",                "دعوت همکار"
        DAILY_QUIZ              = "DAILY_QUIZ",              "کوئیز روزانه"
        TREASURE_HUNT           = "TREASURE_HUNT",           "گنج‌یابی"
        PUZZLE                  = "PUZZLE",                  "پازل محصولات"
        FORTUNE_WHEEL           = "FORTUNE_WHEEL",           "گردونه شانس"
        LUCKY_BOX               = "LUCKY_BOX",               "جعبه شانس"
        WEEKLY_STREAK           = "WEEKLY_STREAK",           "تکمیل هفته (استریک)"
        SURVEY                  = "SURVEY",                  "شرکت در نظرسنجی"
        FRIDAY_CHECKIN          = "FRIDAY_CHECKIN",          "حضور در قرار جمعه"
        QA_QUESTION             = "QA_QUESTION",             "پرسیدن سؤال"
        QA_ANSWER               = "QA_ANSWER",               "پاسخ دادن"
        GALLERY_TOP             = "GALLERY_TOP",             "عکس برتر هفته در گالری"
        ORDER_REFUND            = "ORDER_REFUND",            "برگشت امتیاز با لغو سفارش"
        # ── SPEND ──
        GIFT_REDEEM             = "GIFT_REDEEM",             "خرید هدیه از ویترین"
        CUSTOM_GIFT             = "CUSTOM_GIFT",             "هدیه سفارشی"
        EXPIRE                  = "EXPIRE",                  "انقضای امتیاز"
        # ── EARN / SPEND (بسته به موقعیت) ──
        ADMIN_ADJUST            = "ADMIN_ADJUST",            "تنظیم دستی توسط ادمین"
        # ── مهاجرت داده‌های قدیمی ──
        LEGACY                  = "LEGACY",                  "قدیمی (مهاجرت)"

    # ──────────────────────────────────────────────────────
    # منبع تراکنش
    # ──────────────────────────────────────────────────────
    class Source(models.TextChoices):
        USER   = "user",   "کاربر"
        SYSTEM = "system", "سیستم"
        ADMIN  = "admin",  "ادمین"

    # ──────────────────────────────────────────────────────
    # فیلدها
    # ──────────────────────────────────────────────────────
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_score_logs", verbose_name="کاربر")
    transaction_code = models.CharField(max_length=32, choices=TransactionCode.choices, db_index=True, verbose_name="کد نوع تراکنش")
    direction = models.CharField(max_length=10, choices=Direction.choices, db_index=True, verbose_name="جهت")
    amount = models.PositiveIntegerField(verbose_name="مقدار امتیاز", help_text="برای شکست در بازی‌ها/کوئیز، مقدار صفر (۰) ذخیره شود")

    balance_before = models.IntegerField(verbose_name="موجودی قبل از تراکنش")
    balance_after  = models.IntegerField(verbose_name="موجودی بعد از تراکنش")

    # منبع و متادیتا
    reference_type = models.CharField(max_length=32, null=True, blank=True, verbose_name="نوع مرجع", 
                                      help_text="invoice / project / promotion_order / gift_order / ...")
    reference_id = models.CharField(max_length=100, null=True, blank=True, db_index=True, verbose_name="شناسه مرجع")
    idempotency_key = models.CharField(max_length=128, null=True, blank=True, db_index=True, verbose_name="کلید یکتایی", 
                                       help_text="مثال: SIGNUP:user_42 | DAILY_QUIZ:user_42:2025-01-15")
    
    extra_data = models.JSONField(default=dict, blank=True, verbose_name="داده اضافی", 
                                  help_text="JSON: admin_note, invoice_amount, share_percent, wheel_result ...")
    
    source = models.CharField(max_length=10, choices=Source.choices, default=Source.SYSTEM, verbose_name="منبع")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="relation_score_logs_created",
                                   verbose_name="ایجادکننده", help_text="برای ADMIN_ADJUST یا اصلاح دستی")
    reason = models.CharField(max_length=255, null=True, blank=True, verbose_name="توضیح")

    # برگشت تراکنش
    is_reversed = models.BooleanField(default=False, verbose_name="برگشت‌خورده")
    reversed_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان برگشت")
    reverses_log = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="reversal_logs", 
                                     verbose_name="برگشتِ", help_text="این لاگ، کدام تراکنش اصلی را برگشت زده است (برای ORDER_REFUND و اصلاح ادمین)")

    class Meta:
        db_table = "score_log"
        verbose_name = "تاریخچه امتیاز"
        verbose_name_plural = "تاریخچه امتیازات"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"], name="ix_score_user_created"),
            models.Index(fields=["user", "transaction_code"], name="ix_score_user_code"),
            models.Index(fields=["reference_type", "reference_id"], name="ix_score_ref"),
            models.Index(fields=["transaction_code", "-created_at"], name="ix_score_code_created"),
        ]
        constraints = [
            # یکتا بودن idempotency_key برای هر کاربر
            models.UniqueConstraint(
                fields=["user", "idempotency_key"],
                condition=models.Q(idempotency_key__isnull=False),
                name="uniq_score_user_idempotency",
            ),
            # یکتا بودن (user, code, reference) وقتی reference موجود است
            models.UniqueConstraint(
                fields=["user", "transaction_code", "reference_id"],
                condition=models.Q(reference_id__isnull=False),
                name="uniq_score_user_code_reference",
            ),
        ]

    def __str__(self):
        sign = "+" if self.direction == self.Direction.EARNED else "-"
        return f"{self.user_id} {sign}{self.amount} [{self.transaction_code}]"   


#######################################
#    
#    قاعده امتیازدهی برای هر نوع تراکنش.
#    یک ردیف برای هر transaction_code.
#
#######################################
class ScoreRule(BaseModel):

    class CalcType(models.TextChoices):
        FIXED       = "fixed",       "مقدار ثابت"
        PERCENT     = "percent",     "درصد از مبلغ مبنا"
        PER_UNIT    = "per_unit",    "به ازای هر واحد/نفر"
        PER_LEVEL   = "per_level",   "وابسته به سطح کاربر"
        RANDOM      = "random",      "تصادفی (گردونه/جعبه)"

    class CapPeriod(models.TextChoices):
        DAILY   = "daily",   "روزانه"
        WEEKLY  = "weekly",  "هفتگی"
        MONTHLY = "monthly", "ماهانه"
        YEARLY  = "yearly",  "سالانه"
        ONCE    = "once",    "یک‌بار برای همیشه"

    # ──────────────────────────────────────────────────────
    # شناسه — همون کد تراکنش
    # ──────────────────────────────────────────────────────
    code = models.CharField(
        max_length=32,
        choices=UserScoreLog.TransactionCode.choices,
        unique=True,
        verbose_name="کد تراکنش",
        help_text="هر کد فقط یک قاعده دارد. برای تغییر مقدار، همین ردیف را ویرایش کنید.",
    )

    # ──────────────────────────────────────────────────────
    # مقدار
    # ──────────────────────────────────────────────────────
    calc_type = models.CharField(
        max_length=16,
        choices=CalcType.choices,
        default=CalcType.FIXED,
        verbose_name="نوع محاسبه",
    )
    default_amount = models.PositiveIntegerField(
        default=0,
        verbose_name="مقدار پیش‌فرض",
        help_text=(
            "برای FIXED: مقدار امتیاز | "
            "برای PERCENT: درصد (مثلاً 5 برای ۵٪) | "
            "برای PER_UNIT: امتیاز به ازای هر واحد/نفر | "
            "برای PER_LEVEL و RANDOM: استفاده نمی‌شود (از metadata)"
        ),
    )

    # ──────────────────────────────────────────────────────
    # محدودیت تکرار
    # ──────────────────────────────────────────────────────
    cap_period = models.CharField(
        max_length=10,
        choices=CapPeriod.choices,
        null=True,
        blank=True,
        verbose_name="دوره محدودیت",
        help_text="خالی = بدون سقف تکرار (مثلاً فاکتور)",
    )
    cap_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="حداکثر تعداد در دوره",
        help_text="مثال: TREASURE_HUNT با cap_period=daily و cap_count=3",
    )
    max_amount_per_period = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="حداکثر امتیاز در دوره",
        help_text="سقف مجموع امتیاز در دوره (اختیاری)",
    )

    # ──────────────────────────────────────────────────────
    # شرط و پاداش
    # ──────────────────────────────────────────────────────
    requires_reference = models.BooleanField(
        default=False,
        verbose_name="نیاز به مرجع",
        help_text="اگر True، reference_id در ثبت تراکنش الزامی است",
    )
    requires_approval = models.BooleanField(
        default=False,
        verbose_name="نیاز به تأیید",
        help_text="مثل مدارک شغلی یا فاکتور — تا تأیید نشود امتیاز ثبت نمی‌شود",
    )

    # ──────────────────────────────────────────────────────
    # فعال/غیرفعال و متادیتا
    # ──────────────────────────────────────────────────────
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
        help_text="اگر False، هیچ تراکنشی از این نوع ثبت نمی‌شود",
    )
    priority = models.PositiveSmallIntegerField(
        default=100,
        verbose_name="اولویت",
        help_text="در صورت تداخل قواعد، عدد کمتر = اولویت بالاتر",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="داده اضافی",
        help_text=(
            "JSON برای تنظیمات خاص. مثال‌ها:\n"
            "  PER_LEVEL: {'level_amounts': {'bronze': 10, 'silver': 20, 'gold': 30}}\n"
            "  RANDOM:    {'options': [0, 1, 2, 3, 5, 10], 'weights': [10, 20, 20, 20, 20, 10]}\n"
            "  PER_UNIT:  {'min_units': 1, 'max_units': 100}\n"
            "  EXPIRE:    {'expire_after_days': 365}"
        ),
    )

    # ──────────────────────────────────────────────────────
    # بازه اعتبار قاعده (برای تعطیلات، کمپین و ...)
    # ──────────────────────────────────────────────────────
    valid_from = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="معتبر از",
    )
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="معتبر تا",
    )

    class Meta:
        db_table = "score_rule"
        verbose_name = "قاعده امتیاز"
        verbose_name_plural = "قواعد امتیاز"
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"], name="ix_rule_code"),
            models.Index(fields=["is_active"], name="ix_rule_active"),
        ]

    def __str__(self):
        return f"{self.get_code_display()} ({self.get_calc_type_display()}: {self.default_amount})"

    # ──────────────────────────────────────────────────────
    # متدهای کمکی
    # ──────────────────────────────────────────────────────
    def is_currently_valid(self) -> bool:
        """آیا قاعده همین الان معتبر است؟"""
        from django.utils import timezone
        now = timezone.now()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return self.is_active

    def compute_amount(
        self,
        *,
        base_value: int | None = None,
        units: int | None = None,
        level: str | None = None,
    ) -> int:
        """
        محاسبه مقدار امتیاز بر اساس calc_type.

        Parameters
        ----------
        base_value : مبلغ فاکتور/پروژه (برای PERCENT)
        units      : تعداد واحد یا نفر (برای PER_UNIT)
        level      : سطح کاربر (برای PER_LEVEL)
        """
        import random as _random

        if self.calc_type == self.CalcType.FIXED:
            return self.default_amount

        if self.calc_type == self.CalcType.PERCENT:
            if base_value is None:
                raise ValueError("base_value لازم است برای PERCENT")
            return int(base_value * self.default_amount / 100)

        if self.calc_type == self.CalcType.PER_UNIT:
            if units is None:
                raise ValueError("units لازم است برای PER_UNIT")
            return self.default_amount * units

        if self.calc_type == self.CalcType.PER_LEVEL:
            level_amounts = self.metadata.get("level_amounts", {})
            return int(level_amounts.get(level or "bronze", 0))

        if self.calc_type == self.CalcType.RANDOM:
            options = self.metadata.get("options", [self.default_amount])
            weights = self.metadata.get("weights")
            if weights and len(weights) == len(options):
                return _random.choices(options, weights=weights, k=1)[0]
            return _random.choice(options)

        return self.default_amount
    