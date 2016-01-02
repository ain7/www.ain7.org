# -*- coding: utf-8
"""
 ain7/voyages/urls.py
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

urlpatterns = patterns('ain7.voyages.views',

    # Voyages
    url(r'^$', 'index', name='travels-index'),
    url(r'^add/$', 'edit', name='travel-add'),
    url(r'^edit/$', 'edit', name='travel-edit'),
    url(r'^(?P<travel_id>\d+)/$', 'details', name='travel-details'),
    url(r'^(?P<travel_id>\d+)/edit/$', 'edit', name='travel-edit'),
    url(r'^(?P<travel_id>\d+)/delete/$', 'delete', name='travel-delete'),

)
