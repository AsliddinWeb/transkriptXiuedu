from django.apps import AppConfig


class TranskriptAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transkript_app'
    verbose_name = "Transkriptlar"

    def ready(self):
        import transkript_app.signals
