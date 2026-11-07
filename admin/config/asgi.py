import os
import django
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from starlette.routing import Mount, Router

# تنظیمات Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django_app = get_asgi_application()

# ایجاد FastAPI اصلی
from app_fastapi.main import app as fastapi_app


# ادغام Django و FastAPI
application = Router(
    [
        Mount("/manager/api", app=fastapi_app),  # FastAPI در مسیر /api
        Mount("/", app=django_app),      # Django در مسیر اصلی
    ]
)