from asgiref.sync import sync_to_async
from django.core.paginator import Paginator
from fastapi import APIRouter, HTTPException, Depends, Request, Form
from django.utils.timezone import now
from channels.db import database_sync_to_async
from fastapi import APIRouter, HTTPException, Depends


from app_fastapi.conf.response import success_response, error_response
from applications.core.utils import get_ip_address
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

router = APIRouter()
meta_Key = "ContactUs"


#############################################################################################
#############################################################################################
###########################################
###########################################         All ContactUs
@router.post("/store")
async def get_all(request: Request):
    form_data = await request.json()
    username = form_data.get('name')
    subject = form_data.get('subject')
    phone = form_data.get('phone')
    text = form_data.get('text')

    if username is None or username == '':
        return error_response(f"{_('name')} {_('Required')}")
    if subject is None or subject == '':
        return error_response(f"{_('Subject')} {_('Required')}")
    if phone is None or phone == '':
        return error_response(f"{_('Phone')} {_('Required')}")
    if text is None or text == '':
        return error_response(f"{_('Text')} {_('Required')}")

    result = await sync_create(username, subject, text, phone, get_ip_address(request))
    if result == "LIMIT":
        return error_response(f"{_('Daily limit contact form')}")

    if not result:
        return error_response(f"{_('You have already submitted')}")

    return success_response(f"{_('ContactUs')} {_('Successfully Stored')}")


###########################################         async
@database_sync_to_async
def sync_create(username, subject, text, phone, ip):
    last_24h = timezone.now() - timedelta(hours=24)
