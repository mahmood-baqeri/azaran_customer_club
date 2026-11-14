# admin/applications/gift/views/gift.py

import json
import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from applications.core.fileManager import deleteFile
from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess
from applications.core.utils import redirect_back
from applications.core.validators import is_valid_date

from ..forms import OrderAssignForm, OrderStatusForm, gift__form
from ..models import Gift, GiftOrder, GiftOrderLog

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# GIFT LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def gift_index(request):
    RequiredAccess(request, "GiftRead")

    qs = Gift.objects.all()

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

    # فیلتر سفارشی (for_user) → theFilterItems
    filter_val = (request.GET.get("filter") or "").strip()
    if filter_val in dict(Gift.ForUser.choices):
        qs = qs.filter(for_user=filter_val)

    # مرتب‌سازی
    sort = request.GET.get("sort", "desc")
    if sort == "asc":
        qs = qs.order_by("id")
    elif sort == "active":
        qs = qs.filter(is_active=True).order_by("-id")
    elif sort == "deactive":
        qs = qs.filter(is_active=False).order_by("-id")
    else:
        qs = qs.order_by("-id")

    try:
        count = int(request.GET.get("count", "10"))
    except ValueError:
        count = 10

    paginator = Paginator(qs, count)
    page = paginator.get_page(request.GET.get("page"))

    data = {
        "pageTitle": "لیست هدایا",
        "newUrl": reverse("app_gift:gift_create"),
        "searchUrl": reverse("app_gift:gift_index"),
        "searchText": q,
        "searchSort": sort,
        "searchCount": count,
        "sortWithActiveDeactive": 1,
        "theFilterItems": list(Gift.ForUser.choices),
        "filter": filter_val,
        "all": page,
        "total": qs.count(),
    }
    return render(request, "pages/gift/all_gifts.html", {"data": data})




@is_admin_required
def gift_create(request):
    RequiredAccess(request, "GiftCreate")

    if request.method == "POST":
        # اعتبارسنجی سبک و ساخت مستقیم (چون form.html از data.items استفاده می‌کند)
        title = (request.POST.get("title") or "").strip()
        for_user = request.POST.get("for_user") or ""
        azar_value = request.POST.get("azar_value") or "0"
        stock = request.POST.get("stock") or "0"

        errors = []
        if not title:
            errors.append("عنوان الزامی است")
        if for_user not in dict(Gift.ForUser.choices):
            errors.append("نوع کاربر نامعتبر است")
        if not azar_value.isdigit():
            errors.append("ارزش آذر نامعتبر است")
        if not stock.lstrip("-").isdigit():
            errors.append("موجودی نامعتبر است")

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد هدیه جدید",
                    "backUrl": reverse("app_gift:gift_index"),
                    "storeUrl": reverse("app_gift:gift_create"),
                    "items": gift__form(raw_data=request.POST),
                }
            })

        gallery_raw = request.POST.get("gallery_text") or ""
        gallery = [line.strip() for line in gallery_raw.splitlines() if line.strip()]

        Gift.objects.create(
            title=title,
            for_user=for_user,
            description=(request.POST.get("description") or "").strip() or None,
            photo=request.FILES.get("photo") or None,
            azar_value=int(azar_value),
            stock=int(stock),
            gallery=gallery,
            is_active=request.POST.get("is_active") == "on",
        )
        messages.success(request, "هدیه با موفقیت ایجاد شد")
        return redirect("app_gift:gift_index")

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ایجاد هدیه جدید",
            "backUrl": reverse("app_gift:gift_index"),
            "storeUrl": reverse("app_gift:gift_create"),
            "items": gift__form(),
        }
    })


@is_admin_required
def gift_update(request, id):
    RequiredAccess(request, "GiftUpdate")
    gift = get_object_or_404(Gift, id=id)

    if request.method == "POST":
        title = (request.POST.get("title") or "").strip()
        for_user = request.POST.get("for_user") or ""
        azar_value = request.POST.get("azar_value") or "0"
        stock = request.POST.get("stock") or "0"

        errors = []
        if not title:
            errors.append("عنوان الزامی است")
        if for_user not in dict(Gift.ForUser.choices):
            errors.append("نوع کاربر نامعتبر است")
        if not azar_value.isdigit():
            errors.append("ارزش آذر نامعتبر است")
        if not stock.lstrip("-").isdigit():
            errors.append("موجودی نامعتبر است")

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ویرایش هدیه",
                    "backUrl": reverse("app_gift:gift_index"),
                    "storeUrl": reverse("app_gift:gift_update", kwargs={"id": gift.id}),
                    "items": gift__form(gift=gift, raw_data=request.POST),
                }
            })

        gallery_raw = request.POST.get("gallery_text") or ""
        gift.gallery = [line.strip() for line in gallery_raw.splitlines() if line.strip()]
        gift.title = title
        gift.for_user = for_user
        gift.description = (request.POST.get("description") or "").strip() or None
        gift.azar_value = int(azar_value)
        gift.stock = int(stock)
        gift.is_active = request.POST.get("is_active") == "on"
        if request.FILES.get("photo"):
            gift.photo = request.FILES["photo"]
        gift.save()

        messages.success(request, "هدیه با موفقیت به‌روزرسانی شد")
        return redirect("app_gift:gift_index")

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ویرایش هدیه",
            "backUrl": reverse("app_gift:gift_index"),
            "storeUrl": reverse("app_gift:gift_update", kwargs={"id": gift.id}),
            "items": gift__form(gift=gift),
        }
    })


@is_admin_required
def gift_delete(request, id):
    RequiredAccess(request, "GiftDelete")
    if request.method != "POST":
        messages.error(request, "درخواست نامعتبر")
        return redirect("app_gift:gift_index")

    gift = get_object_or_404(Gift, id=id)
    if gift.orders.exists():
        messages.error(request, "این هدیه دارای سفارش است و قابل حذف نیست")
        return redirect_back(request)

    gift.delete()
    messages.success(request, "هدیه با موفقیت حذف شد")
    return redirect("app_gift:gift_index")


@is_admin_required
def delete_gallery_photo(request):
    if request.method == "POST":
        inputData = json.loads(request.body)

        gift = Gift.objects.filter(id=inputData['param']['itemId']).first()
        if gift is None:
            return JsonResponse({"data": f"هدیه یافت نشد"}, content_type="application/json", status=203)

        gallery = gift.gallery
        deleteFile(gallery[int(inputData['param']['galleryIndex'])])

        gallery.pop(int(inputData['param']['galleryIndex']))
        gift.gallery = gallery
        gift.save()

        return JsonResponse({"data": 'ok'}, content_type="application/json", status=201)

    else:
        return JsonResponse({"data": f"درخواست نامعتبر"}, content_type="application/json", status=203)