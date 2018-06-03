"""
Django app development-specific settings
"""

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
