# admin/app_fastapi/views/user/user.py
import re

import jwt
import logging
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
from app_fastapi.views.user.helper import get_current_user

# ── Import Models ─────────────────────────────────
from applications.user.models import User, UserInvitation
from applications.project.models import Project
from applications.factor.models import Factor
from applications.gift.models import GiftOrder
from applications.promotion.models import PromotionOrder
from applications.support.models import Support
from applications.gallery.models import Gallery
from applications.visit.models import RequestVisit
from applications.faq.models import FAQ
from applications.review.models import ReviewQuestion

router = APIRouter()

logger = logging.getLogger(__name__)


def _location_name(obj):
    if not obj:
        return None
    return getattr(obj, "name", None) or getattr(obj, "title", None) or str(obj)


#############################################################################################
# سریالایزر کاربر
#############################################################################################
def user_serialize(user, include_full_information=False):
    score   = user.get_score

    # ------- داده‌های پایه (همیشه) -------
    base_data = {
        "uuid": str(user.uuid),
        "name": user.full_name,
        "firstname": user.first_name,
        "lastname": user.last_name,
        "short_name": user.short_name,
        "avatar": get_file_url(user.avatar),
        # "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        # "last_active_at": user.last_active_at.isoformat() if user.last_active_at else None,
        "nature": user.nature,
        "nature_display": user.get_nature_display(),

        "level": user.level_info,

        "score": {
            "current_balance": score.current_balance,
            "total_earned": score.total_earned,
            "total_spent": score.total_spent,
        } if score else None,

      
    }

    # ------- فقط در /me/ -------
    if include_full_information:
        inviter = user.get_inviter
        profile = user.get_profile_info
    
        # stats مورد علاقه‌مندی
        try:
            from applications.user.models import FavoriteQuestion
            favorite_answers_count = user.user_favorite_answers.count()
            total_active_questions = FavoriteQuestion.objects.filter(is_active=True).count()
            has_answered_all_favorites = (
                True if total_active_questions == 0
                else user.user_favorite_answers.filter(question__is_active=True).count()
                     >= total_active_questions
            )
        except Exception:
            favorite_answers_count = 0
            has_answered_all_favorites = False

        base_data.update({
            "profile": _profile_serialize(profile),
            "mobile": user.mobile,
            "is_mobile_verified": user.is_mobile_verified,
            "referral_code": user.referral_code,
            "invited_by": {
                "uuid": str(inviter.uuid),
                "name": inviter.full_name,
                "mobile": inviter.mobile,
                "referral_code": inviter.referral_code,
            } if inviter else None,
            "favorite_answers_count": favorite_answers_count,
            "has_answered_all_favorites": has_answered_all_favorites,
            "job_certificates": _job_certificates_serialize(user),
        })

    return base_data


def _profile_serialize(profile):
    if not profile:
        return None
    return {
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
    }


def _job_certificates_serialize(user):
    if not hasattr(user, "user_job_certificates"):
        return []
    return [{
        "id": cert.id,
        "type": cert.type,
        "type_display": cert.get_type_display(),
        "file": get_file_url(cert.file),
        "file_size": cert.file_size,
        "file_type": cert.file_type,
        "is_verified": cert.is_verified,
        "verified_at": cert.verified_at.isoformat() if cert.verified_at else None,
        "can_edit": not cert.is_verified,
    } for cert in user.user_job_certificates.all()]



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
#############################################################################################
#############################################################################################
#############################################################################################
#############################################################################################
#############################################################################################
#############################################################################################
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
            if not re.fullmatch(r"09\d{9}", mobile):
                return error_response("شماره موبایل نامعتبر است", status_code=400)
        
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

    if birth_day is not None:
        if birth_day == "":
            profile.birth_date = None
        else:
            try:
                profile.birth_date = datetime.strptime(birth_day, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                return error_response("تاریخ تولد نامعتبر است", status_code=400)

    # کد ملی هم همین رفتار
    if national_code is not None:
        profile.national_code = national_code or None
        
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
# تمام اطلاعات کاربر
#############################################################################################
@router.get("/full_information/")
async def get_my_full_profile(user: User = Depends(get_current_user)):
    """
    دریافت اطلاعات جامع کاربر در یک درخواست واحد (بهینه با Prefetch).
    """
    try:
        data = await _get_full_information(user.id)
        return success_response("پروفایل کامل کاربر", data)
    except Exception:
        logger.exception("get_my_full_profile failed")
        return error_response("خطا در دریافت اطلاعات پروفایل")


@sync_to_async
def _get_full_information(user_id: int):
    # ۱. واکشی هوشمندانه کاربر با تمام روابط (جلوگیری از N+1)
    user = (
        User.objects
        .select_related(
            "relation_profile",              # reverse OneToOne → UserProfile
            "relation_profile__province",    # FK درون UserProfile
            "relation_profile__city",        # FK درون UserProfile
            "relation_score",                # reverse OneToOne → Score
        )
        .prefetch_related(
            "user_job_certificates",
            "user_favorite_answers",
            "user_projects",
            "user_factors",
            "user_gift_orders__gift",        # gift داخل gift_order
            "user_promotion_orders",
            "user_supports",
            "user_gallery_posts",
            "user_visit_requests__visit",
            "user_faqs",
            "review_answers",
            "user_score_logs",
            "relation_sent_invitations",     # ← ✅ کاما اینجا الزامی
        )
        .get(id=user_id)
    )

    # ۲. سریالایزر پایه (اطلاعات پروفایل، مدارک و ...)
    base_data = user_serialize(user, include_full_information=True)

    # ─────────────────────────────────────────────
    # ۳. محاسبه آمار (از دیتای پیش‌واکشی‌شده در حافظه - بدون کوئری اضافی)
    # ─────────────────────────────────────────────

    projects = list(user.user_projects.all())
    factors = list(user.user_factors.all())
    gift_orders = list(user.user_gift_orders.all())
    promo_orders = list(user.user_promotion_orders.all())
    supports = list(user.user_supports.all())
    gallery = list(user.user_gallery_posts.all())
    visits = list(user.user_visit_requests.all())
    faqs = list(user.user_faqs.all())
    reviews = list(user.review_answers.all())
    invitations = list(user.relation_sent_invitations.all())

    # شمارش در حافظه (O(N) - بسیار سریع)
    projects_stats = {
        "total": len(projects),
        "pending": sum(1 for p in projects if p.status == Project.Status.PENDING),
        "approved": sum(1 for p in projects if p.status == Project.Status.APPROVED),
        "rejected": sum(1 for p in projects if p.status == Project.Status.REJECTED),
    }

    factors_stats = {
        "total": len(factors),
        "pending": sum(1 for f in factors if f.status == Factor.Status.PENDING),
        "approved": sum(1 for f in factors if f.status == Factor.Status.APPROVED),
        "rejected": sum(1 for f in factors if f.status == Factor.Status.REJECTED),
    }

    gift_orders_stats = {
        "total": len(gift_orders),
        "pending": sum(1 for g in gift_orders if g.status == GiftOrder.Status.PENDING),
        "shipped": sum(1 for g in gift_orders if g.status == GiftOrder.Status.SHIPPED),
        "delivered": sum(1 for g in gift_orders if g.status == GiftOrder.Status.DELIVERED),
    }

    promo_orders_stats = {
        "total": len(promo_orders),
        "pending": sum(1 for p in promo_orders if p.status == PromotionOrder.Status.PENDING),
        "delivered": sum(1 for p in promo_orders if p.status == PromotionOrder.Status.DELIVERED),
    }

    supports_stats = {
        "total": len(supports),
        "open": sum(1 for s in supports if s.status == Support.Status.OPEN),
        "in_progress": sum(1 for s in supports if s.status == Support.Status.IN_PROGRESS),
        "closed": sum(1 for s in supports if s.status == Support.Status.CLOSED),
    }

    gallery_stats = {
        "total": len(gallery),
        "approved": sum(1 for g in gallery if g.status == Gallery.Status.APPROVED),
        "pending": sum(1 for g in gallery if g.status == Gallery.Status.PENDING),
    }

    visits_stats = {
        "total": len(visits),
        "pending": sum(1 for v in visits if v.status == RequestVisit.Status.PENDING),
        "approved": sum(1 for v in visits if v.status == RequestVisit.Status.APPROVED),
    }

    # نظرسنجی
    # نکته: برای بررسی تعداد سوالات فعال، یک کوئری جدا می‌زنیم (چون برای هر کاربر واکشی نمی‌شود)
    total_active_reviews = ReviewQuestion.objects.filter(is_active=True).count()
    has_answered_all_reviews = (len(reviews) >= total_active_reviews) if total_active_reviews > 0 else True

    invitation_stats = {
        "total_sent": len(invitations),
        "successful": sum(1 for i in invitations if i.invited_user_id is not None),
        "rewarded": sum(1 for i in invitations if i.is_rewarded),
    }

    # ۴. ساخت خروجی نهایی آمار
    base_data["stats"] = {
        "projects": projects_stats,
        "factors": factors_stats,
        "gift_orders": gift_orders_stats,
        "promotion_orders": promo_orders_stats,
        "supports": supports_stats,
        "gallery": gallery_stats,
        "visits": visits_stats,
        "faqs_count": len(faqs),
        "reviews": {
            "answered_count": len(reviews),
            "total_active": total_active_reviews,
            "has_answered_all": has_answered_all_reviews,
        },
        "invitations": invitation_stats,
    }

    # ─────────────────────────────────────────────
    # ۵. آخرین فعالیت‌ها (با مرتب‌سازی روی دیتای حافظه)
    # ─────────────────────────────────────────────
    
    # مرتب‌سازی در حافظه (چون از قبل لود شده‌اند)
    recent_projects = sorted(projects, key=lambda x: x.created_at, reverse=True)[:3]
    recent_factors = sorted(factors, key=lambda x: x.created_at, reverse=True)[:3]
    recent_gifts = sorted(gift_orders, key=lambda x: x.created_at, reverse=True)[:3]
    
    # برای لاگ‌های امتیاز، چون ممکن است زیاد باشند، از خود دیتابیس با limit استفاده می‌کنیم
    # اما چون prefetch کردیم، مرتب‌سازی در حافظه هم سریع است
    recent_score_logs = sorted(
        list(user.user_score_logs.all()), 
        key=lambda x: x.created_at, 
        reverse=True
    )[:5]

    base_data["recent_projects"] = [
        {
            "id": p.id,
            "title": p.title,
            "type_display": p.get_type_display(),
            "status_display": p.get_status_display(),
            "created_at": p.created_at.isoformat() if p.created_at else None,
        } for p in recent_projects
    ]

    base_data["recent_factors"] = [
        {
            "id": f.id,
            "invoice_number": f.invoice_number,
            "status_display": f.get_status_display(),
            "amount": f.amount,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        } for f in recent_factors
    ]

    base_data["recent_gift_orders"] = [
        {
            "id": g.id,
            "gift_title": g.gift.title if g.gift else "هدیه",
            "status_display": g.get_status_display(),
            "created_at": g.created_at.isoformat() if g.created_at else None,
        } for g in recent_gifts
    ]

    base_data["recent_score_logs"] = [
        {
            "id": log.id,
            "code_display": log.get_transaction_code_display(),
            "direction": log.direction,
            "amount": log.amount,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        } for log in recent_score_logs
    ]

    return base_data


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