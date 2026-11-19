# Path: applications/core/processors.py

# applications/core/context_processors.py

import datetime
import logging

from django.core.cache import cache
from django.urls import NoReverseMatch, reverse

from applications.role.models import Actions, Role
from applications.setting.models import Setting
from applications.core.keyValue import settingPhoto

logger = logging.getLogger(__name__)

# TTL کش (ثانیه) — ۶۰ ثانیه کافی است، ادمین‌ها نیازی به real-time ندارند
_NOTIF_CACHE_TTL = 60


# ═══════════════════════════════════════════════════════════
# adminAccess — بدون تغییر
# ═══════════════════════════════════════════════════════════
def adminAccess(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"adminAccess": []}

    data = set()
    if user.nature == "manager":
        role_ids = user.role_ids or []
        if not role_ids:
            return {"adminAccess": []}

        roles = Role.objects.filter(pk__in=role_ids).values_list("action_ids", flat=True)
        all_action_ids = set()
        for ids in roles:
            if isinstance(ids, list):
                all_action_ids.update(ids)

        if not all_action_ids:
            return {"adminAccess": []}

        actions = Actions.objects.filter(pk__in=all_action_ids).values_list("action", flat=True)
        data.update(actions)

    return {"adminAccess": list(data)}


def checkActiveModule(request):
    return {"checkActiveModule": []}


def initAppSetting(request):
    data = {}
    for item in Setting.objects.all():
        data[item.key] = (
            str(item.value_file) if item.key in settingPhoto() else str(item.value_text)
        )
    data["date"] = datetime.datetime.now().year
    return {"initAppSetting": data}


def sitSettings(request):
    data = {}
    for item in Setting.objects.all():
        data[item.key] = (
            str(item.value_file) if item.key in settingPhoto() else str(item.value_text)
        )
    data["date"] = datetime.datetime.now().year
    return {"sitSettings": data}


# ═══════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════
def _safe_reverse(*names, query=""):
    """اولین URL name که resolve شد را با query برمی‌گرداند."""
    for name in names:
        try:
            return reverse(name) + (query or "")
        except NoReverseMatch:
            continue
    return None


def _compute_notifications():
    """محاسبه‌ی نوتیفیکیشن‌های pending. یک بار در ۶۰ ثانیه."""
    items = []

    # ۱) سفارشات هدیه
    try:
        from applications.gift.models import GiftOrder
        n = GiftOrder.objects.filter(status="pending").count()
        url = _safe_reverse("app_gift:order_index", query="?filter=pending")
        if n and url:
            items.append({
                "key": "gift_orders", "label": "سفارش هدیه در انتظار",
                "count": n, "icon": "fe-gift", "color": "warning", "url": url,
            })
    except Exception:
        pass

    # ۲) سفارشات اقلام تبلیغاتی
    try:
        from applications.promotion.models import PromotionOrder
        n = PromotionOrder.objects.filter(status="pending").count()
        url = _safe_reverse("app_promotion:order_index", query="?filter=pending")
        if n and url:
            items.append({
                "key": "promotion_orders", "label": "سفارش پک تبلیغاتی در انتظار",
                "count": n, "icon": "fe-package", "color": "info", "url": url,
            })
    except Exception:
        pass

    # ۳) پروژه‌ها
    try:
        from applications.project.models import Project
        n = Project.objects.filter(status="pending").count()
        url = _safe_reverse(
            "app_project:project_index", "project:project_index",
            query="?status=pending",
        )
        if n and url:
            items.append({
                "key": "projects", "label": "پروژه در انتظار تأیید",
                "count": n, "icon": "fe-briefcase", "color": "primary", "url": url,
            })
    except Exception:
        pass

    # ۴) فاکتورها
    try:
        from applications.factor.models import Factor
        n = Factor.objects.filter(status="pending").count()
        url = _safe_reverse(
            "app_factor:factor_index", "factor:factor_index",
            query="?status=pending",
        )
        if n and url:
            items.append({
                "key": "factors", "label": "فاکتور در انتظار تأیید",
                "count": n, "icon": "fe-file-text", "color": "success", "url": url,
            })
    except Exception:
        pass

    # ۵) درخواست‌های بازدید
    try:
        from applications.visit.models import RequestVisit
        n = RequestVisit.objects.filter(status="pending").count()
        url = _safe_reverse(
            "app_visit:request_index", "visit:request_index",
            query="?status=pending",
        )
        if n and url:
            items.append({
                "key": "visit_requests", "label": "درخواست بازدید در انتظار",
                "count": n, "icon": "fe-calendar", "color": "danger", "url": url,
            })
    except Exception:
        pass

    # ۶) پشتیبانی — open + in_progress
    try:
        from applications.support.models import Support
        n = Support.objects.filter(status__in=["open", "in_progress"]).count()
        url = _safe_reverse(
            "app_support:support_index", "support:support_index",
            query="?status=open",
        )
        if n and url:
            items.append({
                "key": "support", "label": "تیکت پشتیبانی باز",
                "count": n, "icon": "fe-life-buoy", "color": "info", "url": url,
            })
    except Exception:
        pass

    # ۷) گالری
    try:
        from applications.gallery.models import Gallery
        n = Gallery.objects.filter(status="pending").count()
        url = _safe_reverse(
            "app_gallery:gallery_index", "gallery:gallery_index",
            query="?status=pending",
        )
        if n and url:
            items.append({
                "key": "gallery", "label": "پست گالری در انتظار",
                "count": n, "icon": "fe-image", "color": "warning", "url": url,
            })
    except Exception:
        pass

    # ۸) FAQ غیرفعال
    try:
        from applications.faq.models import FAQ
        n = FAQ.objects.filter(is_active=False).count()
        url = _safe_reverse(
            "app_faq:faq_index", "faq:faq_index",
            query="?is_active=0",
        )
        if n and url:
            items.append({
                "key": "faqs", "label": "سوال FAQ در انتظار تأیید",
                "count": n, "icon": "fe-help-circle", "color": "primary", "url": url,
            })
    except Exception:
        pass

    return items


# ═══════════════════════════════════════════════════════════
# adminNotifications — با کش ۶۰ ثانیه‌ای
# ═══════════════════════════════════════════════════════════
def adminNotifications(request):
    """نوتیفیکیشن‌های pending — کش‌شده per-user برای کاهش DB load."""
    empty = {"all": 0, "items": []}

    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"adminNotifications": empty}

    cache_key = f"admin_notif_v1_u{user.id}"

    # ─── تلاش برای خواندن از کش ──────────────────────
    try:
        cached = cache.get(cache_key)
        if cached is not None:
            return {"adminNotifications": cached}
    except Exception:
        cached = None

    # ─── محاسبه (فقط اگر کش نداشتیم) ─────────────────
    try:
        items = _compute_notifications()
        total = sum(i["count"] for i in items)
        result = {"all": total, "items": items}
    except Exception:
        logger.exception("adminNotifications computation failed")
        result = empty

    # ─── ذخیره در کش ─────────────────────────────────
    try:
        cache.set(cache_key, result, _NOTIF_CACHE_TTL)
    except Exception:
        pass

    return {"adminNotifications": result}