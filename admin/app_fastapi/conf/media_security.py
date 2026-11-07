# ========== applications/_fastapi/conf/media_security.py - نسخه نهایی ==========
import os
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Request
from fastapi.responses import FileResponse
from django.conf import settings
from django.core.cache import cache

class SecureMediaService:
    """
    سرویس امن فایل‌های مدیا با:
    - Path traversal prevention
    - Signed URLs
    - پشتیبانی از کاربر مهمان (بدون login)
    - Rate limiting per IP
    """
    
    SIGNATURE_SECRET = settings.SECRET_KEY.encode() + b"_media_secure_salt_2024"
    URL_EXPIRE_SECONDS = 3600  # 1 ساعت
    
    @classmethod
    def generate_signed_url(cls, file_path: str, user_id: Optional[int] = None) -> str:
        """
        تولید URL امضا شده برای دسترسی امن
        اگر user_id = None باشد، کاربر مهمان محسوب می‌شود
        """
        expires = datetime.now() + timedelta(seconds=cls.URL_EXPIRE_SECONDS)
        expires_timestamp = int(expires.timestamp())
        
        # استفاده از شناسه مخصوص مهمان
        user_identifier = f"guest_{expires_timestamp}" if user_id is None else str(user_id)
        message = f"{file_path}:{user_identifier}:{expires_timestamp}"
        
        signature = hmac.new(
            cls.SIGNATURE_SECRET,
            message.encode(),
            hashlib.sha256
        ).hexdigest()[:32]
        
        guest_param = "true" if user_id is None else "false"
        return f"/secure-media/{file_path}?expires={expires_timestamp}&sig={signature}&guest={guest_param}"
    
    @classmethod
    async def verify_and_serve(
        cls, 
        file_path: str, 
        expires: int, 
        signature: str,
        request: Request,
        user_id: Optional[int] = None,
        guest: str = "false"
    ) -> FileResponse:
        """
        بررسی و سرویس امن فایل
        - پشتیبانی از کاربر مهمان
        - اعتبارسنجی کامل signature
        - Rate limiting بر اساس IP
        """
        # 1. بررسی expiration
        current_time = int(datetime.now().timestamp())
        if expires < current_time:
            raise HTTPException(status_code=410, detail="لینک منقضی شده است")
        
        # 2. تعیین نوع کاربر (مهمان یا عضو)
        is_guest = guest.lower() == 'true' or user_id is None
        user_identifier = f"guest_{expires}" if is_guest else str(user_id)
        
        # 3. بررسی signature
        message = f"{file_path}:{user_identifier}:{expires}"
        expected_sig = hmac.new(
            cls.SIGNATURE_SECRET,
            message.encode(),
            hashlib.sha256
        ).hexdigest()[:32]
        
        if not hmac.compare_digest(signature, expected_sig):
            raise HTTPException(status_code=403, detail="لینک نامعتبر است")
        
        # 4. جلوگیری از path traversal
        if '..' in file_path or file_path.startswith('/') or file_path.startswith('\\'):
            raise HTTPException(status_code=403, detail="مسیر فایل نامعتبر است")
        
        # 5. ساخت مسیر کامل و اعتبارسنجی نهایی
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        real_path = os.path.realpath(full_path)
        media_root_real = os.path.realpath(settings.MEDIA_ROOT)
        
        if not real_path.startswith(media_root_real):
            raise HTTPException(status_code=403, detail="دسترسی غیرمجاز")
        
        # 6. بررسی وجود فایل
        if not os.path.exists(real_path):
            raise HTTPException(status_code=404, detail="فایل یافت نشد")
        
        # 7. Rate limiting بر اساس IP (جلوگیری از DOS)
        client_ip = request.client.host
        rate_key = f"media_rate:{client_ip}:{datetime.now().hour}"
        count = cache.get(rate_key, 0)
        
        # محدودیت: 100 دانلود در ساعت برای هر IP
        max_downloads = 200 if not is_guest else 50  # مهمان محدودیت کمتری دارد
        if count >= max_downloads:
            raise HTTPException(
                status_code=429, 
                detail=f"تعداد درخواست بیش از حد مجاز. حداکثر {max_downloads} دانلود در ساعت"
            )
        
        cache.set(rate_key, count + 1, 3600)
        
        # 8. هدرهای امنیتی
        headers = {
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'none'",
            "Cache-Control": "public, max-age=3600",
            "Access-Control-Allow-Origin": "*",
        }
        
        # 9. تعیین نوع محتوا (اختیاری - بر اساس extension)
        import mimetypes
        content_type, _ = mimetypes.guess_type(real_path)
        if content_type:
            headers["Content-Type"] = content_type
        
        return FileResponse(real_path, headers=headers)