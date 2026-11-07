from typing import List

from asgiref.sync import sync_to_async
from django.db.models.fields.files import FieldFile
from fastapi import APIRouter, HTTPException, Depends, Request, Form
from datetime import date
from channels.db import database_sync_to_async
from fastapi import APIRouter, HTTPException, Depends

# from applications._fastapi.pagination import def__pagination, get_querySet_count
from app_fastapi.conf.response import success_response, error_response
from app_fastapi.schemas.setting import SettingSchema
from applications.setting.models import City, Province, Setting

router = APIRouter()


#############################################################################################
#############################################################################################
###########################################
###########################################         All Ad
@router.get("/", response_model=List[SettingSchema])
async def get_all_news(request: Request):
    querySet = await async_get_all_news(request)
    return success_response("All Setting", querySet)


###########################################         async
@database_sync_to_async
def async_get_all_news(request):
    excluded_keys = ["TopCoachsText"]
    all = Setting.objects.exclude(key__in=excluded_keys)
    result = []
    for setting in all:

        value = setting.value_text

        if setting.key in ["Logo", "FavIcon", 'Hero_Photo']:
            value = setting.value_file.url if setting.value_file else "/images/none.png"

        result.append({
            "key": setting.key,
            "value": str(value),
        })
    return result




# ============================================================
# Helpers (توابع آسنکرون برای ارتباط با دیتابیس)
# ============================================================
@database_sync_to_async
def get_all_provinces_sync():
    return list(Province.objects.values("id", "name", "code").order_by("name"))

@database_sync_to_async
def get_cities_by_province_sync(province_id: int):
    return list(City.objects.filter(province_id=province_id).values("id", "name").order_by("name"))

# ============================================================
# Endpoints
# ============================================================

@router.get("/provinces/")
async def get_provinces():
    """دریافت لیست تمام استان‌ها"""
    try:
        provinces = await get_all_provinces_sync()
        return success_response("All Provinces", provinces)
    except Exception as e:
        return error_response(str(e))


@router.get("/provinces/{province_id}/cities/")
async def get_cities(province_id: int):
    """دریافت لیست شهرهای یک استان خاص بر اساس شناسه"""
    try:
        cities = await get_cities_by_province_sync(province_id)
        if not cities:
            return success_response("All Cities", [])
            # اگر شهری پیدا نشد، می‌توانید پیام مناسب‌تری برگردانید
        
        return success_response("All Cities", cities)

    except Exception as e:
        return error_response(str(e))