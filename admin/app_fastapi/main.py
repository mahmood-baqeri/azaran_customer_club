# django/app_fastapi/main.py

import os

from contextlib import asynccontextmanager
from typing import Optional
from fastapi.middleware.gzip import GZipMiddleware
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from django.conf import settings
from django.core.cache import cache
from applications.log.fastapi_middleware import FastAPIRequestLogMiddleware
from app_fastapi.conf.media_security import SecureMediaService
from app_fastapi.conf.redis_client import RedisClient
from app_fastapi.views.user.helper import get_current_user_optional
from applications.user.models import User
from middlewares.fastapiLocaleMiddleware import DjangoLocaleMiddleware
from app_fastapi.conf.response import validation_error_response

# ========== اضافه کردن middleware های امنیتی ==========
from app_fastapi.middlewares.rate_limiter import DOSProtectionMiddleware
from app_fastapi.middlewares.security_headers import SecurityHeadersMiddleware


# ============================================================
# Routers
# ============================================================
from app_fastapi.views.user.auth import router as auth_router
from app_fastapi.views.user.user import router as user_router
from app_fastapi.views.user.invitation import router as invitation_router
from app_fastapi.views.user.favorite import router as user_favorite_router
from app_fastapi.views.user.job_certificate import router as user_job_certificate_router
from app_fastapi.views.slider import router as slider_router
from app_fastapi.views.setting import router as setting_router
from app_fastapi.views.contactus import router as contactus_router

from app_fastapi.views.gift.gift import router as gift_router
from app_fastapi.views.gift.order import router as gift_order_router
from app_fastapi.views.promotion import router as promotion_router
from app_fastapi.views.faq import router as faq_router
from app_fastapi.views.project.project import router as project_router
from app_fastapi.views.factor.factor import router as factor_router
from app_fastapi.views.support.support import router as support_router
from app_fastapi.views.gallery.gallery import router as gallery_router
from app_fastapi.views.visit.visit import router as visit_router
from app_fastapi.views.review.review import router as review_router
from app_fastapi.views.learn.learn import router as learn_router
from app_fastapi.views.score.score import router as score_router
from app_fastapi.views.notification.notification import router as notification_router


# ============================================================
# Lifespan Manager
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    مدیریت چرخه حیات برنامه

    Startup:
        - اتصال Redis
        - آماده‌سازی SSE Manager
        - پاک‌سازی Cache
        - نمایش Route ها

    Shutdown:
        - بستن SSE Manager
        - بستن Redis
    """

    # ========================================================
    # STARTUP
    # ========================================================

    print("🚀 Starting up FastAPI application...")

    # --------------------------------------------------------
    # Redis
    # --------------------------------------------------------

    try:
        redis = await RedisClient.get_client()
        await redis.ping()

        print("✅ Redis connection established")

    except Exception as e:

        print(f"⚠️ Redis connection failed: {e}")

    # --------------------------------------------------------
    # SSE Manager
    # --------------------------------------------------------

    try:

        from app_fastapi.sse_manager import sse_manager

        # اطمینان از بسته شدن Connection های قبلی
        await sse_manager.cleanup_all()

        print("✅ SSE Manager initialized")

    except Exception as e:

        print(f"⚠️ SSE Manager init failed: {e}")

    # --------------------------------------------------------
    # Cache
    # --------------------------------------------------------

    try:

        cache.clear()

        print("✅ Cache cleared")

    except Exception:

        pass

    # --------------------------------------------------------
    # Workflow Registry
    # --------------------------------------------------------

    try:

        # دوباره اجرا نمی‌کنیم؛
        # load_workflows() قبل از ساخت App اجرا شده است.
        print("✅ Workflow registry initialized")

    except Exception as e:

        print(f"⚠️ Workflow registry initialization failed: {e}")

    # --------------------------------------------------------
    # Registered Routes
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("📋 Registered Routes:")
    print("=" * 60)

    for route in app.routes:

        if hasattr(route, "path"):

            methods = getattr(
                route,
                "methods",
                {"MOUNT"},
            )

            if methods == {"MOUNT"}:
                methods_str = "MOUNT"
            else:
                methods_str = ", ".join(
                    sorted(methods)
                )

            print(
                f"{methods_str:15} {route.path}"
            )

    print("=" * 60 + "\n")

    print("✅ Application startup complete")

    # ========================================================
    # APPLICATION RUNNING
    # ========================================================

    yield

    # ========================================================
    # SHUTDOWN
    # ========================================================

    print("🛑 Shutting down FastAPI application...")

    # --------------------------------------------------------
    # SSE Manager
    # --------------------------------------------------------

    try:

        from app_fastapi.sse_manager import sse_manager

        await sse_manager.cleanup_all()

        print("✅ SSE Manager cleaned up")

    except Exception as e:

        print(
            f"⚠️ SSE Manager cleanup error: {e}"
        )

    # --------------------------------------------------------
    # Redis
    # --------------------------------------------------------

    try:

        await RedisClient.close()

        print("✅ Redis connection closed")

    except Exception as e:

        print(
            f"⚠️ Redis close error: {e}"
        )

    print("✅ Shutdown complete")


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="CLUB API",
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# Middleware
# ============================================================

# 1. Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# 2. DOS / Rate Limiting
app.add_middleware(DOSProtectionMiddleware)

app.add_middleware(FastAPIRequestLogMiddleware)

# 4. Internationalization
app.add_middleware(DjangoLocaleMiddleware)

# 5. GZip
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 6. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:8000",
        "http://10.0.2.2:8000",
        "https://yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ============================================================
# Routers
# ============================================================
app.include_router(auth_router, prefix="/v1/auth")
app.include_router(user_router, prefix="/v1/user")
app.include_router(user_favorite_router, prefix="/v1/user")
app.include_router(user_job_certificate_router, prefix="/v1/user")
app.include_router(invitation_router, prefix="/v1/user/invitation")

app.include_router(slider_router,prefix="/v1/slider")
app.include_router(setting_router,prefix="/v1/setting")
app.include_router(contactus_router,prefix="/v1/contact")
app.include_router(gift_router,prefix="/v1/gifts")
app.include_router(gift_order_router,prefix="/v1/gift-orders")
app.include_router(promotion_router,prefix="/v1/promotions")
app.include_router(faq_router,prefix="/v1/faq")
app.include_router(project_router,prefix="/v1/projects")
app.include_router(factor_router,prefix="/v1/factors")
app.include_router(support_router,prefix="/v1/support")
app.include_router(gallery_router,prefix="/v1/gallery")
app.include_router(visit_router,prefix="/v1/visit")
app.include_router(review_router,prefix="/v1/review")
app.include_router(learn_router,prefix="/v1/learn")
app.include_router(score_router,prefix="/v1/score")
app.include_router(notification_router,prefix="/v1/notifications")

# ============================================================
# Static Files
# ============================================================

static_path = os.path.join(
    os.getcwd(),
    "static",
)

if os.path.exists(static_path):

    app.mount(
        "/static",
        StaticFiles(
            directory=static_path
        ),
        name="static",
    )


# ============================================================
# Secure Media Endpoint
# ============================================================

@app.get(
    "/secure-media/{file_path:path}"
)
async def secure_media(
    file_path: str,
    expires: int,
    sig: str,
    request: Request,
    user: Optional[User] = Depends(
        get_current_user_optional
    ),
):
    """
    Endpoint امن برای دسترسی به فایل‌های مدیا

    - پشتیبانی از کاربران وارد شده
    - پشتیبانی از کاربران مهمان
    - نیازمند Signature معتبر
    """

    user_id = user.id if user else None

    return await SecureMediaService.verify_and_serve(
        file_path=file_path,
        expires=expires,
        signature=sig,
        request=request,
        user_id=user_id,
    )


# ============================================================
# Health Check
# ============================================================

@app.get(
    "/health"
)
async def health_check():
    """
    Endpoint برای بررسی سلامت سرویس
    """

    return {
        "status": "healthy",
        "timestamp": __import__(
            "datetime"
        ).datetime.now().isoformat(),
    }


# ============================================================
# Root Endpoint
# ============================================================

@app.get(
    "/"
)
async def root():

    return {
        "message": "Chat API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


# ============================================================
# Exception Handlers
# ============================================================

@app.exception_handler(
    RequestValidationError
)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):

    errors = []

    for error in exc.errors():

        field = (
            ".".join(
                str(loc)
                for loc in error["loc"][1:]
            )
            if len(error["loc"]) > 1
            else str(error["loc"][0])
        )

        message = error["msg"]

        errors.append(
            {
                "field": field,
                "message": message,
            }
        )

    return validation_error_response(
        errors
    )


# ============================================================
# HTTP Exception Handler
# ============================================================

@app.exception_handler(
    HTTPException
)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):

    detail = exc.detail

    if isinstance(detail, dict):

        message = detail.get(
            "message",
            "Unknown Error",
        )

        error_code = detail.get(
            "error_code"
        )

    else:

        message = str(detail)

        error_code = None

    return JSONResponse(
        status_code=exc.status_code,

        content={
            "status": "Error",
            "message": message,
            "error_code": error_code,
            "path": request.url.path,
        },
    )


# ============================================================
# Global Exception Handler
# ============================================================

@app.exception_handler(
    Exception
)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):

    """
    گرفتن خطاهای پیش‌بینی نشده
    """

    import traceback

    print(
        f"Unhandled exception: {exc}"
    )

    traceback.print_exc()

    return JSONResponse(
        status_code=500,

        content={
            "status": "Error",
            "message": "Internal server error",
            "detail": (
                str(exc)
                if settings.DEBUG
                else None
            ),
        },
    )