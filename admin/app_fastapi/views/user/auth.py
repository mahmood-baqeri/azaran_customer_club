# admin/app_fastapi/views/user_auth.py

import uuid
from channels.db import database_sync_to_async
from django.contrib.auth.hashers import make_password
from fastapi import APIRouter, HTTPException, Depends, Request, Form
from django.db.models import Q
import jwt
from fastapi.responses import HTMLResponse
from django.utils import timezone
from datetime import timedelta

from applications.core.sms import sms_verification_code
from app_fastapi.conf.cache import get_cache
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.response import error_response, success_response
from app_fastapi.schemas.user import CheckEmailSchema, CheckUsernameSchema
from app_fastapi.views.user.helper import create_access_token, create_refresh_token, verify_reset_token
from app_fastapi.views.user.user import device_serialize, user_serialize
from applications.user.models import UserDevice, RefreshToken, VerificationCode, User
from app_fastapi.conf.config import SECRET_KEY, ALGORITHM, FORGET_RATE_LIMIT_SECONDS, FORGET_RATE_LIMIT_KEY, \
    VERIFY_MAX_ATTEMPTS, FORGET_RATE_LIMIT_KEY_PHONE
from applications.core.utils import send_otp_code_async, send_verification_email_async
from user_agents import parse
from django.utils.translation import gettext_lazy as trans
from applications.core.validators import check_email
from fastapi.templating import Jinja2Templates

# ✅ ایمپورت سرویس‌های دعوت و امتیاز
from applications.user.services import process_referral_code, reward_referral_after_verification

templates = Jinja2Templates(directory="templates")
router = APIRouter()


# ---------------------
# Login
# ---------------------
@router.post("/login/")
async def login(form: dict = Depends(DependencyDataRequest)):
    mobile = form.get("mobile")

    if not mobile:
        return error_response("Mobile is required", 400)

    existUser = True
    user = await async_user_by_mobile(mobile)

    # اگر کاربر نبود بساز
    if not user:
        user = await async_register(firstname=None, lastname=None, mobile=mobile)
        existUser = False

    # ✅ استفاده از create_code در مدل
    code = await async_create_verification(identifier=mobile, purpose=VerificationCode.Purpose.LOGIN)

    # sms_verification_code(mobile, code)
    await send_otp_code_async(mobile, code, test_mode=True)

    return success_response("OTP sent successfully", {"existUser" : existUser})


# ---------------------
# Register (با کد دعوت)
# ---------------------
@router.post("/register/")
async def register(form: dict = Depends(DependencyDataRequest)):
    mobile = form.get("mobile")
    firstname = form.get("firstname")
    lastname = form.get("lastname")
    referral_code = form.get("referral_code")  # ✅ دریافت کد دعوت از ورودی

    if not mobile:
        return error_response("Mobile required", 400)

    if await async_user_by_mobile(mobile):
        return error_response("Mobile already used", 400)

    user = await async_register(
        firstname=firstname,
        lastname=lastname,
        mobile=mobile
    )

    # ✅ پردازش کد دعوت (در صورت وجود)
    if referral_code:
        success, message = await database_sync_to_async(process_referral_code)(user, referral_code)
        # اگر خطا داشت، می‌توانید در ریسپانس لحاظ کنید (فعلاً نادیده گرفته می‌شود تا ثبت‌نام متوقف نشود)

    code = await async_create_verification(identifier=mobile, purpose=VerificationCode.Purpose.REGISTER)

    # sms_verification_code(mobile, code)
    await send_otp_code_async(mobile, code, test_mode=True)

    return success_response("Verification code sent")


@database_sync_to_async
def async_register(firstname, lastname, mobile=None, email=None, password=None):
    username = str(uuid.uuid4())
    user = User.objects.create(
        first_name=firstname or "",
        last_name=lastname or "",
        email=email or f"{mobile}@temp.local",
        username=username,
        is_superuser=False,
        is_active=False,
        is_staff=True,
        password=make_password(str(password) if password else username),
        mobile=mobile or None,
        password_changed_at=timezone.now(),
    )
    return user


# ---------------------
# Forget / Send Code
# ---------------------
@router.post("/forgot/")
async def forgot(request: Request, form: dict = Depends(DependencyDataRequest), cache=Depends(get_cache)):
    email = form.get("email", "").strip()
    if not email:
        return error_response(str(trans("Email is required")), status_code=400)

    user = await async_user_by_email(email)
    if not user or not user.is_superuser or not user.is_staff:
        return error_response(str(trans("You do not have the required access")), status_code=400)

    key = FORGET_RATE_LIMIT_KEY.format(email=email)
    if await cache.get(key):
        return error_response(str(trans("Please wait before requesting another code")), status_code=400)

    code = await async_forget_handle_verify(identifier=email, purpose=VerificationCode.Purpose.FORGOT, code_length=4)

    await cache.set(key, True, expire=FORGET_RATE_LIMIT_SECONDS)

    try:
        await send_verification_email_async(email, code, test_mode=True)
    except Exception as e:
        print("Email Error:", e)
        return error_response(str(trans("Failed to send email. Please contact support")), status_code=400)

    return success_response(str(trans("Verification code sent to your email")), {})


# ---------------------
# Resend Code
# ---------------------
@router.post("/resend/")
async def resend(form: dict = Depends(DependencyDataRequest), cache=Depends(get_cache)):
    identifier = form.get("identifier")

    resendWithMobile = True
    resendWithEmail = True
    error_message = ""

    try:
        key = FORGET_RATE_LIMIT_KEY_PHONE.format(mobile=identifier)
        if await cache.get(key):
            return error_response(str(trans("Please wait before requesting another code")), status_code=400)
        code = await async_forget_handle_verify(identifier=identifier, purpose=VerificationCode.Purpose.RESEND,
                                                code_length=4)
        await cache.set(key, True, expire=FORGET_RATE_LIMIT_SECONDS)
        sms_verification_code(identifier, code)
        await send_otp_code_async(identifier, code, test_mode=True)
    except Exception as e:
        resendWithMobile = False
        error_message = str(e)

    try:
        key = FORGET_RATE_LIMIT_KEY.format(email=identifier)
        if await cache.get(key):
            return error_response(str(trans("Please wait before requesting another code")), status_code=400)
        code = await async_forget_handle_verify(identifier=identifier, purpose=VerificationCode.Purpose.RESEND,
                                                code_length=4)
        await cache.set(key, True, expire=FORGET_RATE_LIMIT_SECONDS)
        await send_verification_email_async(identifier, code)
    except Exception:
        resendWithEmail = False

    if not resendWithMobile and not resendWithEmail:
        print("Send error:", error_message)
        return error_response(str(trans("Failed to send verification code. Please contact support")), status_code=400)

    return success_response(str(trans("Verification code resent")), {})


# ---------------------
# Verify Code (با پشتیبانی از LOGIN و REGISTER)
# ---------------------
@router.post("/verify/")
async def verify(request: Request, form: dict = Depends(DependencyDataRequest)):
    mobile = form.get("mobile")
    code = form.get("code", "").strip()
    purpose = form.get("purpose", VerificationCode.Purpose.LOGIN)  # ✅ دریافت هدف از ورودی

    if not code:
        return error_response(str(trans("Code is required")), status_code=400)

    if not mobile:
        return error_response(str(trans("Mobile number is required")), status_code=400)

    # ✅ جستجو با purpose مشخص
    verification = await async_get_verification(identifier=mobile, purpose=purpose)
    if not verification:
        return error_response(str(trans("Invalid code or no request found")), status_code=400)

    if verification.attempts >= VERIFY_MAX_ATTEMPTS:
        await async_verify_delete(verification)
        return error_response(str(trans("Too many invalid attempts. Please request a new code")), status_code=400)

    if not verification.is_valid:
        await async_verify_delete(verification)
        return error_response(str(trans("Code expired")), status_code=400)

    is_valid = await async_verify_code(verification, code)

    if not is_valid:
        remaining = await async_save_verify_attempt(verification)
        return error_response(str(trans("Invalid code. %(remaining)s attempts left.") % {"remaining": remaining}),
                              status_code=400)

    user = await async_user(mobile)
    if not user:
        return error_response(str(trans("User not found")), status_code=400)

    device = await async_save_device(request, user)

    await async_active_user(user)
    await async_update_password_changed_at(user)

    # ✅ اعطای پاداش دعوت بعد از تایید نهایی
    await database_sync_to_async(reward_referral_after_verification)(user)

    access_token = await create_access_token(data={"sub": user.username})
    refresh_token = await create_refresh_token(user)

    res = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "device": device_serialize(device),
        "user": await database_sync_to_async(user_serialize)(user)
    }
    response = success_response(str(trans('Welcome')), res)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=2 * 24 * 60 * 60,
        path="/",
    )

    return response


# ---------------------
# Logout (✅ اضافه شد)
# ---------------------
@router.post("/logout/")
async def logout(request: Request):
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        try:
            # دیکد کردن توکن برای پیدا کردن کاربر
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            
            if username:
                user = await async_user_by_username(username)
                if user:
                    # پیدا کردن توکن در دیتابیس و باطل کردن آن
                    token_entry = await async_get_refresh_token(user, refresh_token)
                    if token_entry:
                        await async_revoke_token(token_entry)
        except (jwt.ExpiredSignatureError, jwt.PyJWTError):
            # اگر توکن منقضی یا نامعتبر بود، نادیده بگیر
            pass

    # پاک کردن کوکی از مرورگر
    response = success_response(str(trans("Successfully logged out")))
    response.delete_cookie(
        key="refresh_token",
        path="/",
        secure=True,
        httponly=True,
        samesite="Lax"
    )

    return response


# ---------------------
# Check email / username
# ---------------------
@router.post("/check-email/")
async def checkEmail(req: CheckEmailSchema):
    email = req.email
    if not check_email(email):
        return error_response(str(trans("Email Not Valid")), status_code=400)
    user = await async_user_by_email(email)
    if user:
        return error_response(str(trans("Email Already Used")), status_code=400)
    else:
        return success_response(str(trans("Email")) + ' ' + str(trans("Is Free")))


@router.post("/check-username/")
async def checkUsername(req: CheckUsernameSchema):
    username = req.username
    if len(username) < 2:
        return error_response(str(trans("Username Not Valid")), status_code=400)
    user = await async_user_by_username(username)
    if user:
        return error_response(str(trans("Username Already Used")), status_code=400)
    else:
        return success_response(str(trans("Username")) + ' ' + str(trans("Is Free")))


# ---------------------
# Refresh
# ---------------------
@router.post("/token/refresh/")
async def refresh_token(request: Request):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        return error_response(str(trans("Token Not Found")), status_code=400)

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return error_response(str(trans("Token Not Valid")), status_code=400)
    except jwt.ExpiredSignatureError:
        return error_response(str(trans("Token Expired")), status_code=400)
    except jwt.PyJWTError:
        return error_response(str(trans("Token Not Valid")), status_code=400)

    username = payload.get("sub")
    if not username:
        return error_response(str(trans("Token Not Valid")), status_code=400)

    user = await async_user_by_username(username)
    if not user:
        return error_response(str(trans("Account Not Found")), status_code=400)

    token_entry = await async_get_refresh_token(user, refresh_token)
    if not token_entry:
        return error_response(str(trans("Token Not Found")), status_code=400)

    if token_entry.is_expired:
        await async_verify_delete(token_entry)
        return error_response(str(trans("Token Expired")), status_code=400)

    # ✅ اصلاح: create_access_token یک تابع async است، پس باید await شود
    new_access_token = await create_access_token(data={"sub": user.username})
    return success_response("", new_access_token)


# ---------------------
# Reset Token & Password
# ---------------------
@router.post("/reset-token/", response_class=HTMLResponse)
async def reset_form(request: Request, token: str):
    email = verify_reset_token(token)
    if not email:
        return HTMLResponse(f"<h3> {str(trans('The token is invalid or expired'))} </h3>")
    return templates.TemplateResponse("reset_password_form.html", {"request": request, "token": token})


@router.post("/reset-password")
async def reset_password(token: str = Form(...), new_password: str = Form(...)):
    email = verify_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="توکن نامعتبر است")

    hashed_password = make_password(new_password)
    user = await async_user_by_email(email)
    if not user:
        return error_response(str(trans("User Not Found")), status_code=400)

    await async_update_user_password(user, hashed_password)
    return success_response(str(trans("Password")) + ' ' + str(trans("Successfully Changed")))


@database_sync_to_async
def async_update_user_password(user, hashed_password):
    user.password = hashed_password
    user.password_changed_at = timezone.now()
    user.save()


# ---------------------
# Helpers
# ---------------------
@database_sync_to_async
def async_user_by_username(username):
    return User.objects.filter(username=username).first()


@database_sync_to_async
def async_user_by_email(email):
    return User.objects.filter(email=email).first()


@database_sync_to_async
def async_user_by_mobile(mobile):
    return User.objects.filter(mobile=mobile).first()


@database_sync_to_async
def async_user_by_id(id):
    return User.objects.filter(id=id).first()


@database_sync_to_async
def async_user(identifier):
    return User.objects.filter(Q(email=identifier) | Q(username=identifier) | Q(mobile=identifier)).first()


@database_sync_to_async
def async_forget_handle_verify(identifier, purpose, code_length):
    verification, code = VerificationCode.create_code(identifier=identifier, purpose=purpose, ttl_seconds=600,
                                                      code_length=code_length)
    return code


@database_sync_to_async
def async_create_verification(identifier, purpose):
    verification, code = VerificationCode.create_code(
        identifier=identifier,
        purpose=purpose,
        ttl_seconds=600,
        code_length=4
    )
    return code


@database_sync_to_async
def async_verify_code(verification, code):
    return verification.verify(code)


@database_sync_to_async
def async_get_verification(identifier, purpose):
    return VerificationCode.objects.filter(
        identifier=identifier,
        purpose=purpose
    ).order_by("-created_at").first()


@database_sync_to_async
def async_get_refresh_token(user, token):
    return RefreshToken.objects.filter(
        user=user,
        token=token
    ).first()


@database_sync_to_async
def async_verify_delete(verify):
    verify.delete()


@database_sync_to_async
def async_save_verify_attempt(verify):
    verify.attempts += 1
    verify.save(update_fields=["attempts"])
    return VERIFY_MAX_ATTEMPTS - verify.attempts


@database_sync_to_async
def async_save_verify_user(verify_user):
    verify_user.save()


@database_sync_to_async
def async_active_user(user):
    user.is_active = True
    user.save()


@database_sync_to_async
def async_update_password_changed_at(user):
    user.password_changed_at = timezone.now()
    user.save(update_fields=['password_changed_at'])


# ✅ توابع کمکی برای لاگ‌اوت
@database_sync_to_async
def async_revoke_token(token_entry):
    token_entry.revoke()


# ذخیره device
@database_sync_to_async
def async_save_device(request, user):
    user_agent_string = request.headers.get('User-Agent')
    user_agent = parse(user_agent_string)
    device_name = user_agent.device.family or "Unknown Device"
    device_type = user_agent.device.model or "Unknown Model"
    ip_address = request.client.host

    device = UserDevice.objects.create(
        user=user,
        device_name=device_name,
        device_type=device_type,
        ip_address=ip_address,
        user_agent=user_agent_string
    )
    return device


@database_sync_to_async
def async_userScoreRemain(user):
    return user.userScoreKasb() - user.userScoreKarj()