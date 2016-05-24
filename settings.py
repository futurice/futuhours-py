import os, sys
# BASE SETTINGS
import django.conf.global_settings as DEFAULT_SETTINGS
# SETTINGS
here = lambda x: os.path.join(os.path.abspath(os.path.dirname(__file__)), x)

ROOT = os.path.dirname(os.path.realpath(__file__))
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['*']
ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            here('.'),
            os.path.join(os.path.dirname(__file__), "templates"),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]
        },
    },
]

SECRET_KEY = os.getenv('SECRET_KEY', 'verysecret')
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    here('static'),
)

INSTALLED_APPS = [
'django.contrib.contenttypes',
'django.contrib.auth',
'django.contrib.admin',
'django.contrib.sessions',

'hours',
'bootstrapform',

'connector',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s',
        },
        'default': {
            'format': '%(levelname)s %(message)s',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'stream': sys.stdout,
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

RAVEN_CONFIG = {
    'dsn': os.getenv('RAVEN_DSN'),
}

if not DEBUG:
    INSTALLED_APPS = INSTALLED_APPS + [
        'raven.contrib.django.raven_compat',
    ]
