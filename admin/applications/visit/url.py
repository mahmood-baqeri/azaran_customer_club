# applications/visit/url.py

from django.urls import path

from . import views

app_name = "app_visit"

urlpatterns = [
    # Visits
    path("", views.visit_index, name="visit_index"),
    path("export/", views.visit_export, name="visit_export"),
    path("create/", views.visit_create, name="visit_create"),
    path("<int:id>/", views.visit_detail, name="visit_detail"),
    path("<int:id>/update/", views.visit_update, name="visit_update"),
    path("<int:id>/delete/", views.visit_delete, name="visit_delete"),
    path("<int:id>/toggle-active/", views.visit_toggle_active, name="visit_toggle_active"),

    # Requests
    path("requests/", views.request_index, name="request_index"),
    path("requests/export/", views.request_export, name="request_export"),
    path("requests/create/", views.request_create, name="request_create"),
    path("requests/<int:id>/", views.request_detail, name="request_detail"),
    path("requests/<int:id>/approve/", views.request_approve, name="request_approve"),
    path("requests/<int:id>/reject/", views.request_reject, name="request_reject"),
    path("requests/<int:id>/delete/", views.request_delete, name="request_delete"),
]