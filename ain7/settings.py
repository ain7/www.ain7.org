# -*- coding: utf-8
"""
 ain7/settings.py
"""
#
#   Copyright © 2007-2015 AIn7 Devel Team
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#

import django.conf.global_settings as DEFAULT_SETTINGS

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '45@qqvbavfu*3)@e6vs#z8tp0_l^q^)aota0)2_lw^fh(96rim'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['www.ain7.com', 'ain7.com', 'www.ain7.org', 'ain7.org']

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'grappelli',
)

MIDDLEWARE_CLASSES = (
    'ain7.middleware.forcelocale.ForceDefaultLanguageMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'ain7.urls'

WSGI_APPLICATION = 'ain7.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_URL = '/static/'
MEDIA_URL = '/site_media/'

#
# Added for this project
#

TEMPLATE_DIRS = DEFAULT_SETTINGS.TEMPLATE_DIRS + (
    # Put strings here, like "/home/html/django_templates"
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    BASE_DIR + '/ain7/templates',
)

TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
)


DEFAULT_FROM_EMAIL = 'AIn7 <noreply@ain7.com>'

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# EMAIL_FILE_PATH = '/tmp/app-messages'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

SITE_ID = 1

# autocomplete_light
INSTALLED_APPS += (
    'autocomplete_light',
)

# celery configuration
BROKER_URL = 'redis://localhost:6379/0'
CELERY_IMPORTS = ("ain7.tasks",)

# endless configuration
INSTALLED_APPS += (
    'endless_pagination',
)
ENDLESS_PAGINATION_PER_PAGE = 25

# django-crispy-forms
INSTALLED_APPS += (
    'crispy_forms',
)
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# auth and allauth settings
INSTALLED_APPS += (
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
#    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
#    'allauth.socialaccount.providers.linkedin',
)
AUTHENTICATION_BACKENDS = DEFAULT_SETTINGS.AUTHENTICATION_BACKENDS + (
    'allauth.account.auth_backends.AuthenticationBackend',
)
TEMPLATE_CONTEXT_PROCESSORS += (
    'allauth.account.context_processors.account',
    'allauth.socialaccount.context_processors.socialaccount',
    'ain7.context_processors.piwik',
    'ain7.context_processors.user_groups',
)


LOGIN_REDIRECT_URL = '/'
SOCIALACCOUNT_QUERY_EMAIL = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'}
    }
}

# AIn7 specific stuff

INSTALLED_APPS += (
    'ain7',
    'ain7.adhesions',
    'ain7.annuaire',
    'ain7.association',
    'ain7.emploi',
    'ain7.groups',
    'ain7.manage',
    'ain7.news',
    'ain7.organizations',
    'ain7.pages',
    'ain7.shop',
    'ain7.voyages',
)

MIDDLEWARE_CLASSES += (
    'ain7.middleware.useractivity.UserActivityMiddleware',
    'ain7.middleware.forcelocale.ForceDefaultLanguageMiddleware',
    'ain7.middleware.portalexceptions.PortalException',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'ain7.context_processors.piwik',
    'ain7.context_processors.user_groups',
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'ain7', 'static'),
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'ain7', 'media')
#STATIC_ROOT = os.path.join(BASE_DIR, 'ain7', 'static')

PIWIK_ENABLED = False
PIWIK_URL = 'http://localhost/piwik/'
PIWIK_SITE_ID = '0'

PORTAL_ADMIN = 'ain7-admin'
AIN7_MEMBERS = 'ain7-membre'
AIN7_CONTRIBUTORS = 'ain7-contributor'

FACEBOOK_AIN7 = 'http://www.facebook.com/ENSEEIHT'
LINKEDIN_AIN7 = 'http://www.linkedin.com/groups?gid=73525'
TWITTER_AIN7 = 'http://twitter.com/ENSEEIHT_Alumni'
GPLUS_AIN7 = 'https://plus.google.com/s/enseeiht#105806841193732839789/posts'

SYSTEM_PAY_URL = 'http://localhost'
SYSTEM_PAY_SITE_ID = '123456789'
SYSTEM_PAY_CERTIFICATE = '1234567890912345'
SYSTEM_PAY_MODE = 'TEST'

AIN7_SIRET = '0000000000000001-001'

from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {
    message_constants.ERROR: 'danger',
}

try:
    from settings_local import *
except ImportError:
    pass
