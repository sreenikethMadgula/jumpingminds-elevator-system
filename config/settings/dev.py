from .base import *
DEBUG = True


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'elevators_test',
        'USER': 'user1',
        'PASSWORD': 'password'
    }
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'HOST': 'containers-us-west-76.railway.app',
    #     'NAME': 'railway',
    #     'USER': 'postgres',
    #     'PASSWORD': 'yx34bwYPjz5VTTAc14nr',
    #     'PORT': 6137
    # }
}
