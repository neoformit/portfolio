"""Portfolio production settings."""

# flake8: noqa

from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'stocks.neoformit.com',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'portfolio',
        'USER': 'portfolio',
        'PASSWORD': 'f475y4i85467',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '{levelname} | {asctime} | {module}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'delay': True,
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 10000000,  # 10MB ~ 200k rows
            'backupCount': 5,
            'filename': BASE_DIR / 'portfolio/logs/main.log',
            'formatter': 'verbose',
        },
        'error_file': {
            'delay': True,
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 10000000,  # 10MB ~ 200k rows
            'backupCount': 5,
            'filename': BASE_DIR /'portfolio/logs/error.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'INFO',
        },
    },
}

STATIC_ROOT = BASE_DIR / 'portfolio/static'
