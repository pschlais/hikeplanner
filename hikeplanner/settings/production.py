"""
Django app production-specific settings
"""

from .base import *

DEBUG = False

MIDDLEWARE_CLASSES = (
    # Simplified static file serving.
    # https://warehouse.python.org/project/whitenoise/
    'whitenoise.middleware.WhiteNoiseMiddleware',
                      )

ALLOWED_HOSTS = [".herokuapp.com"]
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True
X_FRAME_OPTIONS = "DENY"

# configure django app for Heroku
import django_heroku
django_heroku.settings(locals())
