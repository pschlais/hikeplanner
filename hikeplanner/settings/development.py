"""
Django app development-specific settings
"""
import os
from .base import *

DEBUG = True

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get("HIKEPLANNER_DB_NAME"),
        'USER': os.environ.get("HIKEPLANNER_DB_USERNAME"),
        'PASSWORD': os.environ.get("HIKEPLANNER_DB_PASSWORD"),
    }
}

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ.get("SENDGRID_SMTP_USERNAME")
EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_SMTP_API_KEY")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
