# -*- coding: utf-8
"""
 ain7/association/urls.py
"""
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

from django.conf.urls import patterns, url


urlpatterns = patterns('ain7.association.views',
    url(r'^$', 'index', name='association-index'),
    url(r'^council/$', 'council', name='council-details'),
    url(r'^council/add/$', 'edit_council_role'),
    url(r'^council/edit/(?P<role_id>\d+)/$', 'edit_council_role'),
    url(r'^council/delete/(?P<role_id>\d+)/$', 'delete_council_role'),
    url(r'^contact/$', 'contact', name='contact'),
    url(r'^status/$', 'status', name='status'),
    url(r'^internalrules/$', 'internalrules', name='internalrules'),

)
