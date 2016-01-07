from __future__ import absolute_import
from celery.schedules import crontab
from datetime import timedelta
import os

BROKER_URL = os.getenv('BROKER_URL', "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = os.getenv('RESULT_BACKEND', "redis://127.0.0.1/0")

CELERYD_PREFETCH_MULTIPLIER = 30
CELERY_ACCEPT_CONTENT = ['json',]
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = CELERY_TASK_SERIALIZER
CELERY_ACCEPT_CONTENT = [CELERY_TASK_SERIALIZER, ]

CELERYBEAT_SCHEDULE = {
    'fetch-report': {
        'task': 'connector.tasks.fetch_report',
        'schedule': timedelta(minutes=30),
    },
}
