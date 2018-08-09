from .email_info import EMAIL_USE_TLS, EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_PORT

import os
import datetime
from django.conf import settings

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

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

if not settings.DEBUG:

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'storages',
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

    access_key = 'YourACCESS_KEYHere'
    secret_key = 'YourSECRET_ACCESS_KEYHere'
    AWS_ACCESS_KEY_ID = access_key
    AWS_SECRET_ACCESS_KEY = secret_key
    AWS_STORAGE_BUCKET_NAME = 'joinwikipedians'
    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

    S3_URL = 'http://' + AWS_STORAGE_BUCKET_NAME + '.s3.amazonaws.com/'
    MEDIA_URL = S3_URL + "media/"
    STATIC_URL = S3_URL + "static/"
    ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
    date_two_months_later = datetime.date.today() + datetime.timedelta(4 * 365 / 12)
    expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")
    AWS_HEADERS = {
        'Expires': expires,
        'Cache-Contral': 'max-age=86400',
    }

    # STATIC_ROOT = os.path.join(settings.BASE_DIR, "static", "static-only")
    # MEDIA_ROOT = os.path.join(settings.BASE_DIR, "static", "media")

    STATICFILES_DIRS = (
        os.path.join(settings.BASE_DIR, 'static'),
    )

    # Template location
    TEMPLATE_DIRS = (
        os.path.join(settings.BASE_DIR, "static", "templates"),

    )
