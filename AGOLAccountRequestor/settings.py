"""
Django settings for AGOLAccountRequestor project.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from django.utils.log import DEFAULT_LOGGING
import json
from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'sssssh-its-a-secret')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',') if 'ALLOWED_HOSTS' in os.environ else []

# Application definition

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_recaptcha',
    'django_filters',
    'social_django',
    # 'drf_social_oauth2',
    'rangefilter',
    'django_admin_listfilter_dropdown',
    'django_ckeditor_5',
    'accounts'
]
INSTALLED_APPS += os.environ.get('INSTALLED_APPS', '').split(',') if os.environ.get('INSTALLED_APPS') else []

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
] + (os.environ.get('CORS_MIDDLEWARE', '').split(',') if 'CORS_MIDDLEWARE' in os.environ else []) + [
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'AGOLAccountRequestor.views.redirect_middleware'
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
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


if 'DATABASES' in os.environ:
    DATABASES = json.loads(os.environ.get('DATABASES', '{}').replace("'", '"'))
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = os.environ.get('STATIC_URL', 'static/')

STATIC_ROOT = 'static'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, '_static'),
 )


AUTHENTICATION_BACKENDS = (
    'AGOLAccountRequestor.agol_auth.AGOLOAuth2Geoplatform',
    'AGOLAccountRequestor.agol_auth.AGOLOAuth2Geosecure',
    'django.contrib.auth.backends.ModelBackend'
)

DISABLE_PASSWORD_AUTH = os.environ.get('DISABLE_PASSWORD_AUTH', False) == 'True'

SOCIAL_AUTH_GEOPLATFORM_DOMAIN = os.environ.get('SOCIAL_AUTH_GEOPLATFORM_DOMAIN')
SOCIAL_AUTH_GEOPLATFORM_KEY = os.environ.get('SOCIAL_AUTH_GEOPLATFORM_KEY')
SOCIAL_AUTH_GEOPLATFORM_SECRET = os.environ.get('SOCIAL_AUTH_GEOPLATFORM_SECRET')
SOCIAL_AUTH_GEOSECURE_DOMAIN = os.environ.get('SOCIAL_AUTH_GEOSECURE_DOMAIN')
SOCIAL_AUTH_GEOSECURE_KEY = os.environ.get('SOCIAL_AUTH_GEOSECURE_KEY')
SOCIAL_AUTH_GEOSECURE_SECRET = os.environ.get('SOCIAL_AUTH_GEOSECURE_SECRET')
SOCIAL_AUTH_REDIRECT_IS_HTTPS = os.environ.get('SOCIAL_AUTH_REDIRECT_IS_HTTPS', True) == True
SOCIAL_AUTH_PIPELINE = [  # Note: Sequence of functions matters here.
    'social_core.pipeline.social_auth.social_details',  # 0
    'social_core.pipeline.social_auth.social_uid',  # 1
    'social_core.pipeline.social_auth.auth_allowed',  # 2
    'social_core.pipeline.social_auth.social_user',  # 3
    'social_core.pipeline.user.get_username',  # 4
    # 'social_core.pipeline.social_auth.associate_by_email',  # 5 need custom associate method
    'AGOLAccountRequestor.agol_auth.associate_by_username',
    'AGOLAccountRequestor.agol_auth.create_accounts_for_preapproved_domains',
    'social_core.pipeline.social_auth.associate_user',  # 6
    'social_core.pipeline.social_auth.load_extra_data',  # 7
    'social_core.pipeline.user.user_details',  # 8
]
SOCIAL_AUTH_GEOPLATFORM_PREAPPROVED_DOMAINS = os.environ.get('SOCIAL_AUTH_GEOPLATFORM_PREAPPROVED_DOMAINS', [])
SOCIAL_AUTH_GEOPLATFORM_UNKNOWN_REQUESTER_GROUP_ID = os.environ.get('SOCIAL_AUTH_GEOPLATFORM_UNKNOWN_REQUESTER_GROUP_ID', 0)
SOCIAL_AUTH_GEOSECURE_PREAPPROVED_DOMAINS = os.environ.get('SOCIAL_AUTH_GEOPLATFORM_PREAPPROVED_DOMAINS', [])
SOCIAL_AUTH_GEOSECURE_UNKNOWN_REQUESTER_GROUP_ID = os.environ.get('SOCIAL_AUTH_GEOPLATFORM_UNKNOWN_REQUESTER_GROUP_ID', 0)
SOCIAL_AUTH_ALLOWED_REDIRECT_HOSTS = os.environ.get('SOCIAL_AUTH_ALLOWED_REDIRECT_HOSTS', '').split(',') if 'SOCIAL_AUTH_ALLOWED_REDIRECT_HOSTS' in os.environ else []
SOCIAL_AUTH_IMMUTABLE_USER_FIELDS = os.environ.get('SOCIAL_AUTH_IMMUTABLE_USER_FIELDS ', '').split(',') if 'SOCIAL_AUTH_IMMUTABLE_USER_FIELDS ' in os.environ else []

REST_FRAMEWORK = json.loads(os.environ.get('REST_FRAMEWORK', '{}').replace("'", '"'))

DRF_RECAPTCHA_SECRET_KEY = os.environ.get('DRF_RECAPTCHA_SECRET_KEY', 'fakey')
DRF_RECAPTCHA_MINIMUM_SCORE = float(os.environ.get('DRF_RECAPTCHA_MINIMUM_SCORE', '1.0'))


CORS_ORIGIN_WHITELIST = os.environ.get('CORS_ORIGIN_WHITELIST', '').split(',') if 'CORS_ORIGIN_WHITELIST' in os.environ else []
CORS_ALLOW_CREDENTIALS = os.environ.get('CORS_ALLOW_CREDENTIALS', False) == 'True'

CSRF_COOKIE_NAME = 'requestcsrftoken'
CSRF_COOKIE_DOMAIN = os.environ.get('CSRF_COOKIE_DOMAIN', '')
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if 'CSRF_TRUSTED_ORIGINS' in os.environ else CORS_ORIGIN_WHITELIST

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'geoservices@epa.gov')

ADMINS = json.loads(os.environ.get('ADMINS', '[]'))
SERVER_EMAIL = "noreply@epa.gov"

LOGGING = DEFAULT_LOGGING

LOGGING['handlers']['mail_admins'] = {
    'level': 'ERROR',
    'filters': ['require_debug_false'],
    "class": "django.utils.log.AdminEmailHandler",
    "include_html": False,
}

LOGGING['handlers']['file'] = {
    'level': 'ERROR',
    'filters': ['require_debug_false'],
    'class': 'logging.FileHandler',
    'filename': os.path.join(BASE_DIR, 'error.log')
}

LOGGING['loggers']['django'] = {
    'handlers': ['console', 'mail_admins', 'file'],
    'level': 'INFO',
}



USE_X_FORWARDED_HOST = os.environ.get('USE_X_FORWARDED_HOST', False)
URL_PREFIX = os.environ.get('URL_PREFIX', '')
LOGIN_REDIRECT_URL = f'/{URL_PREFIX}api/admin/'
LOGIN_URL = f'/{URL_PREFIX}api/admin/'

INTERNAL_IPS = os.environ.get('INTERNAL_IPS', '').split(',') if 'INTERNAL_IPS' in os.environ else []
HOST_ADDRESS = os.environ.get('HOST_ADDRESS', '')

COORDINATOR_ADMIN_GROUP_ID = os.environ.get('COORDINATOR_ADMIN_GROUP_ID', 0)

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'sourceEditing' ],

    }
}
CKEDITOR_5_CUSTOM_CSS = 'editor.css'
