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

import os
# Extends context_processors
import django.conf.global_settings as DEFAULT_SETTINGS


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': BASE_DIR+'/data/ain7.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'fr'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = BASE_DIR + '/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/site_media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '*r9!#_dmg+vj01z8-^*j8(qn4tu^4taa-x_r+4wx+4-sz_1o9z'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'ain7.middleware.forcelocale.ForceDefaultLanguageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'ain7.middleware.useractivity.UserActivityMiddleware',
    'ain7.middleware.portalexceptions.PortalException',
    'django.contrib.messages.middleware.MessageMiddleware',
)


ROOT_URLCONF = 'ain7.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    BASE_DIR + '/templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'ain7.adhesions',
    'ain7.annuaire',
    'ain7.association',
    'ain7.emploi',
    'ain7.groups',
    'ain7.manage',
    'ain7.news',
    'ain7.organizations',
    'ain7.pages',
    'ain7.search_engine',
    'ain7.shop',
    'ain7.sondages',
    'ain7.voyages',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

#
# AIn7 specific settings
#

TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
    'ain7.context_processors.versions',
    'ain7.context_processors.piwik',
    'ain7.context_processors.user_groups',
)

# enable or disable applications
ADVANCEDSEARCH_ENABLED=False
SHOP_ENABLED=False
PIWIK_ENABLED=False

SERVER_EMAIL = 'AIn7 Web Portal <noreply@ain7.com>'
SMTP_HOST='localhost'
SMTP_PORT=25
SMTP_LOGIN=''
SMTP_PASSWORD=''
SMTP_TLS=False

# attributs non standards
SKIN = 'default'

PIWIK_URL = 'http://localhost/piwik/'
PIWIK_SITE_ID = '0'

# Version
BASE = '1.4.2a'
REVISION = ''

try:
    from bzrlib.branch import Branch
    bzr_branch = Branch.open(BASE_DIR + '/../')
    REVISION = 'r'+str(bzr_branch.revno())
except:
    pass

VERSION = BASE+REVISION

TINYMCE_VERSION = '3.3.8'


PORTAL_ADMIN = 'ain7-admin'

FACEBOOK_AIN7='http://www.facebook.com/ENSEEIHT'
LINKEDIN_AIN7='http://www.linkedin.com/groups?gid=73525'
TWITTER_AIN7='http://twitter.com/ENSEEIHT_Alumni'
VIADEO_AIN7='http://www.viadeo.com/communaute/macommunaute/?communityId=0022ezgr59190pqm'
GPLUS_AIN7='https://plus.google.com/s/enseeiht#105806841193732839789/posts'

SPPLUS_CLENT = '58 6d fc 9c 34 91 9b 86 3f fd 64 63 c9 13 4a 26 ba 29 74 1e c7 e9 80 79'
SPPLUS_EXE = '/bin/false'
SPPLUS_IP = ['127.0.0.1']

AIN7_SIRET = '0000000000000001-001'

ENVIRONMENT= 'production'

#HAYSTACK_SITECONF = 'ain7.search_sites'
#HAYSTACK_SEARCH_ENGINE = 'xapian'
#HAYSTACK_XAPIAN_PATH = BASE_DIR +'/data/xapian/'

# INSTALLED_APPS += ('haystack',)


try:
    from settings_local import *
except ImportError:
    pass

