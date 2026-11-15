# applications/gift/views/gift.py

import json
import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from applications.core.fileManager import deleteFile
from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess
from applications.core.utils import redirect_back, response_msg

from ..clean_data import gift__clean__data
from ..forms import gift__form
from ..models import Gift
from ..repositories import gift__store

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def gift_index(request):
    RequiredAccess(request, "GiftRead")

    qs = Gift.objects.all()

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

    filter_val = (request.GET.get("filter") or "").strip()
    if filter_val in dict(Gift.ForUser.choices):
        qs = qs.filter(for_user=filter_val)

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


# ═══════════════════════════════════════════════════════════
# CREATE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def gift_create(request):
    RequiredAccess(request, "GiftCreate")

    if request.method == "POST":
        cleaned, errors = gift__clean__data(request.POST)

        if errors:
            for err in errors:
                response_msg(request, messages.ERROR, err)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد هدیه جدید",
                    "backUrl": reverse("app_gift:gift_index"),
                    "storeUrl": reverse("app_gift:gift_create"),
                    "items": gift__form(raw_data=request.POST),
                }
            })

        try:
            gift__store(request, cleaned=cleaned)
        except Exception:
            logger.exception("gift_create failed")
            response_msg(request, messages.ERROR, "خطا در ذخیره هدیه")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد هدیه جدید",
                    "backUrl": reverse("app_gift:gift_index"),
                    "storeUrl": reverse("app_gift:gift_create"),
                    "items": gift__form(raw_data=request.POST),
                }
            })

        response_msg(request, messages.SUCCESS, "هدیه با موفقیت ایجاد شد")
        return redirect("app_gift:gift_index")

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ایجاد هدیه جدید",
            "backUrl": reverse("app_gift:gift_index"),
            "storeUrl": reverse("app_gift:gift_create"),
            "items": gift__form(),
        }
    })


# ═══════════════════════════════════════════════════════════
# UPDATE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def gift_update(request, id):
    RequiredAccess(request, "GiftUpdate")
    gift = get_object_or_404(Gift, id=id)

    if request.method == "POST":
        cleaned, errors = gift__clean__data(request.POST)

        if errors:
            for err in errors:
                response_msg(request, messages.ERROR, err)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ویرایش هدیه",
                    "backUrl": reverse("app_gift:gift_index"),
                    "storeUrl": reverse("app_gift:gift_update", kwargs={"id": gift.id}),
                    "items": gift__form(gift=gift, raw_data=request.POST),
                }
            })

        try:
            gift__store(request, cleaned=cleaned, item=gift)
        except Exception:
            logger.exception("gift_update failed id=%s", id)
            response_msg(request, messages.ERROR, "خطا در ذخیره هدیه")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ویرایش هدیه",
                    "backUrl": reverse("app_gift:gift_index"),
                    "storeUrl": reverse("app_gift:gift_update", kwargs={"id": gift.id}),
                    "items": gift__form(gift=gift, raw_data=request.POST),
                }
            })

        response_msg(request, messages.SUCCESS, "هدیه با موفقیت به‌روزرسانی شد")
        return redirect("app_gift:gift_index")

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ویرایش هدیه",
            "backUrl": reverse("app_gift:gift_index"),
            "storeUrl": reverse("app_gift:gift_update", kwargs={"id": gift.id}),
            "items": gift__form(gift=gift),
        }
    })


# ═══════════════════════════════════════════════════════════
# DELETE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def gift_delete(request, id):
    RequiredAccess(request, "GiftDelete")
    if request.method != "POST":
        response_msg(request, messages.ERROR, "درخواست نامعتبر")
        return redirect("app_gift:gift_index")

    gift = get_object_or_404(Gift, id=id)
    if gift.orders.exists():
        response_msg(request, messages.ERROR, "این هدیه دارای سفارش است و قابل حذف نیست")
        return redirect_back(request)

    gift.delete()
    response_msg(request, messages.SUCCESS, "هدیه با موفقیت حذف شد")
    return redirect("app_gift:gift_index")


# ═══════════════════════════════════════════════════════════
# AJAX — حذف عکس گالری (ساختار response جدا از messages)
# ═══════════════════════════════════════════════════════════
@is_admin_required
def remove_attachment(request):
    if request.method != "POST":
        return JsonResponse({"data": "درخواست نامعتبر"}, status=400)

    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"data": "بدنه‌ی نامعتبر"}, status=400)

    param = body.get("param") or {}
    item_id = param.get("itemId")
    path    = param.get("path")
    g_index = param.get("galleryIndex")

    if not item_id:
        return JsonResponse({"data": "شناسه الزامی است"}, status=400)

    gift = get_object_or_404(Gift, pk=item_id)
    gallery = list(gift.gallery or [])

    target_index = None

    if path:
        filename = path.rsplit("/", 1)[-1]
        for i, p in enumerate(gallery):
            if str(p).rsplit("/", 1)[-1] == filename:
                target_index = i
                break

    if target_index is None and g_index is not None:
        try:
            i = int(g_index)
            if 0 <= i < len(gallery):
                target_index = i
        except (TypeError, ValueError):
            pass

    if target_index is None:
        return JsonResponse({"data": "تصویر یافت نشد"}, status=404)

    try:
        deleteFile(gallery[target_index])
    except Exception:
        logger.warning("Could not delete %s for gift %s", gallery[target_index], gift.pk)

    gallery.pop(target_index)
    gift.gallery = gallery
    gift.save(update_fields=["gallery", "updated_at"])

    return JsonResponse({"data": "ok"}, status=200)