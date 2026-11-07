import os
import datetime
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
from django.db import models
import tempfile
import shutil

import string
import random
import uuid

from django_dump_die.middleware import dd
from jdatetime import GregorianToJalali
from persiantools.jdatetime import JalaliDate

from config import settings


def uploadFile(file):
    dateFolder = f'{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}'
    path = f'static_media/{dateFolder}'
    if not os.path.exists(path):
        os.makedirs(path)

    filename = f'{customFileName()}{os.path.splitext(file.name)[1]}'
    fd, filepath = tempfile.mkstemp(prefix=file.name, dir=settings.MEDIA_ROOT + '/' + dateFolder)
    filepath = filepath.split(file.name)[0] + filename
    with open(filepath, 'wb+') as dest:
        shutil.copyfileobj(file, dest)

    return dateFolder + '/' + filename


def uploadFileFastAPI(file):
    dateFolder = f'{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}'
    path = os.path.join(settings.MEDIA_ROOT, dateFolder)
    os.makedirs(path, exist_ok=True)

    filename = f'{customFileName()}{os.path.splitext(file.filename)[1]}'
    filepath = os.path.join(path, filename)

    with open(filepath, 'wb+') as dest:
        shutil.copyfileobj(file.file, dest)  # 👈 استفاده از stream اصلی فایل

    return f'{dateFolder}/{filename}'


def uploadFileWithPath(file, path):
    newPath = f'static_media/{path}'
    if not os.path.exists(newPath):
        os.makedirs(newPath)

    today = datetime.datetime.now()
    jalali = JalaliDate(datetime.date(today.year, today.month, today.day)).strftime("%Y-%m-%d")
    name = str(jalali) + '-' + str(today.hour) + '-' + str(today.minute) + os.path.splitext(file.name)[1]
    fd, filepath = tempfile.mkstemp(prefix=file.name, dir=settings.MEDIA_ROOT + '/' + path)
    filepath = filepath.split(file.name)[0] + name
    with open(filepath, 'wb+') as dest:
        shutil.copyfileobj(file, dest)

    return path + '/' + name


def uploadExcel(file):
    today = datetime.datetime.now()
    jalali = JalaliDate(datetime.date(today.year, today.month, today.day)).strftime("%Y-%m-%d")
    name = str(jalali) + '-' + str(today.hour) + '-' + str(today.minute) + '.xlsx'

    # custom_name = f"{uuid.uuid4()}.xlsx"

    file_path = os.path.join(settings.MEDIA_ROOT, 'perferazhExcel', name)
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def uploadFileFromModel(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{customFileName()}.{ext}'
    return os.path.join(f'{datetime.date.today().year}-{datetime.date.today().month}-{datetime.date.today().day}', filename)


def getFilename(file):
    return file.name


def getMimetype(file):
    return file.content_type


def deleteFile(path):
    if os.path.isfile(settings.MEDIA_ROOT + '/' + path):
        os.remove(settings.MEDIA_ROOT + '/' + path)


def checkFileExtension(file):
    if file:
        ext = os.path.splitext(file.name)[1]  # [0] returns path+filename
        photoList = ['.png', '.gif', '.jpg', '.jpeg', '.jfif', '.pjpeg', '.pjp', '.svg', '.webp']
        videoList = ['.mp4', '.wmv', '.mov', '.flv', '.webm', '.avi', '.kmv', '.3gp']
        audioList = ['.mp3', '.wma', '.alag', '.aac', '.flac', '.aiff', '.wav', 'ogg']
        if ext.lower() in photoList:
            return 0
        elif ext.lower() in videoList:
            return 1
        elif ext.lower() in audioList:
            return 2
    return 3


def customFileName():
    return f'{datetime.datetime.now().hour}-{datetime.datetime.now().minute}-{datetime.datetime.now().second}-{datetime.datetime.now().microsecond}'


def detect_file_type(file):
    if file:
        ext = os.path.splitext(file.name)[1]  # [0] returns path+filename
        photoList = ['.png', '.gif', '.jpg', '.jpeg', '.jfif', '.pjpeg', '.pjp', '.svg', '.webp']
        videoList = ['.mp4', '.wmv', '.mov', '.flv', '.webm', '.avi', '.kmv', '.3gp']
        audioList = ['.mp3', '.wma', '.alag', '.aac', '.flac', '.aiff', '.wav', 'ogg']
        if ext.lower() in photoList:
            return "Image"
        elif ext.lower() in videoList:
            return "Video"
        elif ext.lower() in audioList:
            return "Audio"
    return "Unknown"


##################################################
# ==============================
# پردازش تصویر به WebP با حفظ شفافیت
# ==============================
def process_image_with_transparency(file, folder_prefix='static_media', max_width=1200, quality=80):
    """
    تصویر رو به WebP تبدیل می‌کنه، سایز رو محدود می‌کنه، و شفافیت PNG رو حفظ می‌کنه
    """
    dateFolder = f'{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}'
    path = os.path.join(folder_prefix, dateFolder)
    if not os.path.exists(path):
        os.makedirs(path)

    img = Image.open(file)
    img_format = img.format

    # تغییر سایز اگر لازم بود
    if img.width > max_width:
        ratio = max_width / float(img.width)
        height = int(img.height * ratio)
        img = img.resize((max_width, height), Image.Resampling.LANCZOS)

    buffer = BytesIO()

    # بررسی شفافیت
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        # حفظ شفافیت با WebP
        img.save(buffer, format="WEBP", quality=quality, lossless=False, method=6)
    else:
        # تبدیل به RGB اگر شفافیت نیست
        img = img.convert("RGB")
        img.save(buffer, format="WEBP", quality=quality, method=6)

    buffer.seek(0)

    filename = f'{customFileName()}.webp'
    final_path = os.path.join(path, filename)

    with open(final_path, 'wb') as out_file:
        out_file.write(buffer.read())
    buffer.close()

    return f'{dateFolder}/{filename}'


# ==============================
# Mixin جامع پردازش تصاویر
# ==============================
class ImageProcessingMixin(models.Model):
    max_width = 1200
    webp_quality = 80

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # پردازش همه ImageField ها
        for field in self._meta.fields:
            if isinstance(field, models.ImageField):
                image_field = getattr(self, field.name)
                if image_field and hasattr(image_field, 'file'):
                    new_path = process_image_with_transparency(
                        image_field.file,
                        max_width=self.max_width,
                        quality=self.webp_quality
                    )
                    image_field.name = new_path
        super().save(*args, **kwargs)

    def process_gallery(self, gallery_field_name, files, replace=False):
        """
        پردازش و ذخیره گالری
        replace: اگر True باشد، تصاویر قبلی جایگزین می‌شوند، اگر False اضافه می‌شوند
        """
        gallery = [] if replace else (getattr(self, gallery_field_name) or [])
        for f in files:
            gallery.append(process_image_with_transparency(
                f,
                max_width=self.max_width,
                quality=self.webp_quality
            ))
        setattr(self, gallery_field_name, gallery)
        self.save(update_fields=[gallery_field_name])


class ImageProcessingMixinInTranslate:
    max_width = 1200
    webp_quality = 80

    def save(self, *args, **kwargs):
        for field in self._meta.fields:
            if isinstance(field, models.ImageField):
                image_field = getattr(self, field.name)
                if image_field and hasattr(image_field, 'file'):
                    new_path = process_image_with_transparency(
                        image_field.file,
                        max_width=self.max_width,
                        quality=self.webp_quality
                    )
                    image_field.name = new_path
        super().save(*args, **kwargs)

    def process_gallery(self, gallery_field_name, files, replace=False):
        gallery = [] if replace else (getattr(self, gallery_field_name) or [])
        for f in files:
            gallery.append(
                process_image_with_transparency(
                    f,
                    max_width=self.max_width,
                    quality=self.webp_quality
                )
            )
        setattr(self, gallery_field_name, gallery)
        self.save(update_fields=[gallery_field_name])
