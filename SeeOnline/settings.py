import os
from pathlib import Path

import environ

import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Инициализируем переменные окр
env = environ.Env()
env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    env.read_env(env_file)

# Тут секрет кей
SECRET_KEY = env('SECRET_KEY', default='some-fallback-value')  # Or raise an error if missing

# Это дебаг
DEBUG = env.bool('DEBUG', default=False)

# If ALLOWED_HOSTS is a comma-separated string in .env, you could parse it here:
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['127.0.0.1'])

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'rest_framework',
    'django_filters',
    'drf_spectacular',
    'django_prometheus',
    'tracker',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tracker.middleware.RequestLogMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware'
]

ROOT_URLCONF = 'SeeOnline.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'SeeOnline.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django_prometheus.db.backends.postgresql',
        'NAME': env('POSTGRES_DB', default='seeonline'),
        'USER': env('POSTGRES_USER', default='postgres'),
        'PASSWORD': env('POSTGRES_PASSWORD', default=''),
        'HOST': env('POSTGRES_HOST', default='localhost'),
        'PORT': env('POSTGRES_PORT', default='5432'),
    }
}

# На будущее для кэшэй с кастомным двишком от прометеуса для сбора метрик(перед испльзование установить django_redis)
# CACHES = {
#     'default': {
#         'BACKEND': 'django_prometheus.cache.backends.redis.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#     }
# }


LOG_DIR = BASE_DIR / 'logs'

LOG_DIR.mkdir(exist_ok=True)  # На всякий случай создадим папку, если ее нет

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'json': {
            'format': json.dumps({
                "time": "%(asctime)s",
                "level": "%(levelname)s",
                "message": "%(message)s",
                "name": "%(name)s"
            }),
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'app.log',
            'formatter': 'json',
        },
    },

    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'tracker': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'tracker.tasks': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'celery': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

# DRF Settings
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# drf-spectacular
SPECTACULAR_SETTINGS = {
    'TITLE': 'Tracker API',
    'DESCRIPTION': 'Документация API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'operationsSorter': 'method',
        'tagsSorter': 'alpha',
        'deepLinking': True,
        'defaultModelRendering': 'model',
        'defaultModelsExpandDepth': 1,
        'defaultModelExpandDepth': 2,
        'displayRequestDuration': True,
    },
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
}

# Redis
REDIS_HOST = env("REDIS_HOST", default="localhost")

# Celery
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{6379}/{env('CELERY_BROKER_DB', default='0')}"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{6379}/{env('CELERY_RESULT_DB', default='0')}"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'
CELERY_ENABLE_UTC = True

# Default Checker Settings
MANAGER_CHECK_INTERVAL = 5.0

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
