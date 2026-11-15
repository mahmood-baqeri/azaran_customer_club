from django.urls import path, include
from rest_framework.routers import DefaultRouter

from applications.category.views.drf import CategoryViewSet
from applications.page.views.drf import PageViewSet
from applications.setting.views.drf import CityViewSet
from applications.core.views.drf import TinyMCEImageViewSet

router = DefaultRouter()
router.register(r'v1/category',       CategoryViewSet,      basename='category')
router.register(r'v1/page',           PageViewSet,          basename='page')
router.register(r'v1/city',           CityViewSet,          basename='city')
router.register(r'v1/tinymce-image',  TinyMCEImageViewSet,  basename='tinymce-image')

urlpatterns = [
    path('', include(router.urls)),
]