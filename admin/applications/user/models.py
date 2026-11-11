#######    applications/user/models.py

import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import random
import string

from applications.core.baseModel import SoftDeleteModel, BaseModel
from applications.core.utils import hash_code, generate_verification_code
from applications.core.validators import validate_mobile

#######################################
# User
#######################################
class User(AbstractUser, SoftDeleteModel):
    
    class UserNature(models.TextChoices):
        USER = "user", "کاربر عادی"
        MANAGER = "manager", "مدیر"
        SELLER = "seller", "فروشنده"
        EXECUTIVE = "executive", "مجری"

    nature = models.CharField(max_length=16, choices=UserNature.choices, default=UserNature.USER, verbose_name="نوع کاربری")
    mobile = models.CharField(max_length=20, unique=True, null=True, blank=True, validators=[validate_mobile])
    uuid = models.UUIDField(max_length=50 ,default=uuid.uuid4, unique=True, editable=False, verbose_name="شناسه یکتا")

    # وضعیت تایید
    is_mobile_verified = models.BooleanField(default=False, verbose_name="موبایل تایید شده")

    # ظاهر و تنظیمات
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', null=True, blank=True, verbose_name="آواتار")

    # امنیت (فقط همین یک فیلد برای زمان تغییر رمز نیاز است)
    password_changed_at = models.DateTimeField(default=timezone.now, verbose_name="آخرین تغییر رمز")

    # زمان
    last_active_at = models.DateTimeField(auto_now=True, verbose_name="آخرین فعالیت")

    referral_code = models.CharField(max_length=10, unique=True, null=True, blank=True, verbose_name="کد دعوت")
    
    role_ids = models.JSONField(default=list)

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'user_user'
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['mobile']),
            models.Index(fields=['uuid']),
        ]

    def __str__(self):
        return self.get_full_name() or self.email

    def save(self, *args, **kwargs):
        # اگر کاربر جدید است و کد دعوت ندارد، یک کد تصادفی بساز
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
        super().save(*args, **kwargs)
    
    def generate_referral_code(self):
        """ساخت کد 6 رقمی تصادفی یکتا"""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not User.objects.filter(referral_code=code).exists():
                return code
            
    @property
    def full_name(self):
        """نام کامل"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @property
    def short_name(self):
        """نام کوتاه"""
        return self.first_name or self.username

    @property
    def is_password_expired(self) -> bool:
        """بررسی انقضای رمز عبور (7 روز)"""
        if not self.password_changed_at:
            return False
        return (timezone.now() - self.password_changed_at) > timezone.timedelta(days=7)

    @property
    def get_profile_info(self):
        """دریافت پروفایل (بدون کرش کردن در صورت نبود)"""
        # با استفاده از getattr، در صورت نبود پروفایل، None برمی‌گرداند
        return getattr(self, 'relation_profile', None)

    @property
    def get_score(self):
        """دریافت امتیاز (بدون کرش کردن در صورت نبود)"""
        return getattr(self, 'relation_score', None)

    @property
    def get_invitations(self):
        """دریافت لیست دعوت‌های ارسالی (همیشه QuerySet برمی‌گرداند)"""
        # برای روابط Many، همیشه Manager وجود دارد. نیازی به try/except نیست.
        return self.relation_sent_invitations.all()

    @property
    def get_score_logs(self):
        """دریافت تاریخچه امتیازات (همیشه QuerySet برمی‌گرداند)"""
        return self.user_score_logs.all()

    @property
    def get_inviter(self):
        """
        دریافت اطلاعات دعوت‌کننده (چه کسی این کاربر را دعوت کرده است)
        با استفاده از getattr، در صورت وجود نداشتن، None برمی‌گرداند.
        """
        try:
            invitation = getattr(self, 'relation_received_invitation', None)
            if invitation:
                return invitation.inviter
            return None
        except Exception:
            return None
        
        
    
#######################################
# اطلاعات تکمیلی 
#######################################
class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='relation_profile', verbose_name="کاربر")
    
    # ==========================================
    # اطلاعات شخصی
    # ==========================================
    national_code = models.CharField(max_length=10, unique=True, null=True, blank=True, verbose_name="کد ملی")
    birth_date = models.DateField(null=True, blank=True, verbose_name="تاریخ تولد")
    gender = models.CharField(max_length=10, choices=[('male', 'مرد'), ('female', 'زن')], null=True, blank=True, verbose_name="جنسیت")
    address = models.TextField(null=True, blank=True, verbose_name="آدرس")
    post_code = models.CharField(max_length=20, null=True, blank=True, verbose_name="کدپستی")
    province = models.ForeignKey("app_setting.Province", on_delete=models.SET_NULL, null=True, blank=True, related_name='user_profiles')
    city = models.ForeignKey("app_setting.City", on_delete=models.SET_NULL,  null=True, blank=True, related_name='user_profiles')
    
    # ==========================================
    # اطلاعات شغلی / سازمانی
    # ==========================================
    job_title = models.CharField(max_length=100, null=True, blank=True, verbose_name="عنوان شغلی")
    company_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="نام شرکت")

    class Meta:
        db_table = 'user_user_profile'
        verbose_name = 'پروفایل کاربر'
        verbose_name_plural = 'پروفایل‌های کاربران'

    def __str__(self):
        return f"Profile of {self.user.mobile}"
    
    
#######################################
# مدرک شغلی
#######################################
class JobCertificate(BaseModel):
    class FileType(models.TextChoices):
        License = "valid_business_license", "جواز کسب  معتبر"
        Technical = "technical_professional_certificate", "مدرک فنی و حرفه ای"
        Introduction = "letter_of_introduction", "معرفی نامه از نمایندگی آذر"
        
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_job_certificates', verbose_name="کاربر")
    
    type = models.CharField(max_length=100, choices=FileType, default=FileType.License)
    file = models.FileField(upload_to='certificates/%Y/%m/', verbose_name="file")
    file_size = models.PositiveIntegerField(default=0, verbose_name="حجم فایل (بایت)")
    file_type = models.CharField(max_length=100, blank=True, default="", verbose_name="نوع فایل")
    is_verified = models.BooleanField(default=False, verbose_name="تایید شده")
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان تایید")

    class Meta:
        db_table = 'user_job_certificate'
        unique_together = ('user', 'type')

    def __str__(self):
        return f"{self.get_type_display()} - {self.user.mobile}"
    
    
#######################################
#  علاقه مندی ها
#######################################
class FavoriteQuestion(BaseModel):    
    question = models.CharField(max_length=255, verbose_name="سوال")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        db_table = 'user_favorite_question'

    def __str__(self):
        return self.question 
    
    
class FavoriteAnswerItem(models.TextChoices):
    VeryLittle = "very_little", "خیلی کم"
    Little = "little", "کم"
    Average = "average", "متوسط"
    ALot = "a_lot", "زیاد"
    VeryMuch = "very_much", "خیلی زیاد"
    

class FavoriteAnswer(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_favorite_answers')
    question = models.ForeignKey(FavoriteQuestion, on_delete=models.CASCADE, related_name='relation_answers')
    answer = models.CharField(max_length=50, choices=FavoriteAnswerItem, default=FavoriteAnswerItem.VeryLittle)

    class Meta:
        db_table = 'user_favorite_answer'
        unique_together = ('user', 'question')

    def __str__(self):
        return f"FavoriteAnswer of {self.user.mobile}"

    
#######################################
# Invitation (دعوت از دوستان)
#######################################
class UserInvitation(BaseModel):
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='relation_sent_invitations',  verbose_name="دعوت‌کننده")
    
    # شماره موبایلی که دعوت شده (ممکن است هنوز ثبت‌نام نکرده باشد)
    invited_mobile = models.CharField(max_length=20, unique=True, verbose_name="موبایل دعوت‌شده")
    
    # اگر کاربر ثبت‌نام کرد، این فیلد پر می‌شود
    invited_user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='relation_received_invitation', verbose_name="کاربر دعوت‌شده")
    
    # وضعیت
    is_rewarded = models.BooleanField(default=False, verbose_name="پاداش داده شده")
    rewarded_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان پاداش")
        
    class Meta:
        db_table = 'user_invitation'
        verbose_name = 'دعوت'
        verbose_name_plural = 'دعوت‌ها'
        unique_together = ('inviter', 'invited_mobile') # جلوگیری از ثبت تکراری

    def __str__(self):
        return f"{self.inviter.mobile} invited {self.invited_mobile}"


#######################################
# Verify (VerificationCode)
#######################################
class VerificationCode(models.Model):
    class Purpose(models.TextChoices):
        LOGIN = 'login', 'ورود'
        REGISTER = 'register', 'ثبت‌نام'
        FORGOT = 'forgot', "فراموشی رمزعبور"
        RESEND = 'resend', "ارسال مجدد کد"
        RESET_PASSWORD = 'reset_password', 'بازیابی رمز'
        VERIFY_EMAIL = 'verify_email', 'تایید ایمیل'
        VERIFY_MOBILE = 'verify_mobile', 'تایید موبایل'
        DELETE_ACCOUNT = 'delete_account', 'حذف حساب'

    # اطلاعات
    identifier = models.CharField(max_length=255, db_index=True, help_text="ایمیل یا شماره موبایل")
    code_hash = models.CharField(max_length=128, verbose_name="هش کد")
    purpose = models.CharField(max_length=20, choices=Purpose.choices, default=Purpose.LOGIN, verbose_name="هدف")

    # وضعیت
    expires_at = models.DateTimeField(verbose_name="زمان انقضا")
    attempts = models.IntegerField(default=0, verbose_name="تعداد تلاش")
    is_used = models.BooleanField(default=False, verbose_name="استفاده شده")

    # متادیتا
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP درخواست")
    user_agent = models.TextField(null=True, blank=True, verbose_name="مرورگر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")

    class Meta:
        db_table = 'user_verification'
        verbose_name = 'کد تایید'
        verbose_name_plural = 'کدهای تایید'
        indexes = [
            models.Index(fields=['identifier', 'purpose']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.purpose} - {self.identifier}"

    @property
    def is_valid(self) -> bool:
        """بررسی معتبر بودن کد"""
        return not self.is_used and timezone.now() < self.expires_at

    def verify(self, code: str) -> bool:
        """تایید کد وارد شده"""
        if not self.is_valid:
            return False

        self.attempts += 1

        if self.code_hash == hash_code(code):
            self.is_used = True
            self.save(update_fields=['is_used', 'attempts'])
            return True

        self.save(update_fields=['attempts'])
        return False

    @classmethod
    def create_code(cls, identifier: str, purpose: str, ttl_seconds: int = 600, code_length: int = 4):
        # ✅ ۱. حذف کدهای منقضی‌شده در کل سیستم (بیش از 5 دقیقه از ساختشان گذشته)
        expiration_threshold = timezone.now() - timezone.timedelta(minutes=5)
        cls.objects.filter(created_at__lt=expiration_threshold).delete()

        # ✅ ۲. حذف کدهای استفاده‌نشده قبلی برای همین شماره و همین هدف
        # (تا همیشه فقط یک کد فعال برای هر شماره و هدف وجود داشته باشد)
        cls.objects.filter(
            identifier=identifier,
            purpose=purpose,
            is_used=False
        ).delete()

        # ✅ ۳. ساخت کد جدید
        # code = generate_verification_code(code_length)
        code = "1234"
        code_hash = hash_code(code)

        verification = cls.objects.create(
            identifier=identifier,
            code_hash=code_hash,
            purpose=purpose,
            expires_at=timezone.now() + timezone.timedelta(seconds=ttl_seconds)
        )

        return verification, code


#######################################
# Device
#######################################
class UserDevice(BaseModel):
    class DeviceType(models.TextChoices):
        MOBILE = 'mobile', 'موبایل'
        TABLET = 'tablet', 'تبلت'
        DESKTOP = 'desktop', 'کامپیوتر'
        BOT = 'bot', 'ربات'
        OTHER = 'other', 'سایر'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices', verbose_name="کاربر")

    # شناسایی دستگاه
    device_name = models.CharField(max_length=255, verbose_name="نام دستگاه")
    device_type = models.CharField(max_length=20, choices=DeviceType.choices, default=DeviceType.DESKTOP)

    # اطلاعات اتصال
    ip_address = models.GenericIPAddressField(verbose_name="آدرس IP")
    user_agent = models.TextField(verbose_name="مرورگر/سیستم عامل")

    # وضعیت
    is_trusted = models.BooleanField(default=False, verbose_name="دستگاه معتمد")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    # زمان
    last_active = models.DateTimeField(auto_now=True, verbose_name="آخرین فعالیت")

    class Meta:
        db_table = 'user_device'
        verbose_name = 'دستگاه'
        verbose_name_plural = 'دستگاه‌ها'

    def __str__(self):
        return f"{self.device_name} - {self.user.email}"

    def mark_trusted(self):
        """علامت‌گذاری به عنوان دستگاه معتمد"""
        self.is_trusted = True
        self.save(update_fields=['is_trusted'])


#######################################
#   توکن بازخوانی JWT
#######################################
class RefreshToken(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens', verbose_name="کاربر")
    device = models.ForeignKey(UserDevice, on_delete=models.CASCADE, null=True, blank=True, related_name='tokens')

    token = models.CharField(max_length=255, unique=True, verbose_name="توکن")
    expires_at = models.DateTimeField(verbose_name="زمان انقضا")
    revoked_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان لغو")

    class Meta:
        db_table = 'user_refresh_token'
        verbose_name = 'توکن بازخوانی'
        verbose_name_plural = 'توکن‌های بازخوانی'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def revoke(self):
        """لغو توکن"""
        self.revoked_at = timezone.now()
        self.save(update_fields=['revoked_at'])
        