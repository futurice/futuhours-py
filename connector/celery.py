from __future__ import absolute_import

import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import settings
from django.conf import settings

# https://docs.getsentry.com/hosted/clients/python/integrations/celery/
import raven
from raven.contrib.celery import register_signal, register_logger_signal
class Celery(Celery):
    def on_configure(self):
        client = raven.Client(settings.RAVEN_CONFIG['dsn'])
        register_logger_signal(client)
        register_signal(client)

app = Celery('connector')
app.config_from_object('connector.celeryconfig')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
