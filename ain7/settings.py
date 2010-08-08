# -*- coding: utf-8
"""
 ain7/settings.py
"""
#
#   Copyright © 2007-2010 AIn7 Devel Team
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


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Django settings for ain7 project.

DEFAULT_CHARSET = 'utf-8'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SERVER_EMAIL = 'AIn7 Web Portal <noreply@ain7.com>'
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = BASE_DIR + '/data/ain7.db'      # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'fr'

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = BASE_DIR + '/media'

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/site_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '*r9!#_dmg+vj01z8-^*j8(qn4tu^4taa-x_r+4wx+4-sz_1o9z'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
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
)

ROOT_URLCONF = 'ain7.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
    '/usr/share/python-support/python-django/django/contrib/admin/templates',
    BASE_DIR + '/templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.admin',
    'ain7.adhesions',
    'ain7.annuaire',
    'ain7.association',
    'ain7.emploi',
    'ain7.groups',
    'ain7.groupes_professionnels',
    'ain7.groupes_regionaux',
    'ain7.manage',
    'ain7.news',
    'ain7.pages',
    'ain7.sondages',
    'ain7.voyages',
    'ain7.search_engine',
)

# attributs non standards
SKIN = 'default'
FORUMS_URL = 'http://forums.ain7.info/'
GALLERY_URL = 'http://gallery.ain7.info/'

PIWIK_URL = 'http://localhost/piwik/'
PIWIK_SITE_ID = '0'

# Version
BASE = '1.2.3'
REVISION = ''

try:
    from bzrlib.branch import Branch
    bzr_branch = Branch.open(BASE_DIR + '/../')
    REVISION = 'r'+str(bzr_branch.revno())
except:
    pass

VERSION = BASE+REVISION

TINYMCE_VERSION = '3.2.7'

MOOTOOLS_VERSION = '1.2.4'
MOOTOOLS_MORE_VERSION = '1.2.4.2'

JQUERY_VERSION = '1.4.2'

AIN7_PORTAL_ADMIN = 'ain7-admin'

SPPLUS_CLENT = '58 6d fc 9c 34 91 9b 86 3f fd 64 63 c9 13 4a 26 ba 29 74 1e c7 e9 80 79'
SPPLUS_EXE = '/bin/false'
SPPLUS_IP = ['127.0.0.1']

AIN7_SIRET = '0000000000000001-001'

ENVIRONMENT= 'production'

try:
    from settings_local import *
except ImportError:
    pass

