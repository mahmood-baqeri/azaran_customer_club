# Path: applications/review/url.py

# applications/review/url.py

from django.urls import path

from . import views

app_name = "app_review"

urlpatterns = [
    # Questions
    path("questions/", views.question_index, name="question_index"),
    path("questions/export/", views.question_export, name="question_export"),
    path("questions/create/", views.question_create, name="question_create"),
    path("questions/<int:id>/", views.question_detail, name="question_detail"),
    path("questions/<int:id>/update/", views.question_update, name="question_update"),
    path("questions/<int:id>/delete/", views.question_delete, name="question_delete"),
    path("questions/<int:id>/toggle-active/", views.question_toggle_active, name="question_toggle_active"),

    # Answers
    path("answers/", views.answer_index, name="answer_index"),
    path("answers/export/", views.answer_export, name="answer_export"),
    path("answers/<int:id>/delete/", views.answer_delete, name="answer_delete"),
]