# applications/user/urls.py

from django.urls import path
from ..view import user_view


urlpatterns = [
    path("", user_view.user_index, name="user_index"),
    path("create/", user_view.user_create, name="user_create"),
    path("<int:id>/update/", user_view.user_update, name="user_update"),
    path("<int:id>/delete/", user_view.user_delete, name="user_delete"),
    path("<int:id>/", user_view.user_detail, name="user_detail"),

    # Actions
    path("<int:id>/verify-mobile/", user_view.user_verify_mobile_action, name="user_verify_mobile"),
    path("<int:id>/toggle-active/", user_view.user_toggle_active_action, name="user_toggle_active"),
    path("<int:id>/certificate/<int:cert_id>/approve/", user_view.user_certificate_approve, name="user_certificate_approve"),
    path("<int:id>/certificate/<int:cert_id>/reject/", user_view.user_certificate_reject, name="user_certificate_reject"),
]