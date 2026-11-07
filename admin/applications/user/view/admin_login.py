import json

from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, logout
from django.utils import timezone
from datetime import timedelta
from applications.core.utils import redirect_back
from applications.core.sms import sms_verification_code
from applications.user.models import User, VerificationCode
import random
from applications.core.validators import validate_mobile
from applications.core.decorators import is_admin_required
from applications.user.validation import loginWithMobileValidation, loginWithPassValidation
from django.contrib.auth.hashers import make_password
from applications.user.services import reward_referral_after_verification


from django.contrib.auth import authenticate, login, logout

def loginPass(request):
    if request.user.is_authenticated:
        return redirect_back(request, fallback_url="/")

    if request.method == "POST":
        if loginWithPassValidation(request):
            password = request.POST.get('password')
            mobile = request.POST.get('mobile')
            
            # ✅ استفاده از authenticate: خودش بک‌اند (axes یا model) را پیدا و ست می‌کند
            user = authenticate(request, username=mobile, password=password)
            
            if user is not None:
                # چک کردن دسترسی مدیر
                if user.is_superuser == 1 and user.is_active == 1:
                    login(request, user)
                    
                    # ✅ بررسی انقضای 7 روزه رمز عبور
                    if user.is_password_expired:
                        messages.add_message(request, messages.WARNING, json.dumps({'text': 'رمز عبور شما منقضی شده است. لطفاً رمز خود را تغییر دهید.'}))
                        return redirect('app_user:admin_login_with_mobile')

                    return redirect(reverse('dashboard:dashboard'))
                else:
                    messages.add_message(request, messages.ERROR, json.dumps({'text': 'شما دسترسی لازم را ندارید'}))
            else:
                messages.add_message(request, messages.ERROR, json.dumps({'text': 'حساب کاربری یافت نشد'}))
                
    return render(request, "pages/auth/loginWithPass.html")


def loginMobile(request):
    if request.user.is_authenticated:
        return redirect_back(request, fallback_url="/")

    if request.method == "POST":
        mobile = request.POST.get('mobile')

        if loginWithMobileValidation(request):
            user = User.objects.filter(mobile=mobile, is_superuser=1, is_active=1).first()
            if user:
                # ✅ استفاده از متد create_code مدل (کد قبلی رو پاک میکنه، کد جدید میسازه و هش میکنه)
                verification, code = VerificationCode.create_code(
                    identifier=mobile,
                    purpose=VerificationCode.Purpose.LOGIN,
                    ttl_seconds=300,  # 5 دقیقه
                    code_length=10
                )

                # ⚠️ تغییر رمز در اینجا کار خطرناکی است. اما برای حفظ رفتار فعلی، فقط password_changed_at را ریست می‌کنیم.
                user.password = make_password(str(code))
                user.password_changed_at = timezone.now()
                user.save()

                sms_verification_code(mobile, code)
                messages.add_message(request, messages.SUCCESS, json.dumps({'text': 'رمز جدید برای شما ارسال شد'}))
                return redirect('app_user:admin_verify')
            else:
                messages.add_message(request, messages.ERROR, json.dumps({'text': 'شما دسترسی لازم را ندارید'}))
                
    return render(request, "pages/auth/loginWithMobile.html")


def verifyAdmin(request):
    if request.user.is_authenticated:
        return redirect_back(request, fallback_url="/")

    if request.method == "POST":
        code = request.POST.get('code')

        if code is None:
            messages.add_message(request, messages.ERROR, json.dumps({'text': 'کد الزامیست'}))
        elif len(code) != 10:
            messages.add_message(request, messages.ERROR, json.dumps({'text': 'کد معتبر نیست'}))
        else:
            verify = VerificationCode.objects.filter(
                purpose=VerificationCode.Purpose.LOGIN,
                is_used=False
            ).order_by('-created_at').first()
            
            if verify and verify.is_valid and verify.verify(code):
                user = User.objects.filter(mobile=verify.identifier, is_superuser=1, is_active=1).first()
                if user is not None:
                    # ✅ مشخص کردن بک‌اند به صورت دستی هنگام لاگین با OTP
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    
                    user.password_changed_at = timezone.now()
                    user.save(update_fields=['password_changed_at'])

                    return redirect('dashboard:dashboard')
                else:
                    messages.add_message(request, messages.ERROR, json.dumps({'text': 'شما دسترسی لازم را ندارید'}))
                    return redirect('app_user:admin_login_with_mobile')
            else:
                messages.add_message(request, messages.ERROR, json.dumps({'text': 'کد وارد شده اشتباه یا منقضی شده است'}))
                return redirect('app_user:admin_verify')

    return render(request, "pages/auth/verify.html")


@is_admin_required
def logoutAdmin(request):
    logout(request)
    return redirect('app_user:admin_login_with_pass')