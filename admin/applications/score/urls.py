# applications/score/urls.py

from django.urls import path
from . import views

app_name = "app_score"

urlpatterns = [
    # Score Rules
    path("rules/", views.rule_index, name="rule_index"),
    path("rules/create/", views.rule_create, name="rule_create"),
    path("rules/<int:id>/update/", views.rule_update, name="rule_update"),
    path("rules/<int:id>/delete/", views.rule_delete, name="rule_delete"),
    path("rules/<int:id>/toggle/", views.rule_toggle_active, name="rule_toggle_active"),
    path("rules/seed-defaults/", views.rule_seed_defaults, name="rule_seed_defaults"),

    # Score Logs
    path("logs/", views.log_index, name="log_index"),
    path("logs/<int:id>/", views.log_detail, name="log_detail"),

    # User Scores
    path("users/", views.user_score_index, name="user_score_index"),
    path("users/<int:user_id>/", views.user_score_detail, name="user_score_detail"),
    path("users/<int:user_id>/adjust/", views.user_score_adjust, name="user_score_adjust"),
]