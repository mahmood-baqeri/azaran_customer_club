# Path: applications/gallery/url.py

# applications/gallery/url.py

from django.urls import path

from . import views

app_name = "app_gallery"

urlpatterns = [
    # List
    path("", views.gallery_index, name="gallery_index"),
    path("export/", views.gallery_export, name="gallery_export"),

    # CRUD
    path("create/", views.gallery_create, name="gallery_create"),
    path("<int:id>/", views.gallery_detail, name="gallery_detail"),
    path("<int:id>/update/", views.gallery_update, name="gallery_update"),
    path("<int:id>/delete/", views.gallery_delete, name="gallery_delete"),

    # Actions
    path("<int:id>/approve/", views.gallery_approve, name="gallery_approve"),
    path("<int:id>/reject/", views.gallery_reject, name="gallery_reject"),
]