# quick_publisher/celery.py

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')

app = Celery('foodgram')
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
