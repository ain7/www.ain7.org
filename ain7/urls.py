# -*- coding: utf-8
#
# urls.py
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

import os.path

from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin                                                

from ain7.feeds import LatestsEvents, LatestsNews
from ain7.sitemaps import EventsSitemap, TextsSitemap, NewsSitemap, GroupsSitemap
from ain7.sitemaps import TravelsSitemap

feeds = {
    'events': LatestsEvents,
    'news': LatestsNews,
}

sitemaps = {
    'events': EventsSitemap,
    'news': NewsSitemap,
    'groups': GroupsSitemap,
    'voyages': TravelsSitemap,
    'texts': TextsSitemap,
}

urlpatterns = patterns('',

    (r'^~(?P<user_name>\w+)/$', 'ain7.annuaire.views.home'),

    #(r'^accounts/login/$', 'ain7.pages.views.login'),
    #(r'^accounts/logout/$', 'ain7.pages.views.logout'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'registration/login.html'}, name='login'),
    url(r'^acocunts/logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),

    # servir le contenu statique pendant le dev
    url(r'^static/(?P<path>.*)$', 'django.contrib.staticfiles.views.serve'),

    # AIn7 management section
    (r'^manage/', include('ain7.manage.urls')),

    # annuaire
    (r'^annuaire/', include('ain7.annuaire.urls')),

    # emploi
    (r'^emploi/', include('ain7.emploi.urls')),

    # news
    (r'^actualites/', include('ain7.news.urls')),
    # evenements
    (r'^evenements/', include('ain7.news.urls_events')),

    # groups
    (r'^groups/', include('ain7.groups.urls')),
 
    # organizations
    (r'^organizations/', include('ain7.organizations.urls')),

    # voyages
    (r'^voyages/', include('ain7.voyages.urls')),

    # association
    (r'^association/',include('ain7.association.urls')),

    # adhesions
    (r'^adhesions/',include('ain7.adhesions.urls')),

    # Pages particulieres au contenu pseudo statique
    (r'^apropos/$','ain7.pages.views.apropos'),
    (r'^mentions_legales/$','ain7.pages.views.mentions_legales'),
    (r'^lostpassword/$','ain7.pages.views.lostpassword'),
    (r'^lostpassword/([A-Za-z0-9.\-_]+)/$','ain7.pages.views.changepassword'),
    url(r'^$','ain7.pages.views.homepage', name='homepage'),

    # flux RSS
    url(r'^rss/$', 'ain7.pages.views.rss', name='rss'),
    (r'^rss/(?P<url>.*)/$', 'django.contrib.syndication.views.Feed', {'feed_dict': feeds}),

    (r'^ical/$', 'ain7.news.views.ical'),

    # Edit text blocks
    (r'^edit/(?P<text_id>.*)/$', 'ain7.pages.views.edit'),

    # sitemaps
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

    # redirection to external communities
    url(r'^facebook/$', 'ain7.pages.views.facebook', name='facebook'),
    url(r'^linkedin/$', 'ain7.pages.views.linkedin', name='linkedin'),
    url(r'^twitter/$', 'ain7.pages.views.twitter', name='twitter'),
    url(r'^viadeo/$', 'ain7.pages.views.viadeo', name='viadeo'),
    url(r'^g\+/$', 'ain7.pages.views.gplus', name='g+'),

    (r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    (r'^admin/',  include(admin.site.urls)), # admin site

)

