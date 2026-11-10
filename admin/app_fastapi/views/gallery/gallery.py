# app_fastapi/views/gallery/gallery.py

import logging

from asgiref.sync import sync_to_async
from fastapi import APIRouter, Depends, File, UploadFile
from django.db import transaction
from django.db.models import Count

from applications.gallery.models import Gallery, GalleryLike
from applications.user.models import User
from app_fastapi.conf.dependencyRequest import DependencyDataRequest
from app_fastapi.conf.fileManager import get_file_url, handle_save_file
from app_fastapi.conf.response import error_response, success_response
from app_fastapi.views.user.helper import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


# ═══════════════════════════════════════════════════════════
# Serializers
# ═══════════════════════════════════════════════════════════
def _serialize_gallery(g: Gallery, current_user_id: int, *, full: bool = False) -> dict:
    # محاسبه تعداد لایک‌ها و اینکه آیا کاربر فعلی لایک کرده است یا نه
    likes_count = g.likes.count()
    is_liked = g.likes.filter(user_id=current_user_id).exists()

    data = {
        "id": g.id,
        "photo": get_file_url(g.photo) if g.photo else None,
        "caption": g.caption,
        "location": g.location,
        "status": g.status,
        "status_display": g.get_status_display(),
        "created_at": g.created_at.isoformat() if g.created_at else None,
        "likes_count": likes_count,
        "is_liked_by_me": is_liked,
    }

    if full:
        data["user"] = {
            "id": g.user.id,
            "name": g.user.full_name,
            "mobile": g.user.mobile,
        }
    return data


# ═══════════════════════════════════════════════════════════
# ۱. آپلود (ایجاد پست گالری)
# ═══════════════════════════════════════════════════════════
@router.post("/create/")
async def create_gallery_endpoint(
    photo: UploadFile = File(...),
    form: dict = Depends(DependencyDataRequest),
    user: User = Depends(get_current_user),
):
    if not photo:
        return error_response("تصویر الزامی است")

    try:
        saved_name = await sync_to_async(handle_save_file)(photo)
    except Exception:
        logger.exception("photo save failed")
        return error_response("خطا در ذخیره تصویر")

    try:
        gallery = await _create_gallery_db(
            user_id=user.id,
            photo_name=saved_name,
            caption=form.get("caption"),
            location=form.get("location")
        )
        return success_response("تصویر با موفقیت ثبت شد و در انتظار تایید است", gallery)
    except Exception:
        logger.exception("create_gallery failed")
        return error_response("خطا در ثبت تصویر")


@sync_to_async
def _create_gallery_db(user_id, photo_name, caption, location):
    g = Gallery.objects.create(
        user_id=user_id,
        photo=photo_name,
        caption=caption,
        location=location,
        status=Gallery.Status.PENDING  # به صورت پیش‌فرض در انتظار تایید
    )
    return _serialize_gallery(g, user_id, full=True)


# ═══════════════════════════════════════════════════════════
# ۲. حذف پست گالری
# ═══════════════════════════════════════════════════════════
@router.delete("/{gallery_id}/")
async def delete_gallery_endpoint(
    gallery_id: int,
    user: User = Depends(get_current_user),
):
    try:
        result = await _delete_gallery_db(gallery_id, user.id)
        if result.get("error"):
            return error_response(result["error"], status_code=400)
        return success_response("پست گالری با موفقیت حذف شد", {})
    except Exception:
        logger.exception("delete_gallery failed")
        return error_response("خطا در حذف تصویر")


@sync_to_async
def _delete_gallery_db(gallery_id, user_id):
    with transaction.atomic():
        g = Gallery.objects.select_for_update().filter(id=gallery_id).first()
        if not g:
            return {"error": "پست گالری یافت نشد"}
        if g.user_id != user_id:
            return {"error": "شما مجاز به حذف این پست نیستید"}

        # (اختیاری) حذف فیزیکی فایل از سرور
        # if g.photo:
        #     g.photo.delete(save=False)

        g.delete()
        return {"success": True}


# ═══════════════════════════════════════════════════════════
# ۳. لیست گالری (من، محبوب‌ترین، جدیدترین)
# ═══════════════════════════════════════════════════════════
@router.get("/list/")
async def list_galleries(
    filter_type: str = "newest", # گزینه‌ها: mine, newest, popular
    user: User = Depends(get_current_user),
):
    data = await _list_galleries_db(user.id, filter_type)
    return success_response("لیست تصاویر", data)


@sync_to_async
def _list_galleries_db(user_id, filter_type):
    qs = Gallery.objects.select_related("user")

    if filter_type == "mine":
        # فقط پست‌های خود کاربر (چه تایید شده چه در انتظار)
        qs = qs.filter(user_id=user_id)
    else:
        # برای دیگران، فقط پست‌های تایید شده نمایش داده می‌شوند
        qs = qs.filter(status=Gallery.Status.APPROVED)

    # اعمال فیلترها
    if filter_type == "popular":
        # مرتب‌سازی بر اساس بیشترین لایک
        qs = qs.annotate(likes_count=Count('likes')).order_by('-likes_count', '-created_at')
    else:
        # پیش‌فرض (newest): مرتب‌سازی بر اساس جدیدترین
        qs = qs.order_by('-created_at')

    return [_serialize_gallery(g, user_id, full=True) for g in qs]


# ═══════════════════════════════════════════════════════════
# ۴. لایک و دیسلایک (Toggle)
# ═══════════════════════════════════════════════════════════
@router.post("/{gallery_id}/like/")
async def toggle_like_endpoint(
    gallery_id: int,
    user: User = Depends(get_current_user),
):
    try:
        result = await _toggle_like_db(gallery_id, user.id)
        if result.get("error"):
            return error_response(result["error"], status_code=400)
        
        msg = "لایک شد" if result["is_liked"] else "لایک برداشته شد"
        return success_response(msg, result)
    except Exception:
        logger.exception("toggle_like failed")
        return error_response("خطا در ثبت لایک")


@sync_to_async
def _toggle_like_db(gallery_id, user_id):
    with transaction.atomic():
        g = Gallery.objects.filter(id=gallery_id).first()
        if not g:
            return {"error": "پست گالری یافت نشد"}
        
        if g.status != Gallery.Status.APPROVED:
            return {"error": "امکان لایک این پست وجود ندارد"}

        if g.user_id == user_id:
            return {"error": "شما نمی‌توانید پست خودتان را لایک کنید"}

        # بررسی وجود لایک
        like = GalleryLike.objects.filter(gallery_id=gallery_id, user_id=user_id).first()
        
        if like:
            # اگر لایک کرده بود، دیسلایک (حذف) می‌شود
            like.delete()
            is_liked = False
        else:
            # اگر لایک نکرده بود، لایک می‌شود
            GalleryLike.objects.create(gallery_id=gallery_id, user_id=user_id)
            is_liked = True

        return {
            "is_liked": is_liked,
            "likes_count": GalleryLike.objects.filter(gallery_id=gallery_id).count()
        }


# ═══════════════════════════════════════════════════════════
# ۵. جزئیات یک تصویر
# ═══════════════════════════════════════════════════════════
@router.get("/{gallery_id}/")
async def get_gallery_detail(
    gallery_id: int,
    user: User = Depends(get_current_user),
):
    data = await _get_gallery_db(gallery_id, user.id)
    if not data:
        return error_response("تصویر یافت نشد یا دسترسی ندارید", status_code=404)
    return success_response("جزئیات تصویر", data)

@sync_to_async
def _get_gallery_db(gallery_id, user_id):
    g = Gallery.objects.select_related("user").filter(id=gallery_id).first()
    if not g:
        return None
    
    # اگر عکس تایید نشده باشد، فقط صاحبش می‌تواند ببیند
    if g.status != Gallery.Status.APPROVED and g.user_id != user_id:
        return None
        
    return _serialize_gallery(g, user_id, full=True)