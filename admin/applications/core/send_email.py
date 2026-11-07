from email.message import EmailMessage
import aiosmtplib
from django.utils.translation import gettext_lazy as _

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_email@gmail.com"
SMTP_PASSWORD = "your_app_password"  # یا رمز اپلیکیشن در Gmail


async def send_email_with_token(to_email: str, reset_link: str):
    message = EmailMessage()
    message["From"] = SMTP_USERNAME
    message["To"] = to_email
    message["Subject"] = _("Password recovery")

    message.set_content(f"""
    Hello,
    
    Click on the link below to change your password:

    {reset_link}

    If this was not your request, please disregard this email.
    
    Thank you.
    """)

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
        )
        print(f"ایمیل به {to_email} ارسال شد.")
    except Exception as e:
        print(_("Error sending email:"), e)
        raise



# ⚠️ نکات امنیتی:
# از رمز اپلیکیشن (App Password) استفاده کن، نه رمز اصلی Gmail.
#
# برای Gmail باید احراز هویت دو مرحله‌ای (2FA) فعال و App Password تولید بشه.
#
# اگر از سرویس‌هایی مثل SendGrid یا Mailgun استفاده کنی، ارسال ایمیل راحت‌تر و حرفه‌ای‌تره.
#
# می‌خوای نمونه تنظیمات برای Mailgun یا SendGrid هم برات بنویسم؟