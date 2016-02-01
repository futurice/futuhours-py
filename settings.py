from djangomi.init import *
import os
from django.conf import settings

ROOT = os.path.dirname(os.path.realpath(__file__))
settings.ROOT_URLCONF = "app"
settings.TEMPLATE_DIRS = (
    os.path.join(ROOT, 'templates'),
)
settings.INSTALLED_APPS += [
'django.contrib.contenttypes',
'django.contrib.auth',
'django.contrib.admin',
'django.contrib.sessions',

'hours',
'bootstrapform',
'raven.contrib.django.raven_compat',

'connector',
]

RAVEN_CONFIG = {
    'dsn': os.getenv('RAVEN_DSN'),
}

