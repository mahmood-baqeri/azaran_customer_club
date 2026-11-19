# Path: applications/support/url.py

# applications/support/url.py

from django.urls import path

from . import views

app_name = "app_support"

urlpatterns = [
    # List
    path("", views.support_index, name="support_index"),
    path("export/", views.support_export, name="support_export"),

    # CRUD
    path("create/", views.support_create, name="support_create"),
    path("<int:id>/", views.support_detail, name="support_detail"),
    path("<int:id>/update/", views.support_update, name="support_update"),
    path("<int:id>/delete/", views.support_delete, name="support_delete"),

    # Actions
    path("<int:id>/change-status/", views.support_change_status, name="support_change_status"),
    path("<int:id>/close/", views.support_close, name="support_close"),
    path("<int:id>/send-message/", views.support_send_message, name="support_send_message"),
]