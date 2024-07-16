import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ej.settings")

# Use the name of the RabbitMQ container as the hostname.
broker_url = "pyamqp://guest@rabbitmq//"
app = Celery("src/ej_clusters", broker=broker_url)
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
