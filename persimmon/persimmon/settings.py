"""
Django settings for persimmon project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
import sys
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ENVFILE = BASE_DIR.parent / 'prod_creds.txt'
if ENVFILE.exists():
    with open(ENVFILE) as fp:
        for line in fp:
            if line.startswith('export '):
                key, val = line[7:].split('=', 1)
                val = val.strip("'")
                os.environ[key] = val

SECRET_KEY = os.getenv("SECRET_KEY", 'DO NOT USE DO NOT USE DO NOT USE')

DEBUG = os.getenv("DJANGO_DEBUG", "").lower() in ('1', 'true')
if sys.argv[0].endswith('manage.py') and sys.argv[1] == 'runserver':
    DEBUG = True

if sys.argv[0].endswith('manage.py') and sys.argv[1] == 'runserver':
    ALLOWED_HOSTS = ['testserver',
                     '127.0.0.1',
                     'localhost']
else:
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "persimmon.rhelmot.io").split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'website.apps.WebsiteConfig',
    'bootstrap_datepicker_plus',
    'bootstrap4'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'persimmon.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'website.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'persimmon.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.parse(os.getenv("DATABASE_URL", f'sqlite:///{BASE_DIR / "db.sqlite3"}'))
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Phoenix'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR.parent / 'staticfiles'

BOOTSTRAP4 = {
    'include_jquery': True,
}

# service integration

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", 'django.core.mail.backends.console.EmailBackend')
EMAIL_SENDER = os.getenv("EMAIL_SENDER", 'Persimmon Banking Team <noreply@persimmon.rhelmot.io>')
DEFAULT_FROM_EMAIL = EMAIL_SENDER

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "0"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "").lower() in ("true", "1")

SMS_BACKEND = os.getenv("SMS_BACKEND", 'sms.backends.console.SmsBackend')
if sys.argv[0].endswith('manage.py') and sys.argv[1] == 'test':
    SMS_BACKEND = 'sms.backends.locmem.SmsBackend'
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
SMS_SENDER = os.getenv("SMS_SENDER", '+15017122661')
