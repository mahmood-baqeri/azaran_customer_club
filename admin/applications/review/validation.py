import json

from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse, JsonResponse
from django_dump_die.middleware import dd

from applications.core.validators import is_valid_mobile, validate_iranian_national_code
from applications.user.models import User


def adminValidation(request, _id=None):
    section = request.POST.get('section')
    mobile = request.POST.get('mobile')
    nationalCode = request.POST.get('nationalCode')
    personCode = request.POST.get('personCode')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')

    formValid = True

    if first_name is None or first_name == '':
        messages.error(request, 'نام الزامیست')
        formValid = None

    if section is None or section == '' or section == 'None':
        messages.error(request, 'بخش الزامیست')
        formValid = None

    if last_name is None or last_name == '':
        messages.error(request, 'نام خانوادگی الزامیست')
        formValid = None

    if mobile is None or mobile == '':
        messages.error(request, 'شماره موبایل الزامیست')
        formValid = None

    if is_valid_mobile(mobile) is None:
        messages.error(request, 'شماره موبایل معتبر نیست')
        formValid = None

    uMobile = User.objects.filter(mobile=mobile).first()
    if uMobile:
        if uMobile.id != _id:
            messages.error(request, 'شماره موبایل قبلا استفاده شده است')

    if nationalCode is None or nationalCode == '':
        messages.error(request, 'کد ملی الزامیست')
        formValid = None

    # elif isValidNationalCode(nationalCode) is False:
    #     messages.error(request, 'کدملی معتبر نیست')
    #     formValid = None

    uNationalCode = User.objects.filter(nationalCode=nationalCode).first()
    if uNationalCode and _id is None and uNationalCode.id != _id:
        messages.error(request, 'کد ملی قبلا استفاده شده است')
        formValid = None

    if personCode is None or personCode == '':
        messages.error(request, 'کد پرسنلی الزامیست')
        formValid = None

    psCode = User.objects.filter(personCode=personCode).first()
    if psCode:
        if psCode.id != _id:
            messages.error(request, 'کد پرسنلی قبلا استفاده شده است')

    return formValid


def loginWithPassValidation(request):
    password = request.POST.get('password')
    mobile = request.POST.get('mobile')

    formValid = True

    if password is None or password == '':
        messages.add_message(request, messages.ERROR, json.dumps({'text': 'رمزعبور الزامیست'}))
        formValid = None

    if mobile is None or mobile == '':
        messages.add_message(request, messages.ERROR, json.dumps({'text': 'شماره موبایل الزامیست'}))
        formValid = None

    elif is_valid_mobile(mobile) is None:
        messages.add_message(request, messages.ERROR, json.dumps({'text': 'شماره موبایل معتبر نیست'}))
        formValid = None

    return formValid


def loginWithMobileValidation(request):
    mobile = request.POST.get('mobile')

    formValid = True

    if mobile is None or mobile == '':
        messages.add_message(request, messages.ERROR, json.dumps({'text': 'شماره موبایل الزامیست'}))
        formValid = None

    elif is_valid_mobile(mobile) is None:
        messages.add_message(request, messages.ERROR, json.dumps({'text': 'شماره موبایل معتبر نیست'}))
        formValid = None

    return formValid


def changePassValidation(request):
    user = request.user
    oldPassword = request.POST.get('oldPassword')
    newPassword = request.POST.get('newPassword')
    rePassword = request.POST.get('rePassword')

    formValid = True

    if oldPassword is None or oldPassword == '':
        messages.error(request, 'رمزعبور فعلی الزامیست')
        formValid = None

    if newPassword is None or newPassword == '':
        messages.error(request, 'رمزعبور جدید الزامیست')
        formValid = None

    if rePassword is None or rePassword == '':
        messages.error(request, 'تکرار رمزعبور الزامیست')
        formValid = None

    if formValid and request.user.check_password(oldPassword) is False:
        messages.error(request, 'رمزعبور فعلی اشتباه است')
        formValid = None

    if formValid and rePassword != newPassword:
        messages.error(request, 'تکرار رمزعبور مطابقت ندارد')
        formValid = None

    return formValid




def userValidation(request, _id):
    mobile = request.POST.get('mobile')
    formValid = True

    if mobile is None or mobile == '':
        messages.add_message(request, messages.ERROR, json.dumps({'text': 'شماره موبایل الزامیست'}))
        formValid = None

    if is_valid_mobile(mobile) is None:
        messages.add_message(request, messages.ERROR, json.dumps({'text': 'شماره موبایل معتبر نیست'}))
        formValid = None

    uMobile = User.objects.filter(mobile=mobile).first()
    if uMobile:
        if uMobile.id != _id:
            messages.error(request, 'شماره موبایل قبلا استفاده شده است')

    return formValid
