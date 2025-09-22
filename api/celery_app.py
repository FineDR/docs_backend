# api/celery_app.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drf_api.settings")

app = Celery("drf_api")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
