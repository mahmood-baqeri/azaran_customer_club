
"""
سرویس‌های اپ کاربر (فقط دعوت).
تمام عملیات امتیاز از طریق applications.score.services انجام می‌شود.
"""
import logging
from django.db import transaction
from django.utils import timezone

from applications.score.models import UserScoreLog
from applications.score.services import ScoreError, record_score_transaction
from applications.user.models import User, UserInvitation

logger = logging.getLogger(__name__)


def send_invitation_sms(inviter: User, invited_mobile: str):
    """ثبت دعوت و ارسال پیامک به شماره‌ای که هنوز عضو نشده."""
    if inviter.mobile == invited_mobile:
        return False, "نمی‌توانید خودتان را دعوت کنید"

    if User.objects.filter(mobile=invited_mobile).exists():
        return False, "این شماره قبلاً در سیستم ثبت‌نام کرده است"

    if UserInvitation.objects.filter(invited_mobile=invited_mobile).exists():
        return False, "این شماره قبلاً توسط شخص دیگری دعوت شده است"

    try:
        with transaction.atomic():
            UserInvitation.objects.create(
                inviter=inviter,
                invited_mobile=invited_mobile,
            )
        return True, "دعوت با موفقیت ثبت و پیامک ارسال شد"
    except Exception as e:
        logger.exception("invitation failed")
        return False, f"خطا در ثبت دعوت: {str(e)}"


def process_referral_code(new_user: User, referral_code_input: str):
    """پردازش کد دعوت در زمان ثبت‌نام."""
    if not referral_code_input:
        return False, "کد دعوت وارد نشده است"

    inviter = User.objects.filter(
        referral_code=referral_code_input.strip().upper()
    ).first()
    if not inviter:
        return False, "کد دعوت نامعتبر است"

    if inviter.id == new_user.id:
        return False, "نمی‌توانید از کد دعوت خودتان استفاده کنید"

    existing = UserInvitation.objects.filter(invited_mobile=new_user.mobile).first()
    if existing:
        if existing.inviter_id == inviter.id:
            return True, "کد دعوت شما قبلاً ثبت شده است"
        return False, "این شماره قبلاً توسط شخص دیگری دعوت شده است"

    try:
        with transaction.atomic():
            UserInvitation.objects.create(
                inviter=inviter,
                invited_mobile=new_user.mobile,
                invited_user=new_user,
                is_rewarded=False,
            )
        return True, "کد دعوت با موفقیت ثبت شد. پاداش پس از تایید شرایط اعطا می‌شود."
    except Exception as e:
        logger.exception("referral registration failed")
        return False, f"خطا در ثبت کد دعوت: {str(e)}"



def reward_referral_after_verification(user: User):
    """
    پاداش دعوت بعد از تأیید نفر دعوت‌شده.
    طبق اکسل: ۲۰ امتیاز برای هر نفر (دعوت‌کننده و دعوت‌شده).
    strict=True → اگه امتیاز نده، کل تراکنش rollback می‌شه.
    """
    from applications.score import api as score_api

    try:
        with transaction.atomic():
            invitation = (
                UserInvitation.objects
                .select_for_update()
                .filter(invited_user=user, is_rewarded=False)
                .first()
            )
            if not invitation:
                return

            # ۱) پاداش دعوت‌کننده
            score_api.award(
                invitation.inviter,
                "REFERRAL",
                reference_type="invitation",
                reference_id=f"{invitation.id}:inviter",
                reason=f"دعوت موفق {user.mobile}",
                extra={"role": "inviter", "invited_user_id": user.id},
                strict=True,   # ← fail loud
            )

            # ۲) پاداش دعوت‌شده
            score_api.award(
                user,
                "REFERRAL",
                reference_type="invitation",
                reference_id=f"{invitation.id}:invited",
                reason="هدیه ثبت‌نام با کد دعوت",
                extra={"role": "invited", "inviter_id": invitation.inviter_id},
                strict=True,   # ← fail loud
            )

            # ۳) علامت‌گذاری — فقط اگه هر دو موفق
            invitation.is_rewarded = True
            invitation.rewarded_at = timezone.now()
            invitation.save(update_fields=["is_rewarded", "rewarded_at"])

    except ScoreError as e:
        logger.warning("[referral] skipped for user=%s: %s", user.id, e)
    except Exception:
        logger.exception("[referral] unexpected error for user=%s", user.id)
        
        
# from applications.user.services import process_referral_code


# FastAPI (register):
# @router.post("/register/")
# async def register(form: dict = Depends(DependencyDataRequest)):
#     mobile = form.get("mobile")
#     referral_code = form.get("referral_code") # دریافت از ورودی
    
#     # ... (ساخت کاربر) ...
    
#     if referral_code:
#         success, message = await sync_to_async(process_referral_code)(user, referral_code)
#         # می‌توانید در لاگ ثبت کنید یا پیام موفقیت را در ریسپانس بگنجانید
        
#     return success_response("Verification code sent")


# Django 
# referral_input = request.POST.get('referral_code') # دریافت از فرم

# if referral_input:
#     success, message = process_referral_code(user, referral_input)
#     if success:
#         messages.success(request, message)
#     else:
#         messages.warning(request, message)