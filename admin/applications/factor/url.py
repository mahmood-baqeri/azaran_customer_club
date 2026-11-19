# Path: applications/factor/url.py

# applications/factor/url.py

from django.urls import path

from . import views

app_name = "app_factor"

urlpatterns = [
    # List
    path("", views.factor_index, name="factor_index"),
    path("export/", views.factor_export, name="factor_export"),

    # CRUD
    path("create/", views.factor_create, name="factor_create"),
    path("<int:id>/", views.factor_detail, name="factor_detail"),
    path("<int:id>/update/", views.factor_update, name="factor_update"),
    path("<int:id>/delete/", views.factor_delete, name="factor_delete"),

    # Actions
    path("<int:id>/approve/", views.factor_approve_action, name="factor_approve"),
    path("<int:id>/reject/", views.factor_reject_action, name="factor_reject"),
]