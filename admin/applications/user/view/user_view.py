import datetime
import json
from pathlib import Path

import pandas as pd
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, FileResponse
from django.conf import settings
from django_dump_die.middleware import dd
from persiantools.jdatetime import JalaliDate

from django.db.models import Q
from django.core.paginator import Paginator

from applications.core.fileManager import uploadExcel
from applications.core.utils import gregorian_to_jalali, redirect_back
from applications.core.validators import is_valid_date
from applications.core.requiredAccess import RequiredAccess
from applications.core.decorators import is_admin_required
from applications.role.models import Role
from applications.user.forms import backend__userForm
from applications.user.models import User
from applications.user.validation import adminValidation


@is_admin_required
def index(request):
    RequiredAccess(request, 'UserRead')
    data = {}
    data["pageTitle"] = 'لیست کاربر'
    data["newUrl"] = reverse('app_user:user_create')
    data["searchUrl"] = reverse('app_user:user_index')

    data["exportExcel"] = reverse('app_user:user_export_excel')

    data["paginateUrl"] = ''

    all = User.objects.select_related(
        'relation_profile',
        'relation_received_invitation', 
        'relation_received_invitation__inviter'
        ).filter(type__in=["", ""])
    
    if request.GET.get('q'):
        data["paginateUrl"] = f"q={request.GET.get('q')}&"
        all = all.filter(Q(first_name__icontains=request.GET.get('q')) |
                         Q(last_name__icontains=request.GET.get('q')) |
                         Q(mobile__icontains=request.GET.get('q')))

    data["filterDate"] = 1
    if request.GET.get('filterDateStart'):
        if is_valid_date(request.GET.get('filterDateStart')):
            data["filterDateStart"] = request.GET.get('filterDateStart')
            all = all.filter(recruitmentDay__gte=request.GET.get('filterDateStart'))
    if request.GET.get('filterDateEnd'):
        if is_valid_date(request.GET.get('filterDateEnd')):
            data["filterDateEnd"] = request.GET.get('filterDateEnd')
            all = all.filter(recruitmentDay__lte=request.GET.get('filterDateEnd'))

    data["paginateUrl"] += f"count={request.GET.get('count')}&" + f"sort={request.GET.get('sort')}&"

    data["sortWithActiveDeactive"] = 1

    if request.GET.get('sort') == 'asc':
        all = all.order_by('id')
    elif request.GET.get('sort') == 'desc':
        all = all.order_by('-id')
    elif request.GET.get('sort') == 'active':
        all = all.filter(is_active=1)
    elif request.GET.get('sort') == 'deactive':
        all = all.filter(is_active=0)

    data["searchCount"] = (int(request.GET.get('count')) if request.GET.get('count').isnumeric() else 10) if request.GET.get('count') else 10
    paginator = Paginator(all, data["searchCount"])
    page_number = request.GET.get('page')
    data["all"] = paginator.get_page(page_number)
    data["total"] = all.count

    data["searchSort"] = request.GET.get('sort')
    data["searchText"] = request.GET.get('q') if request.GET.get('q') else ''

    data["faFields"] = ['نام', 'نام خانوادگی', 'موبایل',  'فعال']
    data["EnFields"] = ['first_name', 'last_name', 'mobile', 'is_active']

    data["editUrl"] = 'app_user:user_update'
    data["deleteUrl"] = 'app_user:user_delete'

    return render(request, "pages/all.html", {"data": data})



@is_admin_required
def create(request):
    RequiredAccess(request, 'UserCreate')
    data = {}
    data["pageTitle"] = 'اضافه کردن کاربر جدید'
    data["backUrl"] = reverse('app_user:user_index')
    data["storeUrl"] = reverse('app_user::user_create')
    data["items"] = backend__userForm(None)

    if request.method == "POST":
        if adminValidation(request, None):
            user = storeAndUpdateUser(request, None)
            messages.add_message(request, messages.SUCCESS, json.dumps({'text': 'کاربر با موفقیت ایجاد شد'}))
            return redirect('app_user:user_index')

    return render(request, "pages/form.html", {"data": data})


@is_admin_required
def update(request, id):
    RequiredAccess(request, 'UserUpdate')
    user = User.objects.filter(id=id).first()
    if user is None:
        messages.add_message(request, messages.ERROR, json.dumps({'text': 'کاربر یافت نشد'}))
        return redirect_back(request)

    data = {}
    data["pageTitle"] = 'بروزرسانی کاربر'
    data["backUrl"] = reverse('app_user:user_index')
    data["storeUrl"] = reverse('app_user:user_update', kwargs={"id": user.id})
    data["items"] = backend__userForm(user)

    if request.method == "POST":
        if adminValidation(request, id):
            storeAndUpdateUser(request, user)
            messages.add_message(request, messages.SUCCESS, json.dumps({'text': 'کاربر با موفقیت بروزرسانی شد'}))
            return redirect('app_user:user_index')
    return render(request, "pages/form.html", {"data": data})


@is_admin_required
def delete(request, id):
    RequiredAccess(request, 'UserDelete')
    if request.method == "POST":
        user = User.objects.filter(id=id).first()
        if user is None:
            messages.add_message(request, messages.ERROR, json.dumps({'text': 'کاربر یافت نشد'}))
            return redirect_back(request)

        user.delete()
        messages.add_message(request, messages.SUCCESS, json.dumps({'text': 'کاربر با موفقیت حذف شد'}))
    else:
        messages.add_message(request, messages.ERROR, json.dumps({'text': 'درخواست نا معتبر است'}))

    return redirect('app_user:user_index')


##################################################################################
##################################################################################
##################################################################################
##################################################################################   Excel

def exportExcelUser(request):
    all = User.objects.all()
    userLists = []
    for user in all:
        newUser = []
        newUser.append(user.first_name)
        newUser.append(user.last_name)
        newUser.append(user.nationalCode)
        newUser.append(user.personCode)
        newUser.append(user.mobile)
        newUser.append(user.salary)
        newUser.append(user.identifyNo)
        newUser.append(user.fatherName)
        newUser.append(user.issued)
        newUser.append(user.phone)
        newUser.append(user.job)
        newUser.append(user.section)
        newUser.append(user.unit)
        newUser.append(gregorian_to_jalali(user.recruitmentDay))
        newUser.append(gregorian_to_jalali(user.startContractDay))
        newUser.append(gregorian_to_jalali(user.endContractDay))
        newUser.append(gregorian_to_jalali(user.birthDay))
        newUser.append(gregorian_to_jalali(user.marriageDay))
        newUser.append(user.address)

        userLists.append(newUser)

    custom_header = ['نام', 'نام خانوادگی', 'کد ملی', 'کد کاربری', 'شماره موبایل', 'پایه حقوق', 'شماره شناسنامه', 'نام پدر', 'صادره', 'تلفن ثابت',
                     'سمت', 'بخش', 'واحد', 'تاریخ استخدام', 'تاریخ شروع قرارداد', 'تاریخ پایان قرارداد', 'تاریخ تولد', 'تاریخ ازدواج', 'آدرس']

    jalali = JalaliDate(datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)).strftime("%Y-%m-%d")
    name = 'personels ' + str(jalali) + '.xlsx'

    # df = pd.DataFrame(userLists)
    # path = settings.MEDIA_ROOT + '/static/files/export/' + name
    # df.to_excel(path, index=False, na_rep='N/A', header=custom_header, index_label='ID')

    df = pd.DataFrame(userLists)
    path = Path(settings.MEDIA_ROOT) / 'static' / 'files' / 'export' / name
    df.to_excel(path, index=False, na_rep='N/A', header=custom_header, index_label='ID')

    return FileResponse(open(path, 'rb'))


################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
# Store
def storeAndUpdateUser(request, user):
    if user is None:
        user = User(
            is_superuser=0,
            is_active=1 if request.POST.get('active') else 0,
            is_staff=1,
            user_type=2,
            role_ids=[],
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            # password=make_password(str(request.POST.get('mobile'))),
            password='pbkdf2_sha256$390000$VDsB4fzMJesQIqq9aWMQTi$QA5kGxSKScuSerwqr2+i/ZSd5nC9zZ+/ZNfHGrP4bow=',
            nationalCode=request.POST.get('nationalCode'),
            personCode=request.POST.get('personCode'),
            mobile=request.POST.get('mobile'),
        )
        user.save()

    if user:
        user.is_active = 1 if request.POST.get('active') else 0
        user.lat = request.POST.get('lat') if request.POST.get('lat') else user.lat
        user.long = request.POST.get('long') if request.POST.get('long') else user.long
        user.last_name = request.POST.get('last_name')
        user.mobile = request.POST.get('mobile')
        user.nationalCode = request.POST.get('nationalCode')
        user.personCode = request.POST.get('personCode')
        user.address = request.POST.get('address')
        user.phone = request.POST.get('phone') if request.POST.get('phone') else None
        user.job_id = request.POST.get('job')
        user.photo = request.FILES.get('photo') if 'photo' in request.FILES else user.photo
        user.password = make_password(str(request.POST.get('password'))) if request.POST.get('password') else user.password
        
        user.save()
    return user
