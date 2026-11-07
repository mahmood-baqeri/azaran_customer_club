# ========== applications/_fastapi/middlewares/security_headers.py ==========
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    افزودن هدرهای امنیتی به تمام پاسخ‌ها
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # هدرهای امنیتی
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # CSP برای production (در صورت نیاز)
        if not request.url.hostname in ["localhost", "127.0.0.1"]:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'"
            )
        
        return response