"""
This is a pre cvat settings file for use on a development machine
Place it at activebrainatlas/activebrainatlas/settings.py
"""
import os

from activebrainatlas.local_settings import SECRET_KEY, DATABASES

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['localhost']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_plotly_dash.apps.DjangoPlotlyDashConfig',
    'dpd_static_support',
    'background_task',
    'brain',
    'workflow',
    'neuroglancer',
    'rest_framework',
    'corsheaders',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_plotly_dash.middleware.BaseMiddleware',
    'django_plotly_dash.middleware.ExternalRedirectionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'activebrainatlas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR + '/templates/',],
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

WSGI_APPLICATION = 'activebrainatlas.wsgi.application'
ASGI_APPLICATION = 'activebrainatlas.asgi.application'



# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
#USER_ID = 1
INTERNAL_IPS = ['127.0.0.1']
SILENCED_SYSTEM_CHECKS = ['mysql.E001']

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Bangkok'
#TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
#USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
MEDIA_URL = '/share/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'share')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'assets'),)
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
         'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
         'rest_framework.authentication.SessionAuthentication',
         'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

LOGS_ROOT = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_ROOT, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'fileInfo': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_ROOT, "info.log"),
        },
        'fileDebug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_ROOT, "debug.log")
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'fileInfo', 'fileDebug'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
# dash/plotly stuff
X_FRAME_OPTIONS = 'SAMEORIGIN'

PLOTLY_COMPONENTS = [
    'dash_core_components',
    'dash_html_components',
    'dash_bootstrap_components',
    'dash_renderer',
    'dpd_components',
    'dpd_static_support',
]

##### django extensions graph models
GRAPH_MODELS = {
  'app_labels': ["brain", "neuroglancer",],
  'group_models': True,
}