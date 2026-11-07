from starlette.middleware.base import BaseHTTPMiddleware
from django.utils import translation


class DjangoLocaleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # زبان پیش‌فرض
        language = request.headers.get("Language", "en")

        # فعال کردن زبان در Django
        translation.activate(language)

        response = await call_next(request)

        # غیرفعال کردن زبان بعد از پایان پاسخ
        translation.deactivate()

        # فقط برای مسیرهای media
        if request.url.path.startswith("/media"):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
        

        return response
