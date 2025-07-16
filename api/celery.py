import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

app = Celery('nq-api')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks() 