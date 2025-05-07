from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from dotenv import load_dotenv

# Load environment variables from .env file
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
if ENVIRONMENT == 'production':
    load_dotenv('.env.production')
else:
    load_dotenv('.env.development')
    
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# app = Celery('backend', broker='amqp://guest:guest@localhost:5672')
app = Celery('backend', broker=os.getenv('CELERY_BROKER'))

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()