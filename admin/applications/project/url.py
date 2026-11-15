# applications/project/url.py

from django.urls import path

from . import views

app_name = "project"

urlpatterns = [
    # List
    path("", views.project_index, name="project_index"),
    path("export/", views.project_export, name="project_export"),

    # CRUD
    path("create/", views.project_create, name="project_create"),
    path("<int:id>/", views.project_detail, name="project_detail"),
    path("<int:id>/update/", views.project_update, name="project_update"),
    path("<int:id>/delete/", views.project_delete, name="project_delete"),

    # Actions
    path("<int:id>/approve/", views.project_approve_action, name="project_approve"),
    path("<int:id>/reject/",  views.project_reject_action,  name="project_reject"),

    # Colleagues
    path("<int:id>/colleague/add/", views.project_colleague_add, name="project_colleague_add"),
    path("<int:id>/colleague/<int:colleague_id>/delete/",
         views.project_colleague_delete, name="project_colleague_delete"),

    # Attachments
    path("<int:id>/attachment/upload/",
         views.project_attachment_upload, name="project_attachment_upload"),
    path("<int:id>/attachment/<int:attachment_id>/delete/",
         views.project_attachment_delete, name="project_attachment_delete"),
]