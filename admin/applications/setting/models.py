from django.db import models
from django.utils.text import slugify

from applications.core.fileManager import ImageProcessingMixin, ImageProcessingMixinInTranslate
from applications.core.keyValue import appSettings

from applications.core.baseModel import SoftDeleteModel, BaseModel

#######################################
##   Setting
#######################################
class Setting(ImageProcessingMixin, models.Model):
    key = models.CharField(max_length=100, choices=appSettings(), verbose_name="Key")
    value_file = models.ImageField(verbose_name="photo")
    value_text = models.TextField(null=True, blank=True, verbose_name="text", max_length=500)

    def __str__(self):
        return self.get_key_display()

    class Meta:
        db_table = "setting"


#######################################
#  slider
#######################################
class Slider(ImageProcessingMixin, models.Model):
    title = models.CharField(verbose_name="عنوان", max_length=255)
    paragraph = models.CharField(verbose_name="متن دوم", max_length=255)
    is_active = models.BooleanField(default=False, verbose_name="فعال/غیرفعال")
    photo = models.ImageField(verbose_name="photo")

    def __str__(self):
        return self.title

    class Meta:
        db_table = "setting_slider"


#######################################
#  Province
#######################################
class Province(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام استان")
    code = models.CharField(max_length=10, unique=True, null=True, blank=True, verbose_name="کد استان")

    class Meta:
        db_table = 'setting_province'
        verbose_name = 'استان'
        verbose_name_plural = 'استان‌ها'
        ordering = ['name']

    def __str__(self):
        return self.name


#######################################
#  City
#######################################
class City(models.Model):
    province = models.ForeignKey(Province,  on_delete=models.CASCADE,  related_name='cities', verbose_name="استان")
    name = models.CharField(max_length=100, verbose_name="نام شهر")

    class Meta:
        db_table = 'setting_city'
        verbose_name = 'شهر'
        verbose_name_plural = 'شهرها'
        ordering = ['name']
        # ✅ جلوگیری از ثبت شهر تکراری در یک استان
        unique_together = ('province', 'name')

    def __str__(self):
        return f"{self.name} ({self.province.name})"

#######################################
#######################################
#######################################
#######################################
#######################################
#######################################
#######################################
#######################################     Store

#
#
#
#######################################  Slider
def setting__slider__store(request, item=None):
    data = {
        'title': request.POST.get('title'),
        'paragraph': request.POST.get('paragraph'),
        'is_active': bool(request.POST.get('is_active')),
    }

    # ذخیره عکس اگر فرستاده شده باشه
    if 'photo' in request.FILES:
        data['photo'] = request.FILES['photo']

    # ساخت یا آپدیت شیء Slider
    if item is None:
        item = Slider.objects.create(**data)
    else:
        for key, value in data.items():
            setattr(item, key, value)
        item.save()

    return item


#
#
#
#######################################  Ad
def setting__ad__store(request, item=None):
    pass
