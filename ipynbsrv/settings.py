'''
Django settings for acd project.

Generated by 'django-admin startproject' using Django 1.8.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
'''

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'uz*_q8s-z!y7=t5mg$x*zau%0eu6-zmp-(j5!rih-cd79t4-#v'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = (
    # Core
    'ipynbsrv.core',
    'django_admin_conf_vars',
    # API
    'ipynbsrv.api',
    'rest_framework',
    # Admin
    'ipynbsrv.admin.apps.MyAdmin',
    'djangocms_admin_style',
    'django.contrib.admin',
    'django.contrib.admindocs',
    # Web
    'ipynbsrv.web',
    'widget_tweaks',
    # Django
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'ipynbsrv.urls'

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
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ipynbsrv.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'production': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ipynbsrv',
        'USER': 'ipynbsrv',
        'PASSWORD': '123456',
        'HOST': 'ipynbsrv_postgresql',
        'PORT': '5432'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = 'static'

# Messages
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-MESSAGE_TAGS
MESSAGE_TAGS = {
    40: 'danger'
}


# LEGACY SETTINGS FROM OLD IPYNBSRV. NEEDS REFACTORING
LOGIN_URL = '/accounts/login'
LOGIN_REDIRECT_URL = '/accounts/flag'
PUBLIC_URL = '/public/'

VARS_MODULE_PATH = 'ipynbsrv.core.conf'


AUTHENTICATION_BACKENDS = (
    'ipynbsrv.core.auth.authentication_backends.BackendProxyAuthentication',
    'django.contrib.auth.backends.ModelBackend',
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}
