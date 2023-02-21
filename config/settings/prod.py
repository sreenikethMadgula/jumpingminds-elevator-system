from .base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'containers-us-west-76.railway.app',
        'NAME': 'elevators_test',
        'USER': 'postgres',
        'PASSWORD': 'yx34bwYPjz5VTTAc14nr',
        'PORT': 6137
    }
}