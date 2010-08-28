# -*- coding: utf-8
#
# urls.py
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

import os.path

from django.conf.urls.defaults import *

from ain7.feeds import LatestsEvents, LatestsNews
from ain7.sitemaps import EventsSitemap, TextsSitemap, NewsSitemap, GroupesProSitemap
from ain7.sitemaps import GroupesRegionauxSitemap, TravelsSitemap

feeds = {
    'events': LatestsEvents,
    'news': LatestsNews,
}

sitemaps = {
    'events': EventsSitemap,
    'news': NewsSitemap,
    'groupespro': GroupesProSitemap,
    'groupesregionaux': GroupesRegionauxSitemap,
    'voyages': TravelsSitemap,
    'texts': TextsSitemap,
}

urlpatterns = patterns('',

    (r'^~(?P<user_name>\w+)/$', 'ain7.annuaire.views.home'),

    (r'^accounts/login/$', 'ain7.pages.views.login'),
    (r'^accounts/logout/$', 'ain7.pages.views.logout'),

    # servir le contenu statique pendant le dev
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.abspath(os.path.dirname(__file__))+'/media'}),

    # AIn7 management section
    (r'^manage/', include('ain7.manage.urls')),

    # AJAX autocompletion
    (r'^ajax/', include('ain7.ajax.urls')),

    # annuaire
    (r'^annuaire/', include('ain7.annuaire.urls')),

    # emploi
    (r'^emploi/', include('ain7.emploi.urls')),

    # news
    (r'^actualites/', include('ain7.news.urls')),

    # evenements
    (r'^evenements/', include('ain7.news.urls_events')),

    # groupes professionnels
    (r'^groupes_professionnels/', include('ain7.groupes_professionnels.urls')),

    # groupes regionaux
    (r'^groupes_regionaux/', include('ain7.groupes_regionaux.urls')),

    # sondage
    (r'^sondages/', include('ain7.sondages.urls')),

    # organizations
    (r'^organizations/', include('ain7.organizations.urls')),

    # voyages
    (r'^voyages/', include('ain7.voyages.urls')),

    # association
    (r'^association/',include('ain7.association.urls')),

    # adhesions
    (r'^adhesions/',include('ain7.adhesions.urls')),

    # media & communication
    (r'^media_communication/$', 'ain7.association.views.media_com'),
    (r'^media_communication/canal_n7/$', 'ain7.association.views.canal_n7'),
    (r'^media_communication/canal_n7/edito/$', 'ain7.association.views.canal_n7_edito'),

    # relations école étudiants
    (r'^relations_ecole_etudiants/', 'ain7.pages.views.relations_ecole_etudiants'),

    # Pages particulieres au contenu pseudo statique
    (r'^apropos/$','ain7.pages.views.apropos'),
    (r'^web/$','ain7.pages.views.web'),
    (r'^mentions_legales/$','ain7.pages.views.mentions_legales'),
    (r'^lostpassword/$','ain7.pages.views.lostpassword'),
    (r'^lostpassword/([A-Za-z0-9.\-_]+)/$','ain7.pages.views.changepassword'),
    (r'^$','ain7.pages.views.homepage'),

    # flux RSS
    (r'^rss/$', 'ain7.pages.views.rss'),
    (r'^rss/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),

    # Edit text blocks
    (r'^edit/(?P<text_id>.*)/$', 'ain7.pages.views.edit'),

    # sitemaps
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps})

)
