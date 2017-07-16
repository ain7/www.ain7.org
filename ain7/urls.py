# -*- coding: utf-8
#
# urls.py
#
#   Copyright © 2007-2017 AIn7 Devel Team
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

from django.conf.urls import include, url
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps import views as sitemaps_views
from django.views.generic.base import RedirectView
from django.views import static as views_static

from autocomplete_light import shortcuts as autocomplete_light

from ain7.annuaire import views as annuaire_views
from ain7.feeds import NewsFeed
from ain7.news import views as news_views
from ain7.pages import views as pages_views
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

urlpatterns = [

    url(r'^~(?P<user_name>\w+)/$', annuaire_views.home),

    url(r'^accounts/login/$', auth_views.login,
        {'template_name': 'registration/login.html', 'redirect_authenticated_user': True},
        name='account_login',
    ),
    url(r'^accounts/logout/$', auth_views.logout_then_login,
        name='account_logout'),
    #url(r'^accounts/', include('allauth.urls')),

    url(r'^me/$', annuaire_views.me),

    # AIn7 management section
    url(r'^manage/', include('ain7.manage.urls')),

    # annuaire
    url(r'^annuaire/', include('ain7.annuaire.urls')),

    # emploi
    url(r'^emploi/', include('ain7.emploi.urls')),

    # news
    url(r'^actualites/', include('ain7.news.urls')),
    # evenements
    url(r'^evenements/', include('ain7.news.urls_events')),

    # groups
    url(r'^groups/', include('ain7.groups.urls')),

    # organizations
    url(r'^organizations/', include('ain7.organizations.urls')),

    # voyages
    url(r'^voyages/', include('ain7.voyages.urls')),

    # association
    url(r'^association/', include('ain7.association.urls')),

    # adhesions
    url(r'^adhesions/', include('ain7.adhesions.urls')),

    url(r'^welcome/', annuaire_views.welcome),

    # Pages particulieres au contenu pseudo statique
    url(r'^apropos/$', pages_views.apropos, name='apropos'),
    url(r'^mentions_legales/$', pages_views.mentions_legales),
    url(r'^lostpassword/$', pages_views.lostpassword, name='lostpassword'),
    url(r'^lostpassword/([A-Za-z0-9.\-_]+)/$', pages_views.changepassword, name='resetpassword'),
    url(r'^$', pages_views.homepage, name='homepage'),

    # flux RSS
    url(r'^rss/$', NewsFeed(), name='rss'),

    url(r'^ical/$', news_views.ical),

    # Edit text blocks
    url(r'^edit/(?P<text_id>.*)/$', pages_views.edit, name='text-edit'),

    # sitemaps
    url(r'^sitemap.xml$', sitemaps_views.sitemap, {'sitemaps': sitemaps}),

    url(r'^groupes_professionnels/$', pages_views.professionnal_groups, name='professionnal_groups'),
    url(r'^groupes_regionaux/$', pages_views.regional_groups, name='regional_groups'),

    # redirection to external communities
    url(r'^facebook/$', RedirectView.as_view(url=settings.FACEBOOK_AIN7, permanent=True), name='facebook'),
    url(r'^linkedin/$', RedirectView.as_view(url=settings.LINKEDIN_AIN7, permanent=True), name='linkedin'),
    url(r'^twitter/$', RedirectView.as_view(url=settings.TWITTER_AIN7, permanent=True), name='twitter'),
    url(r'^g\+/$', RedirectView.as_view(url=settings.GPLUS_AIN7, permanent=True), name='g+'),

    # django-autocomplete-light
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    # (r'^admin/',  include(admin.site.urls)),  # admin site

    url(r'^site_media/(?P<path>.*)$', views_static.serve, {'document_root': settings.MEDIA_ROOT}),

    url(r'^static/(?P<path>.*)$', views_static.serve, {'document_root': settings.STATIC_ROOT}),
]
