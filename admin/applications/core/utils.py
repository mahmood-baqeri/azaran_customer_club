# backend/apps/core/utils.py
import hashlib
import secrets
import uuid
from django.contrib import messages
from django.core.cache import cache
import json
import os
import tempfile
import shutil
import string
import random
import datetime
import uuid
import re
from django.core.mail import send_mail
from django.conf import settings
import math
from time import time
from persiantools.jdatetime import JalaliDate, JalaliDateTime
from django_dump_die.middleware import dd
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect

from email.message import EmailMessage

#
#
####
def response_msg(request, level, text):
    """شورت‌کات برای ساختار استاندارد پیغام."""
    messages.add_message(request, level, json.dumps({"text": text}))

#
#
####
def generate_uuid():
    """تولید UUID یکتا"""
    return uuid.uuid4()

#
#
####
def generate_api_key():
    """تولید کلید API امن"""
    return secrets.token_urlsafe(32)

#
#
####
def generate_verification_code(length=6):
    """تولید کد تایید عددی"""
    import random
    import string
    return ''.join(random.choices(string.digits, k=length))

#
#
####
def hash_code(code: str) -> str:
    """هش کردن کد با SHA256"""
    return hashlib.sha256(code.encode()).hexdigest()

#
#
####
def rate_limit_check(key: str, limit: int, period: int = 60):
    """
    بررسی محدودیت نرخ
    key: کلید منحصربفرد (مثلاً ip یا user_id)
    limit: حداکثر تعداد درخواست
    period: دوره زمانی بر حسب ثانیه
    """
    cache_key = f"rate_limit_{key}"
    current = cache.get(cache_key, 0)

    if current >= limit:
        return False

    cache.set(cache_key, current + 1, period)
    return True

#
#
####
def get_ip_address(request):
    x_forwarded_for = request.headers.get('x-forwarded-for')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.client.host

def get_ip_address_2(request):
    """دریافت IP واقعی کاربر"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


#
#
####
def persian_digit_to_englidh(input):
    farsi_to_english = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
    }
    return ''.join(farsi_to_english.get(char, char) for char in input)

#
#
####
def randomStr(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

#
#
####
def handle_get_post(request, key, default=None):
    return request.POST.get(key, default)

#
#
####
def handle_get_file(request, key):
    return request.FILES.get(key) if key in request.FILES else None

#
#
####
def gregorian_to_jalali(date):
    try:
        return JalaliDate(datetime.date(int(date.year), int(date.month), int(date.day))).strftime("%Y-%m-%d")
    except:
        return ''

#
#
####
def jalali_to_gregorian(jDate):
    if type(jDate) == str:
        date = jDate.split('-')
        print(date)
        if date[0] and date[1] and date[2]:
            try:
                return JalaliDate(int(date[0]), int(date[1]), int(date[2])).to_gregorian()
            except:
                return None

#
#
####
def gregorian_to_jalali_revese(date):
    try:
        return JalaliDate(datetime.date(int(date.year), int(date.month), int(date.day))).strftime("%d-%m-%Y")
    except:
        return ''
#
#
####
def parse_json_field(request, field_name):
    try:
        raw = request.POST.get(field_name, "[]")
        return json.loads(raw) if raw else []
    except json.JSONDecodeError:
        return []

#
#
####
def generate_numeric_code(length=6):
    start = 10**(length-1)
    end = 10**length - 1
    return str(random.randint(start, end))


#
#
####
async def send_otp_code_async(mobile: str, code: str, test_mode: bool = True):
    txt = f"{_('Your verification code')}: {code}\n{_('This code is valid for 10 minutes')}."

    if test_mode:
        print(f"""
        ------------------------------
        Test Mobile Mode
        To: {mobile}
        Body:
        {txt}
        ------------------------------
        """)
        return

    # sms = GlobalSMS()
    # status, resp = sms.send_sms(mobile, txt)


#
#
####
def send_verification_email(email: str, code: str):
    subject = _("Your verification code")
    message = f"{_('Your verification code')}: {code} \n {_('This code is valid for 10 minutes')}."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

#
#
####
async def send_verification_email_async(email: str, code: str, test_mode: bool = True):
    """
    ارسال ایمیل async با aiosmtplib.
    اگر test_mode=True باشد، ایمیل در کنسول چاپ می‌شود.
    """
    subject = _("Your verification code")
    body = f"{_('Your verification code')}: {code}\n{_('This code is valid for 10 minutes')}."

    if test_mode:
        print(f"""
        ------------------------------
        Test Email Mode
        To: {email}
        Subject: {subject}
        Body:
        {body}
        ------------------------------
        """)
        return

    # ساخت پیام ایمیل
    msg = EmailMessage()
    msg["From"] = settings.DEFAULT_FROM_EMAIL
    msg["To"] = email
    msg["Subject"] = subject
    msg.set_content(body)

    # ارسال از طریق SMTP
    await aiosmtplib.send(
        msg,
        hostname=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        start_tls=settings.EMAIL_USE_TLS,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
    )

#
#
####
async def send_mail_async(subject: str, message: str, recipients: list[str], test_mode: bool = True):
    """
    ارسال ایمیل async.
    :param subject: عنوان ایمیل
    :param message: متن ایمیل
    :param recipients: لیست گیرنده‌ها
    :param test_mode: اگر True باشد، ایمیل چاپ می‌شود و ارسال واقعی انجام نمی‌شود
    """
    if test_mode:
        print(f"--- Email Test Mode ---\nTo: {', '.join(recipients)}\nSubject: {subject}\nBody:\n{message}\n----------------------")
        return

    email_msg = EmailMessage()
    email_msg["From"] = settings.DEFAULT_FROM_EMAIL
    email_msg["To"] = ", ".join(recipients)
    email_msg["Subject"] = subject
    email_msg.set_content(message)

    await aiosmtplib.send(
        email_msg,
        hostname=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        start_tls=settings.EMAIL_USE_TLS,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
    )


#
#
####
def redirect_back(request, fallback_url="/dashboard/"):
    """
    بازگشت به صفحه قبلی (HTTP_REFERER)
    اگر صفحه قبلی وجود نداشت، به fallback_url هدایت می‌شود.
    """
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect(fallback_url)