import os
import json
import uuid

from io import BytesIO

from PIL import Image

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from applications.core.requiredAccess import RequiredAccess
from applications.core.utils import redirect_back
from applications.core.decorators import is_admin_required
from applications.page.models import Category, Page
from applications.page.forms import PageForm, PageFilterForm


# ============================================================
# لیست صفحات
# ============================================================
@is_admin_required
def page_list(request):
    RequiredAccess(request, 'PageRead')
    
    filter_form = PageFilterForm(request.GET or None)

    queryset = Page.objects.all().select_related("category")

    if filter_form.is_valid():
        search = filter_form.cleaned_data.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(summer__icontains=search)
                | Q(text__icontains=search)
                | Q(slug__icontains=search)
                | Q(category__title__icontains=search)
            ).distinct()

        category = filter_form.cleaned_data.get("category")
        if category:
            queryset = queryset.filter(category=category)

        type_value = filter_form.cleaned_data.get("type")
        if type_value:
            queryset = queryset.filter(type=type_value)

        is_active = filter_form.cleaned_data.get("is_active")
        if is_active:
            queryset = queryset.filter(is_active=(is_active == "True"))

    # مرتب‌سازی
    sort_by = request.GET.get("sort", "-id")
    try:
        queryset = queryset.order_by(sort_by)
    except Exception:
        queryset = queryset.order_by("-id")

    paginator = Paginator(queryset, 20)
    page_number = request.GET.get("page", 1)

    try:
        pages = paginator.page(page_number)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)

    context = {
        "data": {
            "pageTitle": "مدیریت صفحات",
            "pages": pages,
            "all": pages,
            "total": paginator.count,
            "filter_form": filter_form,
            "categories": Category.objects.filter(is_active=True),
        }
    }
    return render(request, "pages/page/list.html", context)


# ============================================================
# ایجاد صفحه
# ============================================================
@is_admin_required
@permission_required("page.add_page", raise_exception=True)
def page_add(request):
    RequiredAccess(request, 'PageCreate')
    
    if request.method == "POST":
        form = PageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, json.dumps({'text': 'صفحه با موفقیت ایجاد شد.'}))
            return redirect("pagemanagement:admin_page_list")
    else:
        form = PageForm()

    context = {
        "form": form,
        "data": {
            "pageTitle": "افزودن صفحه جدید",
            "is_edit": False,
            "categories": Category.objects.filter(is_active=True),
        },
    }
    return render(request, "pages/page/form.html", context)


# ============================================================
# ویرایش صفحه
# ============================================================
@is_admin_required
@permission_required("page.change_page", raise_exception=True)
def page_edit(request, pk):
    RequiredAccess(request, 'PageUpdate')
    
    page = Page.objects.filter(pk=pk).first()
    if page is None:
        messages.add_message(request, messages.ERROR, json.dumps({'text': 'صفحه یافت نشد'}))
        return redirect_back(request)

    if request.method == "POST":
        form = PageForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, json.dumps({'text': 'صفحه با موفقیت ویرایش شد.'}))
            return redirect("pagemanagement:admin_page_list")
    else:
        form = PageForm(instance=page)

    context = {
        "form": form,
        "data": {
            "pageTitle": "ویرایش صفحه",
            "page": page,
            "is_edit": True,
            "categories": Category.objects.filter(is_active=True),
        },
    }
    return render(request, "pages/page/form.html", context)


# ============================================================
# حذف صفحه
# ============================================================
@is_admin_required
@permission_required("page.delete_page", raise_exception=True)
@require_http_methods(["POST"])
def page_delete(request):
    RequiredAccess(request, 'PageDelete')
    
    page_id = request.POST.get("id")
    if not page_id:
        return JsonResponse({"success": False, "error": "شناسه صفحه ارسال نشده است"})

    page = Page.objects.filter(pk=page_id).first()
    if not page:
        return JsonResponse({"success": False, "error": "صفحه یافت نشد"})

    page.delete()
    return JsonResponse({"success": True, "message": "صفحه با موفقیت حذف شد"})


# ============================================================
# تغییر وضعیت
# ============================================================
@is_admin_required
@permission_required("page.change_page", raise_exception=True)
@require_http_methods(["POST"])
def page_toggle_status(request):
    RequiredAccess(request, 'PageUpdate')
    
    page_id = request.POST.get("id")
    if not page_id:
        return JsonResponse({"success": False, "error": "شناسه صفحه ارسال نشده است"})

    page = Page.objects.filter(pk=page_id).first()
    if not page:
        return JsonResponse({"success": False, "error": "صفحه یافت نشد"})

    page.is_active = not page.is_active
    page.save(update_fields=["is_active"])
    return JsonResponse({
        "success": True,
        "is_active": page.is_active,
        "message": f"وضعیت به {'فعال' if page.is_active else 'غیرفعال'} تغییر یافت",
    })


# ============================================================
# عملیات دسته‌جمعی
# ============================================================
@is_admin_required
@permission_required("page.change_page", raise_exception=True)
@require_http_methods(["POST"])
def page_bulk_action(request):
    RequiredAccess(request, 'PageUpdate')
    
    ids = request.POST.getlist("ids[]") or request.POST.getlist("ids")
    action = request.POST.get("action")

    if not ids or not action:
        return JsonResponse({"success": False, "error": "اطلاعات کامل ارسال نشده است"})

    queryset = Page.objects.filter(id__in=ids)

    actions_map = {
        "delete": lambda q: q.delete(),
        "activate": lambda q: q.update(is_active=True),
        "deactivate": lambda q: q.update(is_active=False),
    }
    messages_map = {
        "delete": "صفحه حذف شدند",
        "activate": "صفحه فعال شدند",
        "deactivate": "صفحه غیرفعال شدند",
    }

    if action not in actions_map:
        return JsonResponse({"success": False, "error": "عملیات نامعتبر"})

    result = actions_map[action](queryset)
    count = result if isinstance(result, int) else queryset.count()
    return JsonResponse({"success": True, "message": f"{count} {messages_map.get(action, 'عملیات انجام شد')}"})


# ============================================================
# آمار — بهینه با annotate
# ============================================================
@is_admin_required
@permission_required("page.view_page", raise_exception=True)
@require_http_methods(["GET"])
def page_stats(request):
    RequiredAccess(request, 'PageRead')
    
    pages = Page.objects.all()
    stats = {
        "total": pages.count(),
        "active": pages.filter(is_active=True).count(),
        "inactive": pages.filter(is_active=False).count(),
        "by_type": {},
        "by_category": {},
    }

    for type_code, _label in Page.PageType.choices:
        stats["by_type"][type_code] = pages.filter(type=type_code).count()

    # یک کوئری به جای N کوئری
    by_cat = (
        pages.filter(category__isnull=False)
        .values("category__title")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    stats["by_category"] = {row["category__title"]: row["count"] for row in by_cat}

    return JsonResponse({"success": True, "data": stats})


# ============================================================
# گالری
# ============================================================
@is_admin_required
@csrf_exempt
@require_http_methods(["POST"])
def upload_gallery_images(request):
    RequiredAccess(request, 'PageRead')
    
    try:
        files = request.FILES.getlist("gallery_images")
        if not files:
            return JsonResponse({"status": "error", "message": "هیچ فایلی آپلود نشده است"}, status=400)

        uploaded_urls = []
        failed_files = []

        for file in files:
            try:
                if not file.content_type.startswith("image/"):
                    failed_files.append({"name": file.name, "error": "فرمت فایل تصویر نیست"})
                    continue
                if file.size > 5 * 1024 * 1024:
                    failed_files.append({"name": file.name, "error": "حجم فایل بیشتر از 5MB"})
                    continue

                ext = os.path.splitext(file.name)[1].lower()
                if ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]:
                    ext = ".jpg"

                filename = f"gallery/{request.user.id}_{uuid.uuid4().hex[:10]}{ext}"

                image = Image.open(file)
                if image.width > 1920 or image.height > 1920:
                    image.thumbnail((1920, 1920), Image.Resampling.LANCZOS)

                output = BytesIO()
                fmt = "JPEG" if ext in [".jpg", ".jpeg"] else "PNG"
                if fmt == "JPEG":
                    image = image.convert("RGB")
                    image.save(output, format=fmt, quality=85, optimize=True)
                else:
                    image.save(output, format=fmt, optimize=True)

                output.seek(0)
                saved_path = default_storage.save(filename, ContentFile(output.getvalue()))
                url = default_storage.url(saved_path) if hasattr(default_storage, "url") else f"{settings.MEDIA_URL}{saved_path}"
                uploaded_urls.append(url)
            except Exception as e:
                failed_files.append({"name": file.name, "error": str(e)})

        response_data = {
            "status": "success" if uploaded_urls else "error",
            "images": uploaded_urls,
            "count": len(uploaded_urls),
            "failed": failed_files,
            "message": f"{len(uploaded_urls)} تصویر با موفقیت آپلود شد",
        }
        if failed_files:
            response_data["message"] += f" و {len(failed_files)} فایل ناموفق"
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"خطا در آپلود: {str(e)}"}, status=500)


@is_admin_required
@csrf_exempt
@require_http_methods(["POST"])
def delete_gallery_image(request):
    RequiredAccess(request, 'PageRead')
    
    try:
        image_url = request.POST.get("image")
        if not image_url:
            return JsonResponse({"status": "error", "message": "آدرس تصویر ارسال نشده است"}, status=400)

        media_path = image_url.split(settings.MEDIA_URL)[-1] if settings.MEDIA_URL in image_url else image_url
        if default_storage.exists(media_path):
            default_storage.delete(media_path)

        return JsonResponse({"status": "success", "message": "تصویر حذف شد"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"خطا در حذف: {str(e)}"}, status=500)


@is_admin_required
@csrf_exempt
@require_http_methods(["POST"])
def update_gallery_order(request):
    RequiredAccess(request, 'PageRead')
    
    try:
        data = json.loads(request.body)
        image_order = data.get("images", [])
        page_id = data.get("page_id")

        if not page_id:
            return JsonResponse({"status": "error", "message": "شناسه صفحه ارسال نشده است"}, status=400)

        page = Page.objects.filter(id=page_id).first()
        if not page:
            return JsonResponse({"status": "error", "message": "صفحه یافت نشد"}, status=404)

        page.gallery = image_order
        page.save(update_fields=["gallery"])
        return JsonResponse({"status": "success", "message": "ترتیب تصاویر بروزرسانی شد"})
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "داده‌های ارسالی معتبر نیستند"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"خطا: {str(e)}"}, status=500)