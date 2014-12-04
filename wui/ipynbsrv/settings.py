"""
Django settings for ipynbsrv project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'uj^n9qt_dgbsb)+r7dbnx&+s6(*)b!i+gv&qrbrg159ixr!ax3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'ipynbsrv.wui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ifnav_templatetag',
    'widget_tweaks',
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

TEMPLATE_CONTEXT_PROCESSORS = {
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request", # needed by ifnav_templatetag
}

ROOT_URLCONF = 'ipynbsrv.urls'
WSGI_APPLICATION = 'ipynbsrv.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'ldap': {
        'ENGINE': 'ldapdb.backends.ldap',
        'NAME': 'ldap://192.168.65.178/',
        'USER': 'cn=admin,dc=ipynbsrv,dc=ldap',
        'PASSWORD': '123456',
    }
}
DATABASE_ROUTERS = ['ldapdb.router.Router']


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Messages
# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-MESSAGE_TAGS
MESSAGE_TAGS = {
    40: 'danger'
}


# URLs and filesystem paths
LOGIN_REDIRECT_URL = '/'
PUBLIC_URL = '/public/'
STATIC_URL = '/static/'

DATA_ROOT = '/srv/ipynbsrv/data/'
HOME_ROOT = os.path.join(DATA_ROOT, 'homes')
PUBLIC_ROOT = os.path.join(DATA_ROOT, 'public')
SHARE_ROOT = os.path.join(DATA_ROOT, 'shares')


# LDAP Authentication
import ldap
from django_auth_ldap.config import LDAPSearch, PosixGroupType


AUTH_LDAP_SERVER_URI = DATABASES['ldap']['NAME']
AUTH_LDAP_BIND_DN = DATABASES['ldap']['USER']
AUTH_LDAP_BIND_PASSWORD = DATABASES['ldap']['PASSWORD']

AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=ipynbsrv,dc=ldap",
    ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=groups,dc=ipynbsrv,dc=ldap",
    ldap.SCOPE_SUBTREE, "(objectClass=posixGroup)"
)
AUTH_LDAP_GROUP_TYPE = PosixGroupType()

AUTH_LDAP_USER_ATTR_MAP = {
    "uid": "uidNumber",
    "group": "gidNumber",
    "home_directory": "homeDirectory",
    "username": "uid",
    "password": "userPassword"
}

AUTH_LDAP_ALWAYS_UPDATE_USER = True
# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)
