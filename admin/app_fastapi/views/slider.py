from asgiref.sync import sync_to_async
from fastapi import APIRouter, HTTPException, Depends, Request, Form

from channels.db import database_sync_to_async
from fastapi import APIRouter, HTTPException, Depends

# from applications._fastapi.pagination import def__pagination, get_querySet_count
from app_fastapi.conf.response import success_response, error_response
from app_fastapi.schemas.setting import SliderSchema
from applications.setting.models import Slider

router = APIRouter()


#############################################################################################
#############################################################################################
###########################################
###########################################         All Slider
@router.get("/")
async def get_all_news(request: Request):
    querySet = await async_get_all_news(request)
    # paginated_data = await def__pagination(querySet, request, serializer_class=SliderSchema)
    return success_response("All Slider", querySet)


###########################################         async
@database_sync_to_async
def async_get_all_news(request):
    all_sliders = Slider.objects.filter(is_active=1).values("id", "title", "paragraph", "photo")
    return list(all_sliders) 
