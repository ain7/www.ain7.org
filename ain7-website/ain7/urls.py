# -*- coding: utf-8
#
# urls.py
#
#   Copyright (C) 2007 AIn7
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

urlpatterns = patterns('',

     (r'^login/', 'ain7.utils.login'),
     (r'^logout/', 'ain7.utils.logout'),

    # servir le contenu statique pendant le dev
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.abspath(os.path.dirname(__file__))+'/media'}),

    # Uncomment this for admin:
     (r'^admin/', include('django.contrib.admin.urls')),

    # annuaire
    (r'^annuaire/', include('ain7.annuaire.urls')),

    # groupes
    (r'^groupes/', include('ain7.groupes.urls')),

    # sondage
    (r'^sondages/', include('ain7.sondages.urls')),

    # planet
    (r'^planet/', 'ain7.utils.planet'),

    # forums
    (r'^forums/', 'ain7.utils.forums'),

    # Pages particulieres au contenu pseudo statique
    (r'^contact/','ain7.pages.views.contact'),
    (r'^apropos/','ain7.pages.views.apropos'),
    (r'^$','ain7.pages.views.homepage'),

)
