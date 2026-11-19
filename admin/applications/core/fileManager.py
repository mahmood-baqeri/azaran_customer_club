# Path: applications/core/fileManager.py

# applications/core/fileManager.py

import os
import shutil
import datetime
import tempfile
from io import BytesIO
from pathlib import Path

from PIL import Image

from django.conf import settings
from django.db import models


# ═══════════════════════════════════════════════════════════
# helpers
# ═══════════════════════════════════════════════════════════
def _media_root() -> Path:
    """MEDIA_ROOT به‌صورت Path — مستقل از نوع تنظیمات (str یا Path)."""
    return Path(str(settings.MEDIA_ROOT))


def _date_folder() -> str:
    now = datetime.datetime.now()
    return f"{now.year}-{now.month}-{now.day}"


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def customFileName() -> str:
    now = datetime.datetime.now()
    return f"{now.hour}-{now.minute}-{now.second}-{now.microsecond}"


# ═══════════════════════════════════════════════════════════
# Upload / Delete
# ═══════════════════════════════════════════════════════════
def uploadFile(file) -> str:
    """فایل را در MEDIA_ROOT/<date>/<uuid><ext> ذخیره می‌کند. مسیر نسبی برمی‌گرداند."""
    date_folder = _date_folder()
    target_dir = _ensure_dir(_media_root() / date_folder)

    ext = os.path.splitext(file.name)[1]
    filename = f"{customFileName()}{ext}"
    target_path = target_dir / filename

    with open(target_path, "wb+") as dest:
        shutil.copyfileobj(file, dest)

    return f"{date_folder}/{filename}"


def uploadFileWithPath(file, path: str) -> str:
    """ذخیره فایل در MEDIA_ROOT/<path>/ با نام تاریخ شمسی."""
    from persiantools.jdatetime import JalaliDate

    target_dir = _ensure_dir(_media_root() / path)

    today = datetime.datetime.now()
    jalali = JalaliDate(today.date()).strftime("%Y-%m-%d")
    name = f"{jalali}-{today.hour}-{today.minute}{os.path.splitext(file.name)[1]}"

    target_path = target_dir / name
    with open(target_path, "wb+") as dest:
        shutil.copyfileobj(file, dest)

    return f"{path}/{name}"


def uploadExcel(file) -> None:
    """ذخیره اکسل در MEDIA_ROOT/perferazhExcel/<date>.xlsx."""
    from persiantools.jdatetime import JalaliDate

    today = datetime.datetime.now()
    jalali = JalaliDate(today.date()).strftime("%Y-%m-%d")
    name = f"{jalali}-{today.hour}-{today.minute}.xlsx"

    target_dir = _ensure_dir(_media_root() / "perferazhExcel")
    with open(target_dir / name, "wb+") as dest:
        for chunk in file.chunks():
            dest.write(chunk)


def uploadFileFromModel(instance, filename) -> str:
    """callable برای upload_to — نام یونیک + پوشه‌ی تاریخ."""
    ext = filename.rsplit(".", 1)[-1]
    date_folder = _date_folder()
    return f"{date_folder}/{customFileName()}.{ext}"


def deleteFile(path: str) -> None:
    """حذف فایل با مسیر نسبی (مثل '2025-1-15/abc.jpg')."""
    if not path:
        return

    # اگر URL کامل آمد، نرمال کن
    path = str(path)
    media_url = (settings.MEDIA_URL or "/media/")
    if path.startswith(media_url):
        path = path[len(media_url):]
    if path.startswith("/"):
        path = path[1:]

    full = _media_root() / path
    if full.is_file():
        try:
            full.unlink()
        except OSError:
            pass


def getFilename(file):
    return file.name


def getMimetype(file):
    return file.content_type


def checkFileExtension(file) -> int:
    """0=عکس، 1=ویدیو، 2=صوت، 3=نامشخص."""
    if not file:
        return 3
    ext = os.path.splitext(file.name)[1].lower()
    if ext in ('.png', '.gif', '.jpg', '.jpeg', '.jfif', '.pjpeg', '.pjp', '.svg', '.webp'):
        return 0
    if ext in ('.mp4', '.wmv', '.mov', '.flv', '.webm', '.avi', '.kmv', '.3gp'):
        return 1
    if ext in ('.mp3', '.wma', '.alag', '.aac', '.flac', '.aiff', '.wav', '.ogg'):
        return 2
    return 3


def detect_file_type(file) -> str:
    kind = checkFileExtension(file)
    return {0: "Image", 1: "Video", 2: "Audio"}.get(kind, "Unknown")


def uploadFileFastAPI(file) -> str:
    """همان uploadFile، برای UploadFile فست‌API."""
    date_folder = _date_folder()
    target_dir = _ensure_dir(_media_root() / date_folder)

    filename = f"{customFileName()}{os.path.splitext(file.filename)[1]}"
    target_path = target_dir / filename

    with open(target_path, "wb+") as dest:
        shutil.copyfileobj(file.file, dest)

    return f"{date_folder}/{filename}"


# ═══════════════════════════════════════════════════════════
# Image → WebP (با حفظ شفافیت)
# ═══════════════════════════════════════════════════════════
def process_image_with_transparency(file, max_width=1200, quality=80) -> str:
    """تصویر → WebP، محدود به max_width، با حفظ شفافیت."""
    date_folder = _date_folder()
    target_dir = _ensure_dir(_media_root() / date_folder)

    img = Image.open(file)
    if img.width > max_width:
        ratio = max_width / float(img.width)
        img = img.resize((max_width, int(img.height * ratio)),
                         Image.Resampling.LANCZOS)

    buffer = BytesIO()
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        img.save(buffer, format="WEBP", quality=quality, lossless=False, method=6)
    else:
        img.convert("RGB").save(buffer, format="WEBP", quality=quality, method=6)
    buffer.seek(0)

    filename = f"{customFileName()}.webp"
    with open(target_dir / filename, "wb") as out:
        out.write(buffer.read())
    buffer.close()

    return f"{date_folder}/{filename}"


# ═══════════════════════════════════════════════════════════
# Mixins
# ═══════════════════════════════════════════════════════════
class ImageProcessingMixin(models.Model):
    """تبدیل خودکار ImageFieldها به WebP هنگام ذخیره‌ی فایل تازه."""
    max_width = 1200
    webp_quality = 80

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        for field in self._meta.fields:
            if not isinstance(field, models.ImageField):
                continue
            img = getattr(self, field.name)
            # ✅ فقط فایل تازه‌آپلودشده — نه فایل لودشده از DB
            if not img or getattr(img, "_committed", True):
                continue
            try:
                img.file.seek(0)
            except Exception:
                pass
            new_name = process_image_with_transparency(
                img.file,
                max_width=self.max_width,
                quality=self.webp_quality,
            )
            img.name = new_name
            img._committed = True

        super().save(*args, **kwargs)

    def process_gallery(self, gallery_field_name, files, replace=False):
        """پردازش فایل‌های گالری و ذخیره به‌صورت لیست JSON."""
        gallery = [] if replace else list(getattr(self, gallery_field_name) or [])
        for f in files:
            gallery.append(process_image_with_transparency(
                f,
                max_width=self.max_width,
                quality=self.webp_quality,
            ))
        setattr(self, gallery_field_name, gallery)
        self.save(update_fields=[gallery_field_name])


class ImageProcessingMixinInTranslate(ImageProcessingMixin):
    """همان ImageProcessingMixin، برای مدل‌های ترجمه‌ای."""
    class Meta:
        abstract = True