from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
import uuid
import json
import random
from django.db.models import Q
from django.core.paginator import Paginator
from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess
from applications.core.utils import redirect_back
from applications.role.models import Role, Actions, formFields
from applications.user.models import User


@is_admin_required
def index(request):
    RequiredAccess(request, 'RoleRead')
    
    data = {}
    data["pageTitle"] = 'نقش ها'
    data["newUrl"] = reverse('role:create')
    data["searchUrl"] = reverse('role:index')

    data["paginateUrl"] = ''

    allRole = Role.objects.all()
    if request.GET.get('q'):
        data["paginateUrl"] = f"q={request.GET.get('q')}&"
        allRole = allRole.filter(title__icontains=request.GET.get('q'))

    data["paginateUrl"] += f"count={request.GET.get('count')}&"
    data["paginateUrl"] += f"sort={request.GET.get('sort')}&"
    if request.GET.get('sort') == 'asc':
        allRole = allRole.order_by('id')
    if request.GET.get('sort') == 'desc':
        allRole = allRole.order_by('-id')

    data["searchCount"] = (int(request.GET.get('count')) if request.GET.get('count').isnumeric() else 10) if request.GET.get('count') else 10
    paginator = Paginator(allRole, data["searchCount"])
    page_number = request.GET.get('page')
    data["all"] = paginator.get_page(page_number)
    data["total"] = allRole.count

    data["searchSort"] = request.GET.get('sort')
    data["searchText"] = request.GET.get('q') if request.GET.get('q') else ''

    data["faFields"] = ['نام']
    data["EnFields"] = ['title']
    data["editUrl"] = 'role:update'
    data["deleteUrl"] = 'role:delete'

    return render(request, "pages/all.html", {"data": data})


@is_admin_required
def create(request):
    RequiredAccess(request, 'RoleCreate')
    data = {}
    data["pageTitle"] = 'اضافه کردن نقش جدید'
    data["backUrl"] = reverse('role:index')
    data["storeUrl"] = reverse('role:create')
    data["items"] = formFields()

    if request.method == "POST":
        title = request.POST.get('title')

        if title == '':
            messages.add_message(request, messages.ERROR, json.dumps({'text': 'عنوان الزامیست'}))

        else:
            ids = []
            for x in range(1000):
                item = f"action_id#{x}"
                if request.POST.get(item):
                    ids.append(x)

            role = Role.objects.filter(title=title).first()
            if role:
                messages.add_message(request, messages.ERROR, json.dumps({'text': 'این نقش قبلا ایجاد شده است'}))

            else:
                role = Role(
                    title=title,
                    action_ids=ids
                )
                role.save()
                messages.add_message(request, messages.SUCCESS, json.dumps({'text': 'نقش با موفقیت ایجاد شد'}))
                return redirect('role:index')

    return render(request, "pages/form.html", {"data": data})


@is_admin_required
def update(request, id):
    RequiredAccess(request, 'RoleUpdate')
    role = Role.objects.filter(id=id).first()
    if role is None:
        messages.add_message(request, messages.ERROR, json.dumps({'text': 'نقش یافت نشد'}))
        return redirect_back(request)

    data = {}
    data["pageTitle"] = 'بروزرسانی نقش'
    data["backUrl"] = reverse('role:index')
    data["storeUrl"] = reverse('role:update', kwargs={"id": role.id})
    data["items"] = formFields(role)

    if request.method == "POST":
        title = request.POST.get('title')

        if title == '':
            messages.add_message(request, messages.ERROR, json.dumps({'text': 'عنوان الزامیست'}))
        else:
            if Role.objects.filter(title=title).exclude(id=id).first():
                messages.add_message(request, messages.ERROR, json.dumps({'text': 'عنوان قبلا استفاده شده است'}))
            else:
                if role.title in ["مدیر عامل"] and title != role.title:
                    messages.add_message(request, messages.ERROR, json.dumps({'text': 'عنوان قابل ویرایش نیست'}))
                else:
                    ids = []
                    for x in range(1000):
                        item = f"action_id#{x}"
                        if request.POST.get(item):
                            ids.append(x)

                    role.action_ids = ids
                    role.title = title
                    role.save()

                    messages.add_message(request, messages.SUCCESS, json.dumps({'text': 'نقش با موفقیت بروزرسانی شد'}))
                    return redirect('role:index')

    return render(request, "pages/form.html", {"data": data})


@is_admin_required
def delete(request, id):
    RequiredAccess(request, 'RoleDelete')
    if request.method == "POST":
        role = Role.objects.filter(id=id).first()
        if role is None:
            messages.add_message(request, messages.ERROR, json.dumps({'text': 'نقش یافت نشد'}))

        if role.title in ["مدیر عامل"]:
            messages.add_message(request, messages.ERROR, json.dumps({'text': 'این نقش قابل حذف نیست'}))
        else:
            role.delete()
            messages.add_message(request, messages.SUCCESS, json.dumps({'text': 'نقش با موفقیت حذف شد'}))
    else:
        messages.add_message(request, messages.ERROR, json.dumps({'text': 'درخواست نا معتبر است'}))

    return redirect('role:index')
