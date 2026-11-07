from django.urls import path, include
from rest_framework.routers import DefaultRouter

from applications.category.views.drf import CategoryViewSet
from applications.page.views.drf import PageViewSet

router = DefaultRouter()
router.register(r'v1/category', CategoryViewSet, basename='category')
router.register(r'v1/page', PageViewSet, basename='page')

urlpatterns = [
    path('', include(router.urls)),
]
