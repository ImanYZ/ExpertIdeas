import os
import sys
import datetime
from django.conf import settings

if not '/opt/python/run/venv/lib/python2.7/site-packages/pytzwhere' in sys.path:
    sys.path.append('/opt/python/run/venv/lib/python2.7/site-packages/pytzwhere')

from geopy import geocoders
from tzwhere import tzwhere

GEOCODEROBJ = geocoders.GoogleV3()
TZWHEREOBJ = tzwhere.tzwhere()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = DEBUG

ADMINS = (('Admin_ID_Here', 'YourEmailAddressHere'), ('Second_Admin_ID_Here', 'YourEmailAddressHere'))
MANAGERS = (('Manager_ID_Here', 'YourEmailAddressHere'), ('Second_Manager_ID_Here', 'YourEmailAddressHere'))

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'JoinWikipedians.urls'

WSGI_APPLICATION = 'JoinWikipedians.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_REDIRECT_URL = '/'

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

# if DEBUG:

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ExpertIdeas',
)

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['RDS_DB_NAME'],
        'USER': os.environ['RDS_USERNAME'],
        'PASSWORD': os.environ['RDS_PASSWORD'],
        'HOST': os.environ['RDS_HOSTNAME'],
        'PORT': os.environ['RDS_PORT'],
    }
}

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(settings.BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'static', 'media')
MEDIA_URL = '/media/'

SMEDIA_DIRS = (
    os.path.join(settings.BASE_DIR, 'static', "media"),
)

STATICFILES_DIRS = (
    os.path.join(settings.BASE_DIR, 'static', "static"),
)

# Template location
TEMPLATE_DIRS = (
    os.path.join(settings.BASE_DIR, "static", "templates"),
)
