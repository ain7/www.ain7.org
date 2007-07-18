# -*- coding: utf-8
#
# evenements/urls.py
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

    # Evenements
    (r'^$', 'ain7.evenements.views.index'),
    (r'^register/$', 'ain7.evenements.views.register'),
    (r'^search/$', 'ain7.evenements.views.search'),
    (r'^(?P<event_id>\d+)/$', 'ain7.evenements.views.details'),
    (r'^(?P<event_id>\d+)/edit/$', 'ain7.evenements.views.edit'),
    (r'^(?P<event_id>\d+)/image/edit/$', 'ain7.evenements.views.image_edit'),
    (r'^(?P<event_id>\d+)/join/$', 'ain7.evenements.views.join'),
    (r'^(?P<event_id>\d+)/participants/$', 'ain7.evenements.views.participants'),
    (r'^(?P<event_id>\d+)/subscribe/$', 'ain7.evenements.views.subscribe'),
    (r'^(?P<event_id>\d+)/validate/$', 'ain7.evenements.views.validate'),

)
