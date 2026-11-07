# admin/app_fastapi/views/user/user.py
import jwt
from datetime import datetime, timedelta, timezone

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.contrib.auth.hashers import make_password
from fastapi import APIRouter, HTTPException, Depends, Body, Request, Form

from applications.core.validators import is_valid_iranian_national_code
from app_fastapi.conf.fileManager import get_file_url, handle_save_file
from applications.user.models import RefreshToken, User, UserDevice, UserProfile
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.response import success_response, error_response
from app_fastapi.schemas.user import LogoutSchema
from app_fastapi.views.user.user_helper import get_current_user

router = APIRouter()


def _location_name(obj):
    if not obj:
        return None
    return getattr(obj, "name", None) or getattr(obj, "title", None) or str(obj)


#############################################################################################
# سریالایزر کاربر
#############################################################################################
def user_serialize(user):
    inviter = user.get_inviter
    profile = user.get_profile_info
    score   = user.get_score

    try:
        from applications.user.models import FavoriteQuestion
        favorite_answers_count = user.relation_favorite_answers.count()
        
        # بررسی اینکه آیا کاربر به تمام سوالات فعال پاسخ داده است یا خیر
        total_active_questions = FavoriteQuestion.objects.filter(is_active=True).count()
        if total_active_questions == 0:
            has_answered_all_favorites = True # اگر سوالی وجود ندارد، یعنی همه را پاسخ داده
        else:
            answered_active_count = user.relation_favorite_answers.filter(question__is_active=True).count()
            has_answered_all_favorites = answered_active_count >= total_active_questions
    except Exception:
        favorite_answers_count = 0
        has_answered_all_favorites = False


    job_certs = []
    if hasattr(user, 'relation_job_certificates'):
        job_certs = list(user.relation_job_certificates.all())
        
    base_data = {
        # ==========================================
        # اطلاعات پایه کاربر
        # ==========================================
        "uuid": str(user.uuid),
        "name": user.full_name,
        "firstname": user.first_name,
        "lastname": user.last_name,
        "short_name": user.short_name,
        "avatar": get_file_url(user.avatar),

        "mobile": user.mobile,
        "is_mobile_verified": user.is_mobile_verified,
        "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        "last_active_at": user.last_active_at.isoformat() if user.last_active_at else None,

        "referral_code": user.referral_code,
        "nature": user.nature,
        "nature_display": user.get_nature_display(),

        # ==========================================
        # اطلاعات دعوت‌کننده
        # ==========================================
        "invited_by": {
            "uuid": str(inviter.uuid),
            "name": inviter.full_name,
            "mobile": inviter.mobile,
            "referral_code": inviter.referral_code,
        } if inviter else None,

        # ==========================================
        # امتیاز کاربر
        # ==========================================
        "score": {
            "current_balance": score.current_balance,
            "total_earned": score.total_earned,
            "total_spent": score.total_spent,
        } if score else None,

        # ==========================================
        # پروفایل کاربر
        # ==========================================
        "profile": {
            "national_code": profile.national_code,
            "birth_date": profile.birth_date.isoformat() if profile.birth_date else None,
            "gender": profile.gender,
            "gender_display": profile.get_gender_display() if profile.gender else None,
            "address": profile.address,
            "post_code": profile.post_code,

            "province": {
                "id": profile.province_id,
                "name": _location_name(profile.province),
            } if profile.province_id else None,

            "city": {
                "id": profile.city_id,
                "name": _location_name(profile.city),
            } if profile.city_id else None,

            "job_title": profile.job_title,
            "company_name": profile.company_name,
        } if profile else None,

        # ==========================================
        # مدارک شغلی
        # ==========================================
        "job_certificates": [{
            "id": cert.id,
            "type": cert.type,
            "type_display": cert.get_type_display(),
            "file": get_file_url(cert.file),
            "file_size": cert.file_size,
            "file_type": cert.file_type,
            "is_verified": cert.is_verified,
            "verified_at": cert.verified_at.isoformat() if cert.verified_at else None,
            "can_edit": not cert.is_verified,
        } for cert in job_certs],

        # ==========================================
        # خلاصه علاقه‌مندی‌ها
        # ==========================================
       "favorite_answers_count": favorite_answers_count,
        "has_answered_all_favorites": has_answered_all_favorites,
    }

    return base_data


#############################################################################################
# سریالایزر دستگاه
#############################################################################################
def device_serialize(device):
    return {
        "id": device.id,
        "device_name": device.device_name,
        "device_type": device.device_type,
        "ip_address": device.ip_address,
        "user_agent": device.user_agent,
        "is_active": device.is_active,
    }


#############################################################################################
# خروج
#############################################################################################
@router.post("/logout/")
async def logout(res: LogoutSchema):
    refresh_token = res.refresh_token
    if not refresh_token or refresh_token == "undefined":
        return error_response("توکن بازخوانی نامعتبر است")

    await async_logout(refresh_token)
    return success_response("با موفقیت خارج شدید")


#############################################################################################
# دستگاه‌ها
#############################################################################################
@router.get("/devices/")
async def list_devices(user=Depends(get_current_user)):
    devices = await async_get_devices(user)
    return success_response("همه‌ی دستگاه‌های کاربر", devices)


@router.post("/logout_device/{device_id}/")
async def logout_device(device_id: int, user=Depends(get_current_user)):
    try:
        await async_logout_device(id=device_id, user=user)
        return {"message": "دستگاه با موفقیت خارج شد"}
    except UserDevice.DoesNotExist:
        raise HTTPException(status_code=404, detail="دستگاه یافت نشد")


@router.post("/logout_all/")
async def logout_all_devices(user=Depends(get_current_user)):
    await async_logout_all_devices(user)
    return {"message": "همه‌ی دستگاه‌ها با موفقیت خارج شدند"}


#############################################################################################
# پروفایل
#############################################################################################
@router.get("/profile/")
async def profile(current_user: User = Depends(get_current_user)):
    return success_response("اطلاعات کاربر", await database_sync_to_async(user_serialize)(current_user))


@router.post("/profile/update/")
async def profileUpdate(form: dict = Depends(DependencyDataRequest), user: User = Depends(get_current_user)):
    firstname = form.get("firstname")
    lastname = form.get("lastname")
    gender = form.get("gender")
    mobile = form.get("mobile")
    birth_day = form.get("birth_day")
    national_code = form.get("national_code")
    address = form.get("address")
    post_code = form.get("post_code")
    job_title = form.get("job_title")
    company_name = form.get("company_name")
    province_id = form.get("province_id")
    city_id = form.get("city_id")
    nature = form.get("nature")
    referral_code = form.get("referral_code")

    # ------- فیلدهای اجباری -------
    if not firstname:
        return error_response("نام الزامی است", status_code=400)
    if not lastname:
        return error_response("نام خانوادگی الزامی است", status_code=400)

    # ------- ولیدیشن کد ملی (فرمت + تکراری) -------
    if national_code:  # اگر خالی یا None باشد از این بلوک رد می‌شود
        national_code = str(national_code).strip()

        if not is_valid_iranian_national_code(national_code):
            return error_response("کد ملی نامعتبر است", status_code=400)

        # آیا این کد ملی برای پروفایل دیگری ثبت شده؟
        is_taken = await database_sync_to_async(
            lambda: UserProfile.objects
                .filter(national_code=national_code)
                .exclude(user=user)
                .exists()
        )()
        if is_taken:
            return error_response("کد ملی وارد شده قبلاً برای کاربر دیگری ثبت شده است", status_code=400)
     
    # ------- ولیدیشن موبایل (چون روی User هم unique است) -------
    if mobile:
        mobile = str(mobile).strip()
        if mobile != user.mobile:
            is_mobile_taken = await database_sync_to_async(
                lambda: User.objects.filter(mobile=mobile).exclude(pk=user.pk).exists()
            )()
            if is_mobile_taken:
                return error_response("شماره موبایل وارد شده قبلاً ثبت شده است", status_code=400)
            
     # ------- ذخیره -------          
    await async_profileUpdate(
        user, firstname, lastname, gender, mobile, birth_day,
        national_code, address, post_code, job_title, company_name,
        province_id, city_id, nature
    )

    if referral_code:
        try:
            from applications.user.services import process_referral_code
            await database_sync_to_async(process_referral_code)(user, referral_code)
        except Exception as e:
            print("[referral] failed:", e)

    return success_response("به‌روزرسانی شد", await database_sync_to_async(user_serialize)(user))


@sync_to_async
def async_profileUpdate(
    user, firstname, lastname, gender, mobile, birth_day,
    national_code, address, post_code, job_title, company_name,
    province_id, city_id, nature
):
    from datetime import datetime

    user.first_name = firstname
    user.last_name = lastname
    if mobile: user.mobile = mobile
    if nature: user.nature = nature
    user.save()

    profile = user.get_profile_info
    if not profile:
        from applications.user.models import UserProfile
        profile = UserProfile.objects.create(user=user)

    if gender is not None: profile.gender = gender

    if birth_day:
        try:
            profile.birth_date = datetime.strptime(birth_day, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            profile.birth_date = None
    else:
        profile.birth_date = None

    profile.national_code  = national_code or None
    profile.address        = address if address is not None else profile.address
    profile.post_code      = post_code if post_code is not None else profile.post_code
    profile.job_title      = job_title if job_title is not None else profile.job_title
    profile.company_name   = company_name if company_name is not None else profile.company_name

    if province_id is not None:
        profile.province_id = province_id or None
    if city_id is not None:
        profile.city_id = city_id or None
        
    profile.save()

    profile.refresh_from_db(fields=["birth_date"])


#############################################################################################
# آپلود آواتار
#############################################################################################
@router.post("/profile/uploadavatar/")
async def uploadAvatar(form: dict = Depends(DependencyDataRequest), user: User = Depends(get_current_user)):
    avatar = form.get("avatar")

    if avatar is None:
        return error_response("آواتار الزامی است", status_code=400)

    await async_uploadAvatar(user, avatar)
    return success_response("به‌روزرسانی شد", await database_sync_to_async(user_serialize)(user))


@sync_to_async
def async_uploadAvatar(user, avatar):
    user.avatar.name = handle_save_file(avatar)
    user.save(update_fields=["avatar"])


#############################################################################################
# رمز عبور
#############################################################################################
@router.post("/changepass/")
async def changePassword(
        newPassword: str = Form(...),
        confirmPassword: str = Form(...),
        currentPassword: str = Form(...),
        user: User = Depends(get_current_user)):

    if not currentPassword:
        return error_response("رمز عبور فعلی الزامی است", status_code=400)

    if not newPassword:
        return error_response("رمز عبور جدید الزامی است", status_code=400)

    if not confirmPassword:
        return error_response("تکرار رمز عبور الزامی است", status_code=400)

    if user.check_password(currentPassword) is False:
        return error_response("رمز عبور فعلی اشتباه است", status_code=400)

    if confirmPassword != newPassword:
        return error_response("تکرار رمز عبور مطابقت ندارد", status_code=400)

    await async_changePassword(user, newPassword)
    return success_response("رمز عبور تغییر کرد")


@sync_to_async
def async_changePassword(user, newPassword):
    user.password = make_password(str(newPassword))
    user.password_changed_at = timezone.now()
    user.save(update_fields=["password", "password_changed_at"])


#############################################################################################
# تنظیم رمز اولیه
#############################################################################################
@router.post("/profile/set-password/")
async def setInitialPassword(
    form: dict = Depends(DependencyDataRequest),
    user: User = Depends(get_current_user)
):
    password = form.get("password")
    if not password or len(password) < 6:
        return error_response("رمز عبور باید حداقل 6 کاراکتر باشد", status_code=400)

    await async_setPassword(user, password)
    return success_response("رمز عبور تنظیم شد")


@sync_to_async
def async_setPassword(user, password):
    user.password = make_password(str(password))
    user.password_changed_at = timezone.now()
    user.save(update_fields=["password", "password_changed_at"])


#############################################################################################
# بررسی توکن
#############################################################################################
@router.post("/checktoken/")
async def checkToken(user: User = Depends(get_current_user)):
    if user is None:
        return error_response("توکن منقضی شده است", status_code=400)
    return success_response("کاربر معتبر است")


#############################################################################################
# توابع کمکی پایگاه داده
#############################################################################################
@database_sync_to_async
def async_get_devices(user):
    return UserDevice.objects.filter(user=user, is_active=True)


@database_sync_to_async
def async_logout_device(id, user):
    device = UserDevice.objects.get(id=id, user=user)
    device.is_active = False
    device.save(update_fields=["is_active"])


@database_sync_to_async
def async_logout_all_devices(user):
    devices = UserDevice.objects.filter(user=user, is_active=True)
    devices.update(is_active=False)


@database_sync_to_async
def async_logout(refresh_token):
    token_entry = RefreshToken.objects.filter(token=refresh_token).first()
    if token_entry:
        token_entry.delete()