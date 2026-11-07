import json

from django.contrib import messages
from django.utils.translation import gettext_lazy as _


def setting__slider__validation(request, is_edit = None):
    title = (request.POST.get("title") or "").strip()
    photo = request.FILES.get("photo")
    
    form_valid = True

    if not title:
        messages.add_message(request, messages.ERROR, json.dumps({"text": "عنوان الزامیست"}))
        form_valid = None
        
    if not photo and is_edit == None:
        messages.add_message(request, messages.ERROR, json.dumps({"text": "تصویر الزامیست"}))
        form_valid = None

    return form_valid