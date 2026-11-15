from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [

    # Apps
    path("", include('applications.dashboard.url')),
    path("log/", include('applications.log.url')),
    path("role/", include('applications.role.url')),
    path("setting/", include('applications.setting.url')),
    path('page/', include('applications.page.url')),
    path('category/', include('applications.category.url')),
    
    path('gift/', include('applications.gift.url')),
    path('promotion/', include('applications.promotion.url')),
    path('score/', include('applications.score.urls')),
    path('notification/', include('applications.notification.url')),


    # User areas
    path(f"users/", include('applications.user.urls.base')),

    path('server_api/', include('config.urls_rest_api')),
    path("tinymce/", include("tinymce.urls")),

    # Admin & tools
    path("administrator/", admin.site.urls),
    path("api-auth/", include('rest_framework.urls', namespace='rest_framework')),
]
