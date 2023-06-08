from django.apps import AppConfig


class AtlassConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'atlass'

    def ready(self):
        import atlass.signals

