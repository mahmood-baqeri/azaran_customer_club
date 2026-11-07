from django.apps import AppConfig


class config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'applications.user'
    label = 'app_user'

    def ready(self):
        import applications.user.signals