# Path: config/urls_rest_api.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from applications.category.views.drf import CategoryViewSet
from applications.page.views.drf import PageViewSet
from applications.setting.views.drf import CityViewSet
from applications.core.views.drf import TinyMCEImageViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'v1/category', CategoryViewSet, basename='category')
router.register(r'v1/page',     PageViewSet,     basename='page')
router.register(r'v1/city',     CityViewSet,     basename='city')

urlpatterns = [
    path('v1/tinymce-image/',        TinyMCEImageViewSet.as_view({'get': 'list', 'post': 'create'}), name='get_uploaded_images'),
    path('v1/tinymce-image/upload/', TinyMCEImageViewSet.as_view({'post': 'create'}),                name='upload_image'),
    path('v1/tinymce-image/delete/', TinyMCEImageViewSet.as_view({'post': 'destroy_by_name'}),       name='delete_image'),
    path('', include(router.urls)),
]