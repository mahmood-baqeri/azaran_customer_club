import json

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from applications.core.utils import redirect_back
from applications.core.requiredAccess import RequiredAccess
from applications.core.decorators import is_admin_required
from applications.category.models import Category
from applications.category.forms import CategoryForm, CategoryFilterForm


# ============================================================
# لیست دسته‌بندی‌ها
# ============================================================
@is_admin_required
def category_list(request):
    RequiredAccess(request, 'CategoryRead')
    
    filter_form = CategoryFilterForm(request.GET or None)

    queryset = Category.objects.select_related("parent").all()

    if filter_form.is_valid():
        search = filter_form.cleaned_data.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(slug__icontains=search)
                | Q(description__icontains=search)
            ).distinct()

        is_active = filter_form.cleaned_data.get("is_active")
        if is_active:
            queryset = queryset.filter(is_active=(is_active == "True"))

        parent = filter_form.cleaned_data.get("parent")
        if parent:
            queryset = queryset.filter(parent=parent)

    # مرتب‌سازی
    sort_by = request.GET.get("sort", "title")
    try:
        queryset = queryset.order_by(sort_by)
    except Exception:
        queryset = queryset.order_by("title")

    paginator = Paginator(queryset, 20)
    page_number = request.GET.get("page", 1)
    try:
        pages = paginator.page(page_number)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)

    # تعداد صفحات هر دسته (برای ستون «تعداد»)
    page_counts = dict(
        Category.objects.values_list("id").annotate(c=Count("pages"))
    )

    # افزودن شمارش به هر آبجکت
    for cat in pages:
        cat.pages_count = page_counts.get(cat.id, 0)

    context = {
        "data": {
            "pageTitle": "مدیریت دسته‌بندی‌ها",
            "categories": pages,
            "all": pages,
            "total": paginator.count,
            "filter_form": filter_form,
        }
    }
    return render(request, "pages/category/list.html", context)


# ============================================================
# ایجاد دسته‌بندی
# ============================================================
@is_admin_required
def category_add(request):
    RequiredAccess(request, 'CategoryCreate')
    
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, json.dumps({'text': 'دسته‌بندی با موفقیت ایجاد شد.'}))
            return redirect("categorymanagement:admin_category_list")
    else:
        form = CategoryForm()

    context = {
        "form": form,
        "data": {
            "pageTitle": "افزودن دسته‌بندی جدید",
            "is_edit": False,
        },
    }
    return render(request, "pages/category/form.html", context)


# ============================================================
# ویرایش دسته‌بندی
# ============================================================
@is_admin_required
def category_edit(request, pk):
    RequiredAccess(request, 'CategoryUpdate')
    
    category = Category.objects.filter(pk=pk).first()
    if category is None:
        messages.add_message(request, messages.ERROR, json.dumps({'text': 'دسته‌بندی یافت نشد'}))
        return redirect_back(request)

    
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.ERROR, json.dumps({'text': 'دسته‌بندی با موفقیت ویرایش شد.'}))
            return redirect("categorymanagement:admin_category_list")
    else:
        form = CategoryForm(instance=category)

    context = {
        "form": form,
        "data": {
            "pageTitle": "ویرایش دسته‌بندی",
            "category": category,
            "is_edit": True,
        },
    }
    return render(request, "pages/category/form.html", context)


# ============================================================
# حذف دسته‌بندی
# ============================================================
@is_admin_required
@require_http_methods(["POST"])
def category_delete(request):
    RequiredAccess(request, 'CategoryDelete')
    
    cat_id = request.POST.get("id")
    
    if not cat_id:
        return JsonResponse({"success": False, "error": "شناسه دسته‌بندی ارسال نشده است"})

    category = Category.objects.filter(pk=cat_id).first()
    if not category:
        return JsonResponse({"success": False, "error": "دسته‌بندی یافت نشد"})

    # چک: اگر صفحات مرتبط دارد، از PROTECT استفاده کرده‌ایم — پیش‌دستی می‌کنیم
    if category.pages.exists():
        return JsonResponse({
            "success": False,
            "error": "این دسته‌بندی دارای صفحه است و قابل حذف نیست",
        })

    if category.children.exists():
        return JsonResponse({
            "success": False,
            "error": "این دسته‌بندی دارای زیردسته است و قابل حذف نیست",
        })

    category.delete()
    return JsonResponse({"success": True, "message": "دسته‌بندی با موفقیت حذف شد"})


# ============================================================
# تغییر وضعیت
# ============================================================
@is_admin_required
@require_http_methods(["POST"])
def category_toggle_status(request):
    RequiredAccess(request, 'CategoryUpdate')
        
    cat_id = request.POST.get("id")
    if not cat_id:
        return JsonResponse({"success": False, "error": "شناسه دسته‌بندی ارسال نشده است"})

    category = Category.objects.filter(pk=cat_id).first()
    if not category:
        return JsonResponse({"success": False, "error": "دسته‌بندی یافت نشد"})

    category.is_active = not category.is_active
    category.save(update_fields=["is_active"])
    return JsonResponse({
        "success": True,
        "is_active": category.is_active,
        "message": f"وضعیت به {'فعال' if category.is_active else 'غیرفعال'} تغییر یافت",
    })


# ============================================================
# عملیات دسته‌جمعی
# ============================================================
@is_admin_required
@require_http_methods(["POST"])
def category_bulk_action(request):
    RequiredAccess(request, 'CategoryUpdate')
        
    ids = request.POST.getlist("ids[]") or request.POST.getlist("ids")
    action = request.POST.get("action")

    if not ids or not action:
        return JsonResponse({"success": False, "error": "اطلاعات کامل ارسال نشده است"})

    queryset = Category.objects.filter(id__in=ids)

    actions_map = {
        "activate": lambda q: q.update(is_active=True),
        "deactivate": lambda q: q.update(is_active=False),
    }
    messages_map = {
        "activate": "دسته‌بندی فعال شدند",
        "deactivate": "دسته‌بندی غیرفعال شدند",
    }

    if action == "delete":
        # چک: اگر هر کدام pages یا children دارد، جلوی حذف را بگیر
        for cat in queryset:
            if cat.pages.exists():
                return JsonResponse({
                    "success": False,
                    "error": f"دسته‌بندی «{cat.title}» دارای صفحه است",
                })
            if cat.children.exists():
                return JsonResponse({
                    "success": False,
                    "error": f"دسته‌بندی «{cat.title}» دارای زیردسته است",
                })
        result = queryset.delete()
        count = result[0] if isinstance(result, tuple) else queryset.count()
        return JsonResponse({"success": True, "message": f"{count} دسته‌بندی حذف شدند"})

    if action not in actions_map:
        return JsonResponse({"success": False, "error": "عملیات نامعتبر"})

    result = actions_map[action](queryset)
    count = result if isinstance(result, int) else queryset.count()
    return JsonResponse({
        "success": True,
        "message": f"{count} {messages_map.get(action, 'عملیات انجام شد')}",
    })



# ============================================================
# دریافت فرزندان (برای مودال view-children)
# ============================================================
@is_admin_required
@require_http_methods(["GET"])
def category_children(request, id):
    RequiredAccess(request, 'CategoryRead')
    parent = Category.objects.filter(pk=id).first()
    if not parent:
        return JsonResponse({"success": False, "error": "دسته‌بندی یافت نشد"}, status=404)

    children = parent.children.all().values("id", "title", "slug", "is_active")
    data = [
        {
            "id": c["id"],
            "title": c["title"],
            "slug": c["slug"],
            "is_active": c["is_active"],
        }
        for c in children
    ]
    return JsonResponse({"success": True, "data": data})