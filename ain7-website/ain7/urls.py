# -*- coding: utf-8
#
# urls.py
#
#   Copyright (C) 2007-2008 AIn7
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
from django.contrib import admin

from ain7.feeds import LatestEvents, LatestEntriesByCategory

feeds = {
    'events': LatestEvents,
    'categories': LatestEntriesByCategory,
}

# Add (nearly) all object to the django admin, so we can edit them with django admin.
admin.autodiscover()
import ain7.admin

urlpatterns = patterns('',

    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
#    (r'^accounts/logout/$', 'ain7.utils.logout'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url':'/accounts/login/?next=/'}),

    # servir le contenu statique pendant le dev
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.abspath(os.path.dirname(__file__))+'/media'}),

    # django admin
    (r'^admin/(.*)', admin.site.root),

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
    (r'^evenements/', include('ain7.evenements.urls')),

    # groupes professionnels
    (r'^groupes_professionnels/', include('ain7.groupes_professionnels.urls')),

    # groupes regionaux
    (r'^groupes_regionaux/', include('ain7.groupes_regionaux.urls')),

    # sondage
    (r'^sondages/', include('ain7.sondages.urls')),

    # voyages
    (r'^voyages/', include('ain7.voyages.urls')),

    # planet
    (r'^planet/', 'ain7.utils.planet'),

    # forums
    (r'^forums/', 'ain7.utils.forums'),

    # galerie
    (r'^galerie/', 'ain7.utils.galerie'),

    # association
    (r'^association/',include('ain7.association.urls')),

    # adhesions
    (r'^adhesions/',include('ain7.adhesions.urls')),

    # communaute N7
    #(r'^communaute_n7/',include('ain7.communaute_n7.urls')),

    # media & communication
    (r'^media_communication/',include('ain7.media_communication.urls')),

    # relations école étudiants
    (r'^relations_ecole_etudiants/',include('ain7.relations_ecole_etudiants.urls')),

    # Pages particulieres au contenu pseudo statique
    (r'^apropos/$','ain7.pages.views.apropos'),
    (r'^canal_n7/$','ain7.pages.views.canal_n7'),
    (r'^international/$','ain7.pages.views.international'),
    (r'^mentions_legales/$','ain7.pages.views.mentions_legales'),
    (r'^publications/$','ain7.pages.views.publications'),
    (r'^$','ain7.pages.views.homepage'),

    # flux RSS
    (r'^rss/$', 'ain7.pages.views.rss'),
    (r'^rss/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),

)
