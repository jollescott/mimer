from .base import * 

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

sensitive = load_sensitve('local')
SECRET_KEY = sensitive['SECRET_KEY']
SANA_API_KEY = sensitive['SANA_API_KEY']
SANA_API_REGION = sensitive['SANA_API_REGION']
