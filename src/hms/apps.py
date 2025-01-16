from django.apps import AppConfig

class HmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hms'

    def ready(self):
        import hms.signals  # Load signals when the app starts
        print("Signals loaded!") 