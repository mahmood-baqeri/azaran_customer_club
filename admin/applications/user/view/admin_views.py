from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.hashers import make_password
import json
from django_dump_die.middleware import dd


from applications.core.utils import redirect_back
from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess
from applications.user.forms import backend__adminForm, backend__changePass, backend__profileForm
from applications.user.models import User
from django.db.models import Q
from django.core.paginator import Paginator
from applications.user.validation import adminValidation, changePassValidation


@is_admin_required
def index(request):
    RequiredAccess(request, 'AdminRead')

    data = {}
    data["pageTitle"] = 'مدیران'
    data["newUrl"] = reverse('app_user:create')
    data["searchUrl"] = reverse('app_user:index')

    data["paginateUrl"] = ''

    allUser = User.objects.all()
    allUser = allUser.filter(is_superuser=1, is_staff=1, user_type=1)
    if request.GET.get('q'):
        data["paginateUrl"] = f"q={request.GET.get('q')}&"
        allUser = allUser.filter(Q(first_name__icontains=request.GET.get('q')) |
                                 Q(last_name__icontains=request.GET.get('q')) |
                                 Q(mobile__icontains=request.GET.get('q')))

    data["paginateUrl"] += f"count={request.GET.get('count')}&" + f"sort={request.GET.get('sort')}&"

    if request.GET.get('sort') == 'asc':
        allUser = allUser.order_by('id')
    elif request.GET.get('sort') == 'desc':
        allUser = allUser.order_by('-id')

    data["searchCount"] = (int(request.GET.get('count')) if request.GET.get('count').isnumeric() else 10) if request.GET.get('count') else 10
    paginator = Paginator(allUser, data["searchCount"])
    page_number = request.GET.get('page')
    data["all"] = paginator.get_page(page_number)
    data["total"] = allUser.count

    data["searchSort"] = request.GET.get('sort')
    data["searchText"] = request.GET.get('q') if request.GET.get('q') else ''

    data["faFields"] = ['نام', 'نام خانوادگی', 'موبایل', 'تلفن ثابت', 'کدملی', 'تاریخ عضویت', 'فعال', 'تبدیل به پرسنل']
    data["EnFields"] = ['first_name', 'last_name', 'mobile', 'phone', 'nationalCode', 'created', 'is_active', 'changeToPerson']
    data["editUrl"] = 'app_user:update'
    data["deleteUrl"] = 'app_user:delete'

    return render(request, "pages/all.html", {"data": data})


@is_admin_required
def create(request):
    RequiredAccess(request, 'AdminCreate')

    data = {
        "pageTitle": 'اضافه کردن مدیر جدید',
        "backUrl": reverse('app_user:index'),
        "storeUrl": reverse('app_user:create'),
        "items": backend__adminForm(None)
    }

    if request.method == "POST":
        if adminValidation(request, None):
            user = storeAndUpdateAdmin(request, None, 'admin')
            messages.add_message(request, messages.SUCCESS, json.dumps({'text': 'مدیر با موفقیت ایجاد شد'}))
            return redirect('app_user:index')

    return render(request, "pages/form.html", {"data": data})


@is_admin_required
def update(request, id):
    RequiredAccess(request, 'AdminUpdate')
    user = User.objects.filter(id=id).first()
    if user is None:
        messages.add_message(request, messages.ERROR, json.dumps({'text': 'مدیر یافت نشد'}))
        return redirect_back(request)

    data = {}
    data["pageTitle"] = 'بروزرسانی مدیر'
    data["backUrl"] = reverse('app_user:index')
    data["storeUrl"] = reverse('app_user:update', kwargs={"id": user.id})
    data["items"] = backend__adminForm(user)

    if request.method == "POST":
        if adminValidation(request, id):
            storeAndUpdateAdmin(request, user, 'admin')

            messages.add_message(request, messages.SUCCESS, json.dumps({'text': 'مدیر با موفقیت بروزرسانی شد'}))
            return redirect('app_user:index')
    return render(request, "pages/form.html", {"data": data})


@is_admin_required
def delete(request, id):
    RequiredAccess(request, 'AdminDelete')
    if request.method == "POST":
        user = User.objects.filter(id=id).first()
        if user is None:
            messages.add_message(request, messages.ERROR, json.dumps({'text': 'مدیر یافت نشد'}))

        user.delete()
        messages.add_message(request, messages.SUCCESS, json.dumps({'text': 'مدیر با موفقیت حذف شد'}))
    else:
        messages.add_message(request, messages.ERROR, json.dumps({'text': 'درخواست نا معتبر است'}))

    return redirect('app_user:index')


################################################################################
################################################################################
#########################################################
@is_admin_required
def profile(request):
    user = request.user
    if user is None:
        messages.add_message(request, messages.ERROR, json.dumps({'text': 'مدیر یافت نشد'}))
        return redirect_back(request)

    data = {}
    data["pageTitle"] = 'بروزرسانی پروفایل'
    data["backUrl"] = reverse('app_user:index')
    data["storeUrl"] = reverse('app_user:profile')
    data["items"] = backend__profileForm(user)

    if request.method == "POST":
        if adminValidation(request, user.pk):
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.mobile = request.POST.get('mobile')
            user.photo = request.FILES.get('photo') if 'photo' in request.FILES else user.photo
            user.save()
            messages.add_message(request, messages.SUCCESS, json.dumps({'text': 'پروفایل با موفقیت بروزرسانی شد'}))
    return render(request, "pages/form.html", {"data": data})


@is_admin_required
def changePass(request):
    user = request.user
    data = {}
    data["pageTitle"] = 'تغییر رمز عبور'
    data["backUrl"] = reverse('app_user:index')
    data["storeUrl"] = reverse('app_user:changePass')
    data["forgetPass"] = 1
    data["items"] = backend__changePass()
    if request.method == "POST":
        if changePassValidation(request):
            user.password = make_password(str(request.POST.get('newPassword')))
            user.save()
            messages.add_message(request, messages.SUCCESS, json.dumps({'text': 'رمز عبور با موفقیت تغییر یافت'}))

    return render(request, "pages/form.html", {"data": data})



################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
# Store
def storeAndUpdateAdmin(request, user, _type):
    adRoles = []
    for role in request.POST.getlist('roles'):
        adRoles.append(int(role))

    if user is None:
        user = User(
            is_superuser=1,
            is_active=1 if request.POST.get('active') else 0,
            is_staff=1,
            user_type=1,
            role_ids=adRoles,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            password=make_password(str(request.POST.get('mobile'))),
            mobile=request.POST.get('mobile'),
        )
        user.save()

    if user:
        user.is_active = 1 if request.POST.get('active') else 0
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.mobile = request.POST.get('mobile')
        user.role_ids = adRoles
        user.nationalCode = request.POST.get('nationalCode')
        user.personCode = request.POST.get('personCode')
        user.address = request.POST.get('address')
        user.photo = request.FILES.get('photo') if 'photo' in request.FILES else user.photo

        user.save()
    return user
