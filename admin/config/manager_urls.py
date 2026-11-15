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
    path('project/', include('applications.project.url')),
    path('factor/', include('applications.factor.url')),
    path('learn/', include('applications.learn.url')),
    path('support/', include('applications.support.url')),
    path('visit/', include('applications.visit.url')),
    path('gallery/', include('applications.gallery.url')),
    path('review/', include('applications.review.url')),


    # User areas
    path(f"users/", include('applications.user.urls.base')),

    path('server_api/', include('config.urls_rest_api')),
    path("tinymce/", include("tinymce.urls")),

    # Admin & tools
    path("administrator/", admin.site.urls),
    path("api-auth/", include('rest_framework.urls', namespace='rest_framework')),
]
