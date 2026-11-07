import json

from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from applications.core.requiredAccess import RequiredAccess
from applications.core.utils import redirect_back
from applications.setting.validation import setting__slider__validation
from applications.core.fileManager import deleteFile
from applications.setting.forms import setting__slider__form
from applications.setting.models import Slider, setting__slider__store


from applications.core.decorators import is_admin_required, authentication_required
from django.utils.translation import gettext_lazy as _


@is_admin_required
def index(request):
    RequiredAccess(request, 'SettingRead')
    data = {}
    data["pageTitle"] = "لیست اسلایدر ها"
    data["newUrl"] = reverse('setting:createSlider')
    data["searchUrl"] = reverse('setting:indexSlider')

    data["paginateUrl"] = ''

    all = Slider.objects.all()
    if request.GET.get('q'):
        data["paginateUrl"] = f"q={request.GET.get('q')}&"
        all = all.filter(Q(title__icontains=request.GET.get('q')))

    data["paginateUrl"] += f"count={request.GET.get('count')}&" + f"sort={request.GET.get('sort')}&"

    if request.GET.get('sort') == 'asc':
        all = all.order_by('id')
    elif request.GET.get('sort') == 'desc':
        all = all.order_by('-id')

    data["searchCount"] = (int(request.GET.get('count')) if request.GET.get('count').isnumeric() else 10) if request.GET.get('count') else 10
    paginator = Paginator(all, data["searchCount"])
    page_number = request.GET.get('page')
    data["all"] = paginator.get_page(page_number)
    data["total"] = all.count

    data["searchSort"] = request.GET.get('sort')
    data["searchText"] = request.GET.get('q') if request.GET.get('q') else ''

    data["faFields"] = ["عنوان", "پاتراگراف", "تصویر", "وضعیت"]
    data["EnFields"] = ['title', 'paragraph', 'photo', 'is_active']
    data["editUrl"] = 'setting:updateSlider'
    data["deleteUrl"] = 'setting:deleteSlider'

    return render(request, "pages/all.html", {"data": data})


@is_admin_required
def create(request):
    RequiredAccess(request, 'SettingCreate')
    data = {}
    data["pageTitle"] = "اضافه کردن اسلایدر جدید"
    data["backUrl"] = reverse('setting:indexSlider')
    data["storeUrl"] = reverse('setting:createSlider')
    data["items"] = setting__slider__form()

    if request.method == "POST":
        if setting__slider__validation(request):
            setting__slider__store(request, None)
            messages.add_message(request, messages.SUCCESS, json.dumps({'text': 'اسلاید با موفقیت ایجاد شد'}))
            return redirect('setting:indexSlider')

    return render(request, "pages/form.html", {"data": data})


@is_admin_required
def update(request, id):
    RequiredAccess(request, 'SettingUpdate')
    slider = Slider.objects.filter(id=id).first()
    if slider is None:
        messages.add_message(request, messages.ERROR, json.dumps({'text': f"اسلاید یافت نشد"}))
        return redirect_back(request)

    data = {}
    data["pageTitle"] = "بروزرسانی اسلاید"
    data["backUrl"] = reverse('setting:indexSlider')
    data["storeUrl"] = reverse('setting:updateSlider', kwargs={"id": slider.id})
    data["items"] = setting__slider__form(slider)

    if request.method == "POST":
        if setting__slider__validation(request, True):
            setting__slider__store(request, slider)
            messages.add_message(request, messages.SUCCESS, json.dumps({'text': f"اسلاید با موفقیت بروز شد"}))
            return redirect('setting:indexSlider')
    return render(request, "pages/form.html", {"data": data})


@is_admin_required
def delete(request, id):
    RequiredAccess(request, 'SettingDelete')
    if request.method == "POST":
        slider = Slider.objects.filter(id=id).first()
        if slider is None:
            messages.add_message(request, messages.ERROR, json.dumps({'text': f"اسلاید یافت نشد"}))
            return redirect_back(request)

        slider.delete()
        messages.add_message(request, messages.SUCCESS, json.dumps({'text': f"حذف با موفقیت انجام شد"}))
    else:
        messages.add_message(request, messages.ERROR, json.dumps({'text': f"درخواست غیر مجاز"}))

    return redirect('setting:indexSlider')
