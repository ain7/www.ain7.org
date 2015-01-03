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


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

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
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'autocomplete_light',
    'crispy_forms',
    'endless_pagination',
    'grappelli',
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

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ain7.middleware.forcelocale.ForceDefaultLanguageMiddleware',
#    'ain7.middleware.useractivity.UserActivityMiddleware',
    'ain7.middleware.forcelocale.ForceDefaultLanguageMiddleware',
    'ain7.middleware.portalexceptions.PortalException',
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

#
# Added for this project
#

TEMPLATE_DIRS = DEFAULT_SETTINGS.TEMPLATE_DIRS + (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    BASE_DIR + '/ain7/templates',
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'ain7', 'static'),
)

TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
    'ain7.context_processors.piwik',
    'ain7.context_processors.user_groups',
)

PIWIK_ENABLED = False

SERVER_EMAIL = 'AIn7 Web Portal <noreply@ain7.com>'
SMTP_HOST = 'localhost'
SMTP_PORT = 2525
SMTP_LOGIN = ''
SMTP_PASSWORD = ''
SMTP_TLS = False

ENDLESS_PAGINATION_PER_PAGE = 25

PIWIK_URL = 'http://localhost/piwik/'
PIWIK_SITE_ID = '0'

PORTAL_ADMIN = 'ain7-admin'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

FACEBOOK_AIN7 = 'http://www.facebook.com/ENSEEIHT'
LINKEDIN_AIN7 = 'http://www.linkedin.com/groups?gid=73525'
TWITTER_AIN7 = 'http://twitter.com/ENSEEIHT_Alumni'
VIADEO_AIN7 = 'http://www.viadeo.com/communaute/macommunaute/?communityId=0022ezgr59190pqm'
GPLUS_AIN7 = 'https://plus.google.com/s/enseeiht#105806841193732839789/posts'

SYSTEM_PAY_URL = 'http://localhost'
SYSTEM_PAY_SITE_ID = '123456789'
SYSTEM_PAY_CERTIFICATE = '1234567890912345'
SYSTEM_PAY_MODE = 'TEST'

AIN7_SIRET = '0000000000000001-001'

BROKER_URL = 'redis://localhost:6379/0'
CELERY_IMPORTS = ("ain7.tasks",)

try:
    from settings_local import *
except ImportError:
    pass
