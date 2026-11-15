# applications/faq/url.py

from django.urls import path

from . import views

app_name = "app_faq"

urlpatterns = [
    # Categories
    path("categories/", views.category_index, name="category_index"),
    path("categories/export/", views.category_export, name="category_export"),
    path("categories/create/", views.category_create, name="category_create"),
    path("categories/<int:id>/update/", views.category_update, name="category_update"),
    path("categories/<int:id>/delete/", views.category_delete, name="category_delete"),
    path("categories/<int:id>/toggle-active/", views.category_toggle_active, name="category_toggle_active"),

    # FAQ
    path("", views.faq_index, name="faq_index"),
    path("export/", views.faq_export, name="faq_export"),
    path("<int:id>/", views.faq_detail, name="faq_detail"),
    path("<int:id>/delete/", views.faq_delete, name="faq_delete"),
    path("<int:id>/toggle-active/", views.faq_toggle_active, name="faq_toggle_active"),

    # Answers
    path("<int:id>/answer/create/", views.answer_create, name="answer_create"),
    path("answer/<int:answer_id>/toggle-active/", views.answer_toggle_active, name="answer_toggle_active"),
    path("answer/<int:answer_id>/delete/", views.answer_delete, name="answer_delete"),
]