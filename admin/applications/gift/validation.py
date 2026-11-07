import json

from django.contrib import messages
from django.utils.translation import gettext_lazy as _


def page_validation(request):
    """
    اعتبارسنجی ساده فرم صفحه.
    فقط title و (summer یا text) بررسی می‌شود.
    """
    title = (request.POST.get("title") or "").strip()
    summer = (request.POST.get("summer") or "").strip()
    text = (request.POST.get("text") or "").strip()

    form_valid = True

    if not title:
        messages.add_message(
            request, messages.ERROR,
            json.dumps({"text": "عنوان الزامیست"}),
        )
        form_valid = None

    if not summer and not text:
        messages.add_message(
            request, messages.ERROR,
            json.dumps({"text": _("حداقل یکی از متن کوتاه یا متن اصلی الزامی است")}),
        )
        form_valid = None

    return form_valid