"""
Django settings for AGOLAccountRequestor project.

Generated by 'django-admin startproject' using Django 2.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from . import local_settings
from django.utils.log import DEFAULT_LOGGING

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = local_settings.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = local_settings.DEBUG

ALLOWED_HOSTS = local_settings.ALLOWED_HOSTS

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_recaptcha',
    'django_filters',
    'oauth2_provider',
    'social_django',
    # 'drf_social_oauth2',
    'accounts'
] + local_settings.INSTALLED_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
] + local_settings.CORS_MIDDLEWARE + [
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'AGOLAccountRequestor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), os.path.join(BASE_DIR, 'accounts', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'AGOLAccountRequestor.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = local_settings.DATABASES

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = getattr(local_settings, 'STATIC_URL', '/request/static/')

#STATIC_ROOT = 'static'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
 )

MIGRATION_MODULES = {
    'oauth2_provider': 'oauth2_migrations'
}

AUTHENTICATION_BACKENDS = (
    'AGOLAccountRequestor.agol_auth.AGOLOAuth2',
    'django.contrib.auth.backends.ModelBackend'
)

OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = 'oauth2_provider.AccessToken'
OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth2_provider.Application'
OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL = 'oauth2_provider.RefreshToken'
OAUTH2_PROVIDER_ID_TOKEN_MODEL = "oauth2_provider.IDToken"

SOCIAL_AUTH_AGOL_DOMAIN = local_settings.SOCIAL_AUTH_AGOL_DOMAIN
SOCIAL_AUTH_AGOL_KEY = local_settings.SOCIAL_AUTH_AGOL_KEY
SOCIAL_AUTH_AGOL_SECRET = local_settings.SOCIAL_AUTH_AGOL_SECRET
SOCIAL_AUTH_REDIRECT_IS_HTTPS = getattr(local_settings, 'SOCIAL_AUTH_REDIRECT_IS_HTTPS', True)
SOCIAL_AUTH_PIPELINE = local_settings.SOCIAL_AUTH_PIPELINE
SOCIAL_AUTH_AGOL_PREAPPROVED_DOMAINS = getattr(local_settings, 'SOCIAL_AUTH_AGOL_PREAPPROVED_DOMAINS', [])
SOCIAL_AUTH_AGOL_UNKNOWN_REQUESTER_GROUP_ID = getattr(local_settings, 'SOCIAL_AUTH_AGOL_UNKNOWN_REQUESTER_GROUP_ID', 0)
SOCIAL_AUTH_ALLOWED_REDIRECT_HOSTS = getattr(local_settings, 'SOCIAL_AUTH_ALLOWED_REDIRECT_HOSTS', [])

REST_FRAMEWORK = local_settings.REST_FRAMEWORK

DRF_RECAPTCHA_SECRET_KEY = local_settings.DRF_RECAPTCHA_SECRET_KEY

CORS_ORIGIN_WHITELIST = local_settings.CORS_ORIGIN_WHITELIST
CORS_ALLOW_CREDENTIALS = getattr(local_settings, 'CORS_ALLOW_CREDENTIALS', False)

EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = local_settings.SENDGRID_API_KEY
SENDGRID_SANDBOX_MODE_IN_DEBUG = local_settings.SENDGRID_SANDBOX_MODE_IN_DEBUG

LOGGING = DEFAULT_LOGGING

LOGGING['handlers']['slack'] = {
    'level': 'ERROR',
    'filters': ['require_debug_false'],
    'class': 'slack_logging.SlackExceptionHandler',
    'bot_token': getattr(local_settings.SLACK_LOGGING, 'SLACK_BOT_TOKEN', ''),
    'channel_id': getattr(local_settings.SLACK_LOGGING, 'SLACK_CHANNEL', '')
}

LOGGING['handlers']['file'] = {
    'level': 'ERROR',
    'filters': ['require_debug_false'],
    'class': 'logging.FileHandler',
    'filename': os.path.join(BASE_DIR, 'error.log')
}

LOGGING['loggers']['django'] = {
    'handlers': ['console', 'slack', 'file'],
    'level': 'INFO',
}
LOGGING['loggers']['R9DMT'] = {
    'handlers': ['console', 'slack', 'file'],
    'level': 'ERROR',
}


USE_X_FORWARDED_HOST = getattr(local_settings, 'USE_X_FORWARDED_HOST', False)
URL_PREFIX = getattr(local_settings, 'URL_PREFIX', '')
LOGIN_REDIRECT_URL = f'/{URL_PREFIX}api/admin/'
LOGIN_URL = f'/{URL_PREFIX}api/admin/'

INTERNAL_IPS = getattr(local_settings, 'INTERNAL_IPS', [])
HOST_ADDRESS = getattr(local_settings, 'HOST_ADDRESS', '')

COORDINATOR_ADMIN_GROUP_ID = getattr(local_settings, 'COORDINATOR_ADMIN_GROUP_ID', 0)

CSRF_COOKIE_NAME = 'requestcsrftoken'
