# applications/notification/url.py

from django.urls import path

from . import views

app_name = "notification"

urlpatterns = [
    # List
    path("", views.notification_index, name="notification_index"),
    path("export/", views.notification_export, name="notification_export"),

    # CRUD
    path("create/", views.notification_create, name="notification_create"),
    path("<int:id>/", views.notification_detail, name="notification_detail"),
    path("<int:id>/update/", views.notification_update, name="notification_update"),
    path("<int:id>/delete/", views.notification_delete, name="notification_delete"),

    # Actions
    path("<int:id>/send/", views.notification_send_action, name="notification_send"),
    path("<int:id>/cancel/", views.notification_cancel_action, name="notification_cancel"),
]