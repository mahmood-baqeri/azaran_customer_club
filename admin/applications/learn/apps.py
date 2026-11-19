# Path: applications/learn/apps.py

from django.apps import AppConfig


class config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'applications.learn'
    label = 'app_learn'
