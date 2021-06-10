# Copyright (C) 2018 Intel Corporation
#
# SPDX-License-Identifier: MIT

from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS += ['django_extensions',]

ALLOWED_HOSTS.append('testserver')


#INSTALLED_APPS += [    'mod_wsgi.server',]

NUCLIO['HOST'] = os.getenv('CVAT_NUCLIO_HOST', 'nuclio')

for key in RQ_QUEUES:
    RQ_QUEUES[key]['HOST'] = os.getenv('CVAT_REDIS_HOST', 'cvat_redis')

CACHEOPS_REDIS['host'] = os.getenv('CVAT_REDIS_HOST', 'cvat_redis')

# Django-sendfile:
# https://github.com/johnsensible/django-sendfile
SENDFILE_BACKEND = 'sendfile.backends.xsendfile'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '192.168.1.12',
        'NAME': 'cvat_db',
        'USER': 'cvat_user',
        'PASSWORD': 'cv54321#',
        'OPTIONS': {'sql_mode': 'traditional', 'init_command': 'SET storage_engine=INNODB;'},
    }
}
SILENCED_SYSTEM_CHECKS = ['mysql.E001']

# Cross-Origin Resource Sharing settings for CVAT UI
UI_SCHEME = os.environ.get('UI_SCHEME', 'http')
UI_HOST = os.environ.get('UI_HOST', 'localhost')
UI_PORT = os.environ.get('UI_PORT', 3000)
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [UI_HOST]
UI_URL = '{}://{}'.format(UI_SCHEME, UI_HOST)

if UI_PORT and UI_PORT != '80':
    UI_URL += ':{}'.format(UI_PORT)
# set UI url to redirect to after successful e-mail confirmation
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '{}/auth/login'.format(UI_URL)

CORS_ORIGIN_WHITELIST = [UI_URL]
CORS_REPLACE_HTTPS_REFERER = True
