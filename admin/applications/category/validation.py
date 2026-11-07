import json

from django.contrib import messages
from django.utils.translation import gettext_lazy as _


def category_validation(request):
    """اعتبارسنجی ساده فرم دسته‌بندی"""
    title = (request.POST.get("title") or "").strip()
    form_valid = True

    if not title:
        messages.add_message(
            request, messages.ERROR,
            json.dumps({"text": _("عنوان الزامی است")}),
        )
        form_valid = None

    return form_valid