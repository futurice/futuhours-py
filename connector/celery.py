from __future__ import absolute_import

import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import settings
from django.conf import settings

app = Celery('connector')
app.config_from_object('connector.celeryconfig')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
