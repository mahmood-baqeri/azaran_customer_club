import json

from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django_dump_die.middleware import dd

from applications.core.decorators import authentication_required
from applications.user.models import Job, Payslip
from applications.user.validation import userValidation, changePassValidation


@authentication_required
def dashboard(request):
    data = {}
    data["pageTitle"] = 'داشبورد من'
    data["user"] = request.user
    return render(request, "user/dashboard.html", {"data": data})


@authentication_required
def profile(request):
    data = {}
    data["pageTitle"] = 'پروفایل من'
    data["user"] = request.user
    return render(request, "user/profile.html", {"data": data})


@authentication_required
def settings(request):
    data = {}
    data["pageTitle"] = "ویرایش پروفایل"
    data["user"] = request.user
    data["profile"] = front__userForm(request.user) # pyright: ignore[reportUndefinedVariable]
    data["profileStore"] = reverse('userFront:updateProfile')
    return render(request, "user/settings.html", {"data": data})


@authentication_required
def updateProfile(request):
    user = request.user
    if request.method == "POST":
        if userValidation(request, user.id):
            # user.first_name = request.POST.get('first_name')
            # user.last_name = request.POST.get('last_name')
            # user.mobile = request.POST.get('mobile')
            user.lat = request.POST.get('lat') if request.POST.get('lat') else user.lat
            user.long = request.POST.get('long') if request.POST.get('long') else user.long
            user.address = request.POST.get('address')
            user.birthDay = request.POST.get('birthDay') if validate(request.POST.get('birthDay')) else user.birthDay # pyright: ignore[reportUndefinedVariable]
            user.marriageDay = request.POST.get('marriageDay') if validate(request.POST.get('marriageDay')) else user.marriageDay # pyright: ignore[reportUndefinedVariable]
            user.phone = request.POST.get('phone') if request.POST.get('phone') else None
            user.photo = request.FILES.get('photo') if 'photo' in request.FILES else user.photo
            user.save()
            messages.success(request, 'پروفایل شما با موفقیت بروزرسانی شد')

    return redirect('userFront:settings')


@authentication_required
def changePass(request):
    user = request.user
    data = {}
    data["pageTitle"] = 'تغییر رمز عبور'
    data["storeUrl"] = reverse('userFront:changePass')
    data["items"] = [
        {'l': 'رمز عبور فعلی', 'n': 'oldPassword', 'v': '', 'id': 'thePassEl1', 'r': 1, 'c': 'col-12', 'b': 'password.html'},
        {'l': 'رمز عبور جدید', 'n': 'newPassword', 'v': '', 'id': 'thePassEl2', 'r': 1, 'c': 'col-12', 'b': 'password.html'},
        {'l': 'تکرار رمز عبور', 'n': 'rePassword', 'v': '', 'id': 'thePassEl3', 'r': 1, 'c': 'col-12', 'b': 'password.html'},
    ]

    if request.method == "POST":
        if changePassValidation(request):
            user = request.user
            user.password = make_password(str(request.POST.get('newPassword')))
            user.save()
            messages.success(request, 'رمز عبور با موفقیت تغییر یافت')
    return render(request, "user/form.html", {"data": data})


#######################################################################################
#######################################################################################
#######################################################################################
@authentication_required
def landing(request):
    data = {}
    data["pageTitle"] = 'کارتابل من'
    data["user"] = request.user
    return render(request, "user/cartable/index.html", {"data": data})
