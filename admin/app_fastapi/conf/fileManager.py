#  admin/app_fastapi/conf/fileManager.py

import mimetypes
import shutil
from typing import List, Optional
from fastapi import UploadFile, Request
from asgiref.sync import sync_to_async
from django.db import transaction
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from PIL import Image
import datetime
from uuid import uuid4
import os

import filetype


MEDIA_ROOT = "static_media"


def custom_filename(ext: str) -> str:
    return f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}_{uuid4().hex}{ext}"


def handle_save_file(file: UploadFile, max_width: int = 1200, quality: int = 80) -> str:
    """
    ذخیره فایل با حفظ نام اصلی.
    - اگر تصویر بود: resize و تبدیل به WebP
    - اگر ویدیو یا فایل دیگر بود: مستقیم ذخیره
    برمی‌گرداند مسیر ذخیره شده
    """
    import re
    
    original_ext = os.path.splitext(file.filename)[1].lower()
    original_name = os.path.splitext(os.path.basename(file.filename))[0]
    
    # پاکسازی نام فایل از کاراکترهای غیرمجاز (حفظ حروف فارسی، انگلیسی، اعداد، خط تیره و آندرلاین)
    safe_name = re.sub(r'[^\w\-\u0600-\u06FF]', '_', original_name)
    # جلوگیری از اسم‌های خیلی طولانی
    safe_name = safe_name[:50] 

    # پیشوند یکتا (تاریخ و ساعت) برای جلوگیری از تداخل فایل‌های هم‌نام
    unique_prefix = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    date_folder = datetime.datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(MEDIA_ROOT, date_folder)
    os.makedirs(path, exist_ok=True)

    # چک تصویر
    if original_ext in [".png", ".jpg", ".jpeg", ".jfif", ".gif", ".webp"]:
        image = Image.open(file.file)
        if image.width > max_width:
            ratio = max_width / float(image.width)
            height = int(image.height * ratio)
            image = image.resize((max_width, height), Image.Resampling.LANCZOS)

        buffer = BytesIO()
        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            image.save(buffer, format="WEBP", quality=quality, lossless=False, method=6)
        else:
            image = image.convert("RGB")
            image.save(buffer, format="WEBP", quality=quality, method=6)
        buffer.seek(0)

        # اسم جدید با پسوند webp
        filename = f"{unique_prefix}_{safe_name}.webp"
        final_path = os.path.join(path, filename)
        with open(final_path, "wb") as f:
            f.write(buffer.read())
        buffer.close()
        return f"{date_folder}/{filename}"

    # ویدیو یا فایل دیگه (مثل PDF)
    else:
        # اسم جدید با پسوند اصلی
        filename = f"{unique_prefix}_{safe_name}{original_ext}"
        final_path = os.path.join(path, filename)
        # مستقیم کپی از UploadFile
        with open(final_path, "wb") as out_file:
            shutil.copyfileobj(file.file, out_file)
        return f"{date_folder}/{filename}"

###
###
###
###
async def fastapi_uploadfile(upload_file: Optional[UploadFile], field_name: str) -> Optional[InMemoryUploadedFile]:
    """
    تبدیل FastAPI UploadFile به InMemoryUploadedFile قابل استفاده در Django
    """
    if not upload_file:
        return None

    file_content = await upload_file.read()
    return InMemoryUploadedFile(
        BytesIO(file_content),
        field_name=field_name,
        name=upload_file.filename,
        content_type=upload_file.content_type,
        size=len(file_content),
        charset=None
    )



###
###
###
###
def get_real_file_type_fastapi(file: UploadFile) -> dict:
    """
    تشخیص نوع واقعی فایل (فقط تصویر و ویدیو).
    اگر قابل تشخیص نبود، None برمی‌گرداند.
    """
    # خواندن بایت‌های بیشتر برای ویدیو
    content = file.file.read(4096)
    file.file.seek(0)

    kind = filetype.guess(content)
    if kind is not None:
        if kind.mime.startswith("image/") or kind.mime.startswith("video/"):
            return {"extension": f".{kind.extension}", "mime_type": kind.mime}

    # fallback با mimetypes از filename
    mime = mimetypes.guess_type(file.filename)[0]
    if mime and (mime.startswith("image/") or mime.startswith("video/")):
        ext =  file.filename.split(".")[-1]
        return {"extension": ext, "mime_type": mime}

    return {"extension": None, "mime_type": None}



def get_real_file_type(file) -> dict:
    """
    تشخیص نوع واقعی فایل (image / video)
    سازگار با Django UploadedFile
    """

    # خواندن بایت‌ها
    content = file.read(4096)
    file.seek(0)

    kind = filetype.guess(content)
    if kind and (kind.mime.startswith("image/") or kind.mime.startswith("video/")):
        return {
            "extension": f".{kind.extension}",
            "mime_type": kind.mime
        }

    # fallback با نام فایل (Django)
    mime, _ = mimetypes.guess_type(file.name)
    if mime and (mime.startswith("image/") or mime.startswith("video/")):
        ext = file.name.split(".")[-1]
        return {
            "extension": f".{ext}",
            "mime_type": mime
        }

    return {"extension": None, "mime_type": None}



def get_file_size(upload_file) -> int:
    """حجم واقعی UploadFile (FastAPI) را برمی‌گرداند."""
    try:
        upload_file.file.seek(0, os.SEEK_END)
        size = upload_file.file.tell()
        upload_file.file.seek(0)
        return size
    except Exception:
        return 0


def get_file_url(file_field):
    """آدرس امن فایل — چه FieldFile باشد چه رشته."""
    if not file_field:
        return None
    if hasattr(file_field, "url"):
        try:
            return file_field.url
        except Exception:
            return None
    return str(file_field)
