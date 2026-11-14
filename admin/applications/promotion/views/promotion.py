# applications/promotion/views/promotion.py

import json
import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from applications.core.decorators import is_admin_required
from applications.core.requiredAccess import RequiredAccess
from applications.core.utils import redirect_back

from ..clean_data import promotion__clean__data, promotion_item__clean__data
from ..forms import promotion__form, promotion_item__form
from ..models import Promotion, PromotionItem, PromotionOrder
from ..repositories import (
    promotion__store,
    promotion_item__delete,
    promotion_item__store,
)

logger = logging.getLogger(__name__)


def _msg(request, level, text):
    messages.add_message(request, level, json.dumps({"text": text}))


# ═══════════════════════════════════════════════════════════
# PROMOTION LIST
# ═══════════════════════════════════════════════════════════
@is_admin_required
def promotion_index(request):
    RequiredAccess(request, "PromotionRead")

    qs = Promotion.objects.all()

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(title__icontains=q)

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
        "pageTitle": "لیست پک‌های تبلیغاتی",
        "newUrl": reverse("app_promotion:promotion_create"),
        "searchUrl": reverse("app_promotion:promotion_index"),
        "searchText": q,
        "searchSort": sort,
        "searchCount": count,
        "sortWithActiveDeactive": 1,
        "all": page,
        "total": qs.count(),
    }
    return render(request, "pages/promotion/all_promotions.html", {"data": data})


# ═══════════════════════════════════════════════════════════
# PROMOTION CREATE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def promotion_create(request):
    RequiredAccess(request, "PromotionCreate")

    if request.method == "POST":
        cleaned, errors = promotion__clean__data(request.POST)

        if errors:
            for err in errors:
                _msg(request, messages.ERROR, err)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد پک تبلیغاتی",
                    "backUrl": reverse("app_promotion:promotion_index"),
                    "storeUrl": reverse("app_promotion:promotion_create"),
                    "items": promotion__form(raw_data=request.POST),
                }
            })

        try:
            promotion = promotion__store(cleaned)
        except Exception:
            logger.exception("promotion_create failed")
            _msg(request, messages.ERROR, "خطا در ذخیره پک")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ایجاد پک تبلیغاتی",
                    "backUrl": reverse("app_promotion:promotion_index"),
                    "storeUrl": reverse("app_promotion:promotion_create"),
                    "items": promotion__form(raw_data=request.POST),
                }
            })

        _msg(request, messages.SUCCESS, "پک تبلیغاتی ایجاد شد. اکنون آیتم‌ها را اضافه کنید.")
        return redirect("app_promotion:promotion_detail", id=promotion.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ایجاد پک تبلیغاتی",
            "backUrl": reverse("app_promotion:promotion_index"),
            "storeUrl": reverse("app_promotion:promotion_create"),
            "items": promotion__form(),
        }
    })


# ═══════════════════════════════════════════════════════════
# PROMOTION UPDATE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def promotion_update(request, id):
    RequiredAccess(request, "PromotionUpdate")
    promotion = get_object_or_404(Promotion, id=id)

    if request.method == "POST":
        cleaned, errors = promotion__clean__data(request.POST)

        if errors:
            for err in errors:
                _msg(request, messages.ERROR, err)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ویرایش پک تبلیغاتی",
                    "backUrl": reverse("app_promotion:promotion_index"),
                    "storeUrl": reverse("app_promotion:promotion_update", kwargs={"id": promotion.id}),
                    "items": promotion__form(promotion=promotion, raw_data=request.POST),
                }
            })

        try:
            promotion__store(cleaned, item=promotion)
        except Exception:
            logger.exception("promotion_update failed id=%s", id)
            _msg(request, messages.ERROR, "خطا در ذخیره پک")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": "ویرایش پک تبلیغاتی",
                    "backUrl": reverse("app_promotion:promotion_index"),
                    "storeUrl": reverse("app_promotion:promotion_update", kwargs={"id": promotion.id}),
                    "items": promotion__form(promotion=promotion, raw_data=request.POST),
                }
            })

        _msg(request, messages.SUCCESS, "پک تبلیغاتی به‌روزرسانی شد")
        return redirect("app_promotion:promotion_detail", id=promotion.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": "ویرایش پک تبلیغاتی",
            "backUrl": reverse("app_promotion:promotion_index"),
            "storeUrl": reverse("app_promotion:promotion_update", kwargs={"id": promotion.id}),
            "items": promotion__form(promotion=promotion),
        }
    })


# ═══════════════════════════════════════════════════════════
# PROMOTION DELETE
# ═══════════════════════════════════════════════════════════
@is_admin_required
def promotion_delete(request, id):
    RequiredAccess(request, "PromotionDelete")
    if request.method != "POST":
        _msg(request, messages.ERROR, "درخواست نامعتبر")
        return redirect("app_promotion:promotion_index")

    promotion = get_object_or_404(Promotion, id=id)

    if promotion.promotion_items_relation.exists():
        _msg(request, messages.ERROR, "این پک دارای آیتم است. ابتدا آیتم‌ها را حذف کنید.")
        return redirect_back(request)

    if promotion.promotion_orders_relation.exists():
        _msg(request, messages.ERROR, "این پک دارای سفارش است و قابل حذف نیست.")
        return redirect_back(request)

    promotion.delete()
    _msg(request, messages.SUCCESS, "پک تبلیغاتی حذف شد")
    return redirect("app_promotion:promotion_index")


# ═══════════════════════════════════════════════════════════
# PROMOTION DETAIL — نمایش پک + آیتم‌ها + فرم افزودن
# ═══════════════════════════════════════════════════════════
@is_admin_required
def promotion_detail(request, id):
    RequiredAccess(request, "PromotionRead")
    promotion = get_object_or_404(Promotion, id=id)
    items = promotion.promotion_items_relation.order_by("-created_at")
    return render(request, "pages/promotion/promotion_detail.html", {
        "promotion": promotion,
        "items": items,
    })


# ═══════════════════════════════════════════════════════════
# PROMOTION ITEM — Create
# ═══════════════════════════════════════════════════════════
@is_admin_required
def promotion_item_create(request, id):
    RequiredAccess(request, "PromotionUpdate")
    promotion = get_object_or_404(Promotion, id=id)

    if request.method == "POST":
        cleaned, errors = promotion_item__clean__data(request.POST)

        if errors:
            for err in errors:
                _msg(request, messages.ERROR, err)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"افزودن آیتم به «{promotion.title}»",
                    "backUrl": reverse("app_promotion:promotion_detail", kwargs={"id": promotion.id}),
                    "storeUrl": reverse("app_promotion:promotion_item_create", kwargs={"id": promotion.id}),
                    "items": promotion_item__form(raw_data=request.POST),
                }
            })

        try:
            promotion_item__store(request, promotion, cleaned)
        except Exception:
            logger.exception("promotion_item_create failed promotion=%s", id)
            _msg(request, messages.ERROR, "خطا در ذخیره آیتم")
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"افزودن آیتم به «{promotion.title}»",
                    "backUrl": reverse("app_promotion:promotion_detail", kwargs={"id": promotion.id}),
                    "storeUrl": reverse("app_promotion:promotion_item_create", kwargs={"id": promotion.id}),
                    "items": promotion_item__form(raw_data=request.POST),
                }
            })

        _msg(request, messages.SUCCESS, "آیتم با موفقیت اضافه شد")
        return redirect("app_promotion:promotion_detail", id=promotion.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": f"افزودن آیتم به «{promotion.title}»",
            "backUrl": reverse("app_promotion:promotion_detail", kwargs={"id": promotion.id}),
            "storeUrl": reverse("app_promotion:promotion_item_create", kwargs={"id": promotion.id}),
            "items": promotion_item__form(),
        }
    })


# ═══════════════════════════════════════════════════════════
# PROMOTION ITEM — Update
# ═══════════════════════════════════════════════════════════
@is_admin_required
def promotion_item_update(request, id, item_id):
    RequiredAccess(request, "PromotionUpdate")
    promotion = get_object_or_404(Promotion, id=id)
    item = get_object_or_404(PromotionItem, id=item_id, promotion=promotion)

    if request.method == "POST":
        cleaned, errors = promotion_item__clean__data(request.POST)

        if errors:
            for err in errors:
                _msg(request, messages.ERROR, err)
            return render(request, "pages/form.html", {
                "data": {
                    "pageTitle": f"ویرایش آیتم «{item.title}»",
                    "backUrl": reverse("app_promotion:promotion_detail", kwargs={"id": promotion.id}),
                    "storeUrl": reverse("app_promotion:promotion_item_update", kwargs={"id": promotion.id, "item_id": item.id}),
                    "items": promotion_item__form(item=item, raw_data=request.POST),
                }
            })

        try:
            promotion_item__store(request, promotion, cleaned, item=item)
        except Exception:
            logger.exception("promotion_item_update failed item=%s", item_id)
            _msg(request, messages.ERROR, "خطا در ذخیره آیتم")
            return redirect("app_promotion:promotion_detail", id=promotion.id)

        _msg(request, messages.SUCCESS, "آیتم به‌روزرسانی شد")
        return redirect("app_promotion:promotion_detail", id=promotion.id)

    return render(request, "pages/form.html", {
        "data": {
            "pageTitle": f"ویرایش آیتم «{item.title}»",
            "backUrl": reverse("app_promotion:promotion_detail", kwargs={"id": promotion.id}),
            "storeUrl": reverse("app_promotion:promotion_item_update", kwargs={"id": promotion.id, "item_id": item.id}),
            "items": promotion_item__form(item=item),
        }
    })


# ═══════════════════════════════════════════════════════════
# PROMOTION ITEM — Delete
# ═══════════════════════════════════════════════════════════
@is_admin_required
def promotion_item_delete(request, id, item_id):
    RequiredAccess(request, "PromotionUpdate")
    if request.method != "POST":
        _msg(request, messages.ERROR, "درخواست نامعتبر")
        return redirect("app_promotion:promotion_detail", id=id)

    promotion = get_object_or_404(Promotion, id=id)
    item = get_object_or_404(PromotionItem, id=item_id, promotion=promotion)

    promotion_item__delete(item)
    _msg(request, messages.SUCCESS, "آیتم حذف شد")
    return redirect("app_promotion:promotion_detail", id=id)