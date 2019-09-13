from .base import * 

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['mimer-test.herokuapp.com']

sensitive = load_sensitve('production')
SECRET_KEY = sensitive['SECRET_KEY']
SANA_API_KEY = sensitive['SANA_API_KEY']
SANA_API_REGION = sensitive['SANA_API_REGION']
