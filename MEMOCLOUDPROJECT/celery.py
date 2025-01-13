from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Définir le module de configuration par défaut de Django pour le programme Celery.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'votre_projet.settings')

app = Celery('votre_projet')

# Charger la configuration de Django.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autoload des tâches dans les applications Django.
app.autodiscover_tasks()