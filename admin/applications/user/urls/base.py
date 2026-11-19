# Path: applications/user/urls/base.py

# admin/applications/user/url/base.py

from django.urls import path, include

app_name = "app_user"

urlpatterns = [
    path("admin/", include("applications.user.urls.admin_urls")),
    
    path("user/", include("applications.user.urls.user_urls")),
]