from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
import json
from django.core.paginator import Paginator

from applications.core.utils import redirect_back
from applications.core.decorators import is_admin_required
from applications.core.keyValue import settingBoolean, settingLong, settingPhoto
from applications.core.requiredAccess import RequiredAccess
from applications.setting.forms import setting__setting__form
from applications.setting.models import Setting


@is_admin_required
def index(request):
    RequiredAccess(request, 'SettingRead')
    data = {}
    data["pageTitle"] = 'لیست تنظیمات سایت'
    data["searchUrl"] = reverse('setting:index')
    data["newUrl"] = reverse('setting:create')

    data["paginateUrl"] = ''

    allSetting = Setting.objects.all()

    pagiantCount = (int(request.GET.get('count')) if request.GET.get('count').isnumeric() else 10) if request.GET.get('count') else 10
    data["paginateUrl"] += f"count={pagiantCount}&"
    data["paginateUrl"] += f"sort={request.GET.get('sort')}&"
    if request.GET.get('sort') == 'asc':
        allSetting = allSetting.order_by('id')
    if request.GET.get('sort') == 'desc':
        allSetting = allSetting.order_by('-id')

    paginator = Paginator(allSetting, pagiantCount)
    page_number = request.GET.get('page')
    data["all"] = paginator.get_page(page_number)
    data["total"] = allSetting.count

    data["searchCount"] = pagiantCount
    data["searchSort"] = request.GET.get('sort')
    data["searchText"] = request.GET.get('q') if request.GET.get('q') else ''

    data["photoList"] = settingPhoto()
    data["boolean"] = settingBoolean()
    data["long"] = settingLong()

    return render(request, "pages/setting.html", {"data": data})


@is_admin_required
def create(request):
    RequiredAccess(request, 'SettingCreate')
    data = {}
    data["pageTitle"] = 'اضافه کردن مورد جدید'
    data["backUrl"] = reverse('setting:index')
    data["storeUrl"] = reverse('setting:create')
    data["scriptSetting"] = 1
    data["items"] = setting__setting__form()

    if request.method == "POST":
        theValue = request.POST.get('theValue')
        if theValue == '':
            messages.add_message(request, messages.ERROR, json.dumps({'text': 'داده الزامیست'}))
        else:
            key = request.POST.get('key')
            setting = Setting.objects.filter(key=key).first()
            if setting:
                messages.add_message(request, messages.ERROR, json.dumps({'text': 'این مورد قبلا ایجاد شده است'}))
            else:
                newSetting = Setting(key=key)
                newSetting.save()

                if key in settingPhoto():
                    newSetting.value_file = request.FILES.get('theValue')
                else:
                    newSetting.value_text = theValue

                newSetting.save()
                messages.add_message(request, messages.SUCCESS, json.dumps({'text': 'مورد با موفقیت ایجاد شد'}))
                return redirect('setting:index')

    return render(request, "pages/form.html", {"data": data})


@is_admin_required
def update(request, id):
    RequiredAccess(request, 'SettingUpdate')
    setting = Setting.objects.filter(id=id).first()
    if setting is None:
        messages.add_message(request, messages.ERROR, json.dumps({'text': 'گزینه مورد نظر یافت نشد'}))
        return redirect_back(request)

    data = {}
    data["pageTitle"] = 'بروزرسانی' + ''
    data["backUrl"] = reverse('setting:index')
    data["storeUrl"] = reverse('setting:update', kwargs={"id": setting.id})
    data["items"] = setting__setting__form(setting)
    data["scriptSetting"] = 1
    if request.method == "POST":
        theValue = request.POST.get('theValue')
        if theValue == '':
            messages.add_message(request, messages.ERROR, json.dumps({'text': 'داده الزامیست'}))
        else:
            key = request.POST.get('key')
            if key in settingPhoto():
                setting.value_file = request.FILES.get('theValue')
            else:
                setting.value_text = theValue
            setting.save()

            messages.add_message(request, messages.SUCCESS, json.dumps({'text': 'گزینه با موفقیت بروزرسانی شد'}))
            return redirect('setting:index')

    return render(request, "pages/form.html", {"data": data})
