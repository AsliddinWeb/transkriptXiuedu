# from django.apps import AppConfig
#
#
# class SettingsAppConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'settings_app'
#     verbose_name = 'Sayt sozlamalari'
#

from django.apps import AppConfig

class SettingsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'settings_app'
    verbose_name = 'Sayt sozlamalari'

    def ready(self):
        from simple_history import register
        from django.contrib.auth.models import User

        register(User)
