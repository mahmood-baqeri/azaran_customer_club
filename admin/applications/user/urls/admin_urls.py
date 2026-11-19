# Path: applications/user/urls/admin_urls.py

from django.urls import path
from applications.user.view import admin_login
from applications.user.view import manager_view


from django.urls import path

urlpatterns = [    
    path('login/pass', admin_login.loginPass, name='admin_login_with_pass'),
    path('login/mobile', admin_login.loginMobile, name='admin_login_with_mobile'),
    path('verify', admin_login.verifyAdmin, name='admin_verify'),
    path('logout', admin_login.logoutAdmin, name='admin_logout'),


    path("managers/", manager_view.manager_index, name="manager_index"),
    path("managers/export/", manager_view.manager_export, name="manager_export"),
    path("managers/create/", manager_view.manager_create, name="manager_create"),
    path("managers/profile/", manager_view.manager_profile, name="manager_profile"),                        # ← جدید
    path("managers/change-password/", manager_view.manager_change_password, name="manager_change_password"), # ← جدید
    path("managers/<int:id>/", manager_view.manager_detail, name="manager_detail"),
    path("managers/<int:id>/update/", manager_view.manager_update, name="manager_update"),
    path("managers/<int:id>/delete/", manager_view.manager_delete, name="manager_delete"),
    path("managers/<int:id>/toggle-active/", manager_view.manager_toggle_active_action, name="manager_toggle_active"),
]