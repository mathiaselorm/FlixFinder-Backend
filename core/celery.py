from __future__ import absolute_import, unicode_literals
import os
from celery import Celery



# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Initialize Celery with the project name
app = Celery('core')

# Load configuration from Django's settings.py using the CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks from all registered Django app configs
app.autodiscover_tasks()

# Define a sample debug task to test the Celery worker
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    return "Task executed successfully"

