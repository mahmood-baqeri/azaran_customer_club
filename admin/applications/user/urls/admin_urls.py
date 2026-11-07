from django.urls import path
from applications.user.view import admin_login
from applications.user.view import admin_views


urlpatterns = [
    
    path('', admin_views.index, name='admin_index'),
    path('create', admin_views.create, name='admin_create'),
    path('update/<int:id>', admin_views.update, name='admin_update'),
    path('delete/<int:id>', admin_views.delete, name='admin_delete'),
    
    
    path('login/pass', admin_login.loginPass, name='admin_login_with_pass'),
    path('login/mobile', admin_login.loginMobile, name='admin_login_with_mobile'),
    path('verify', admin_login.verifyAdmin, name='admin_verify'),
    path('logout', admin_login.logoutAdmin, name='admin_logout'),


    path('profile', admin_views.profile, name='admin_profile'),
    path('changePass', admin_views.changePass, name='admin_change_pass'),
]


