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

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^ain7/', include('ain7.apps.foo.urls.foo')),

    # servir le contenu statique pendant le dev
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/lionel/dev/ain7/ain7-website/ain7/media'}),

    # Uncomment this for admin:
     (r'^admin/', include('django.contrib.admin.urls')),

    # annuaire
    (r'^annuaire/', include('ain7.annuaire.urls')),

    # sondage
    (r'^sondages/', include('ain7.sondages.urls')),

    # Pages particulieres au contenu pseudo statique
    (r'^contact/','ain7.pages.views.contact'),
    (r'^apropos/','ain7.pages.views.apropos'),
    (r'^$','ain7.pages.views.homepage'),

)
