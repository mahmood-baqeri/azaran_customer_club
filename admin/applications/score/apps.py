from django.apps import AppConfig


class config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'applications.score'
    label = 'app_score'


    def ready(self):
        from applications.score import hooks  # noqa