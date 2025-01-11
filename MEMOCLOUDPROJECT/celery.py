from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'votre_projet.settings')

app = Celery('votre_projet')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()