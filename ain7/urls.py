# -*- coding: utf-8
#
# urls.py
#
#   Copyright © 2007-2016 AIn7 Devel Team
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

from django.conf.urls import include, patterns, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.views.generic.base import RedirectView

import autocomplete_light

from ain7.feeds import NewsFeed
from ain7.sitemaps import (
    EventsSitemap, TextsSitemap, NewsSitemap, GroupsSitemap
)
from ain7.sitemaps import TravelsSitemap

autocomplete_light.autodiscover()

sitemaps = {
    'events': EventsSitemap,
    'news': NewsSitemap,
    'groups': GroupsSitemap,
    'voyages': TravelsSitemap,
    'texts': TextsSitemap,
}

urlpatterns = patterns('',

    url(r'^~(?P<user_name>\w+)/$', 'ain7.annuaire.views.home'),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'template_name': 'registration/login.html'}, name='account_login'),
    url(r'^acocunts/logout/$', 'django.contrib.auth.views.logout_then_login',
        name='account_logout'),
    #url(r'^accounts/', include('allauth.urls')),

    (r'^me/$', 'ain7.annuaire.views.me'),

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
    (r'^association/', include('ain7.association.urls')),

    # adhesions
    (r'^adhesions/', include('ain7.adhesions.urls')),

    url(r'^welcome/', 'ain7.annuaire.views.welcome'),

    # Pages particulieres au contenu pseudo statique
    (r'^apropos/$', 'ain7.pages.views.apropos'),
    (r'^mentions_legales/$', 'ain7.pages.views.mentions_legales'),
    url(r'^lostpassword/$', 'ain7.pages.views.lostpassword', name='lostpassword'),
    (r'^lostpassword/([A-Za-z0-9.\-_]+)/$', 'ain7.pages.views.changepassword'),
    url(r'^$', 'ain7.pages.views.homepage', name='homepage'),

    # flux RSS
    url(r'^rss/$', NewsFeed(), name='rss'),

    (r'^ical/$', 'ain7.news.views.ical'),

    # Edit text blocks
    url(r'^edit/(?P<text_id>.*)/$', 'ain7.pages.views.edit', name='text-edit'),

    # sitemaps
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap',
        {'sitemaps': sitemaps}),

    url(r'^groupes_professionnels/$', 'ain7.pages.views.professionnal_groups', name='professionnal_groups'),
    url(r'^groupes_regionaux/$', 'ain7.pages.views.regional_groups', name='regional_groups'),

    # redirection to external communities
    url(r'^facebook/$', RedirectView.as_view(url=settings.FACEBOOK_AIN7, permanent=True), name='facebook'),
    url(r'^linkedin/$', RedirectView.as_view(url=settings.LINKEDIN_AIN7, permanent=True), name='linkedin'),
    url(r'^twitter/$', RedirectView.as_view(url=settings.TWITTER_AIN7, permanent=True), name='twitter'),
    url(r'^g\+/$', RedirectView.as_view(url=settings.GPLUS_AIN7, permanent=True), name='g+'),

    # django-autocomplete-light
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    (r'^grappelli/', include('grappelli.urls')),  # grappelli URLS
    (r'^admin/',  include(admin.site.urls)),  # admin site

    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),

)
