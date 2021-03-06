"""
Django app production-specific settings
"""

from .base import *

DEBUG = False

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_FROM_EMAIL = 'webmaster@adventurersportal.herokuapp.com'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ.get("SENDGRID_SMTP_USERNAME")
EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_SMTP_API_KEY")
EMAIL_PORT = 587
EMAIL_USE_TLS = True

ALLOWED_HOSTS = ["localhost", ".herokuapp.com"]
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True
X_FRAME_OPTIONS = "DENY"

# configure django app for Heroku
import django_heroku
import dj_database_url
DATABASE_URL = os.environ.get("DATABASE_URL")
DATABASES = {}
DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)
django_heroku.settings(locals())
