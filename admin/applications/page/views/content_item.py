import json

from django.contrib.auth.decorators import permission_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _

from applications.core.requiredAccess import RequiredAccess
from applications.core.decorators import is_admin_required
from applications.page.models import Page, PageContentItem


@is_admin_required
def page_content_items(request, page_id):
    RequiredAccess(request, 'PageRead')
    
    page = get_object_or_404(Page, id=page_id)
    items = page.content_items.all().order_by("kind", "order")

    context = {
        "page": page,
        "items": items,
        "data": {"pageTitle": f"مدیریت محتوای صفحه: {page.title}"},
    }
    return render(request, "pages/page/content_items.html", context)


@is_admin_required
def content_item_create(request, page_id):
    RequiredAccess(request, 'PageRead')
    
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    page = get_object_or_404(Page, id=page_id)

    kind = request.POST.get("kind")
    title = (request.POST.get("title") or "").strip()
    body = request.POST.get("body") or ""
    order_raw = request.POST.get("order") or 0
    extra_raw = request.POST.get("extra", "{}")

    if not kind:
        return JsonResponse({"status": "error", "message": _("نوع آیتم الزامی است")}, status=400)
    if not title:
        return JsonResponse({"status": "error", "message": _("عنوان الزامی است")}, status=400)

    try:
        order = int(order_raw)
    except ValueError:
        order = 0

    try:
        extra = json.loads(extra_raw) if extra_raw else {}
    except json.JSONDecodeError:
        extra = {}

    try:
        item = PageContentItem.objects.create(
            page=page, kind=kind, title=title, body=body,
            order=order, extra=extra,
        )
    except IntegrityError:
        return JsonResponse(
            {"status": "error", "message": _("ترتیب وارد شده تکراری است؛ عدد دیگری انتخاب کنید")},
            status=400,
        )

    return JsonResponse({
        "status": "success",
        "message": _("آیتم با موفقیت ایجاد شد"),
        "item": {
            "id": item.id, "kind": item.kind, "title": item.title,
            "body": item.body, "order": item.order, "extra": item.extra,
        },
    })


@is_admin_required
def content_item_edit(request, item_id):
    RequiredAccess(request, 'PageRead')
    
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    item = get_object_or_404(PageContentItem, id=item_id)

    if request.POST.get("kind"):
        item.kind = request.POST.get("kind")
    if request.POST.get("title") is not None:
        item.title = request.POST.get("title").strip()
    if request.POST.get("body") is not None:
        item.body = request.POST.get("body")
    if request.POST.get("order") is not None:
        try:
            item.order = int(request.POST.get("order"))
        except ValueError:
            pass
    extra_raw = request.POST.get("extra")
    if extra_raw:
        try:
            item.extra = json.loads(extra_raw)
        except json.JSONDecodeError:
            item.extra = {}

    try:
        item.save()
    except IntegrityError:
        return JsonResponse(
            {"status": "error", "message": _("ترتیب وارد شده تکراری است؛ عدد دیگری انتخاب کنید")},
            status=400,
        )

    return JsonResponse({
        "status": "success",
        "message": _("آیتم با موفقیت ویرایش شد"),
        "item": {
            "id": item.id, "kind": item.kind, "title": item.title,
            "body": item.body, "order": item.order, "extra": item.extra,
        },
    })


@is_admin_required
def content_item_delete(request, item_id):
    RequiredAccess(request, 'PageRead')
    
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    item = get_object_or_404(PageContentItem, id=item_id)
    item.delete()
    return JsonResponse({"status": "success", "message": _("آیتم با موفقیت حذف شد")})


@is_admin_required
def content_item_reorder(request):
    RequiredAccess(request, 'PageRead')
    
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "داده نامعتبر"}, status=400)

    # مرحله ۱: انتقال موقت به order های منفی برای جلوگیری از تعارض unique
    items = data.get("items", [])
    for item_data in items:
        item_id = item_data.get("id")
        if item_id:
            PageContentItem.objects.filter(id=item_id).update(order=-1)

    # مرحله ۲: اعمال ترتیب جدید
    for item_data in items:
        item_id = item_data.get("id")
        order = item_data.get("order")
        if item_id and order is not None:
            PageContentItem.objects.filter(id=item_id).update(order=order)

    return JsonResponse({"status": "success", "message": _("ترتیب آیتم‌ها بروزرسانی شد")})


@is_admin_required
def get_content_item_data(request, item_id):
    item = get_object_or_404(PageContentItem, id=item_id)
    return JsonResponse({
        "status": "success",
        "item": {
            "id": item.id, "kind": item.kind, "title": item.title,
            "body": item.body, "order": item.order, "extra": item.extra,
        },
    })