from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    # مسیرهای بخش مدیریت
    path('manager/', include('config.manager_urls')),

    # مسیر React App (هر چیزی غیر از موارد بالا)
    re_path(
        r'^(?!manager|api/|media/|static/|assets/).*$',
        TemplateView.as_view(template_name='index.html'),
        name='react_app'
    ),
]


# فایل‌های استاتیک Django
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# فایل‌های مدیا
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# فایل‌های React
urlpatterns += static(settings.REACT_ASSETS_URL, document_root=settings.REACT_ASSETS_DIR)

urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.FRONTEND_DIR)
