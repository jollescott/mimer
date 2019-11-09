from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

sensitive = load_sensitve('production')
SECRET_KEY = sensitive['SECRET_KEY']
SANA_API_KEY = sensitive['SANA_API_KEY']
SANA_API_REGION = sensitive['SANA_API_REGION']

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': sensitive['DB_DATABASE'],
        'USER': sensitive['DB_USER'],
        'PASSWORD': sensitive['DB_PASSWORD'],
        'HOST': sensitive['DB_HOST'],
        'PORT': sensitive['DB_PORT']
    }
}
