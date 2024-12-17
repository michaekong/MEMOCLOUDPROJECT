# apps.py
from django.apps import AppConfig

class YourAppConfig(AppConfig):
    name = 'memoire'

    def ready(self):
        import your_app.signals  # Assurez-vous d'importer votre fichier signals.py
