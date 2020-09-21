# Copyright (C) 2018 Intel Corporation
#
# SPDX-License-Identifier: MIT

from .base import *

#ALLOWED_HOSTS = ['localhost:3000']
ALLOWED_HOSTS = ['*']
DEBUG = True

#INSTALLED_APPS += ['mod_wsgi.server',]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
#'Access-Control-Allow-Origin' header in the response must not be the wildcard '*'
#CORS_ALLOWED_ORIGINS = ["http://localhost:3000","http://127.0.0.1"]



#NUCLIO['HOST'] = os.getenv('CVAT_NUCLIO_HOST', 'nuclio')

for key in RQ_QUEUES:
    RQ_QUEUES[key]['HOST'] = os.getenv('CVAT_REDIS_HOST', 'localhost')

CACHEOPS_REDIS['host'] = os.getenv('CVAT_REDIS_HOST', 'localhost')

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
