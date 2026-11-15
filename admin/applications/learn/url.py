# applications/learn/url.py

from django.urls import path

from . import views

app_name = "app_learn"

urlpatterns = [
    # List
    path("learn/", views.learn_index, name="learn_index"),
    path("learn/export/", views.learn_export, name="learn_export"),

    # CRUD
    path("learn/create/", views.learn_create, name="learn_create"),
    path("learn/<int:id>/", views.learn_detail, name="learn_detail"),
    path("learn/<int:id>/update/", views.learn_update, name="learn_update"),
    path("learn/<int:id>/delete/", views.learn_delete, name="learn_delete"),

    # Action
    path("learn/<int:id>/toggle-active/", views.learn_toggle_active, name="learn_toggle_active"),
]