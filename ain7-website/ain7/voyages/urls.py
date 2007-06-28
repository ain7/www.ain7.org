# -*- coding: utf-8
#
# voyages/urls.py
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

    # Voyages
    (r'^$', 'ain7.voyages.views.index'),
    (r'^search/$', 'ain7.voyages.views.search'),
    (r'^edit/$', 'ain7.voyages.views.edit'),
    (r'^add/$', 'ain7.voyages.views.add'),
    (r'^list/$', 'ain7.voyages.views.list'),
    (r'^(?P<travel_id>\d+)/$', 'ain7.voyages.views.detail'),
    (r'^(?P<travel_id>\d+)/edit/$', 'ain7.voyages.views.edit'),
    (r'^(?P<travel_id>\d+)/join/$', 'ain7.voyages.views.join'),
    (r'^(?P<travel_id>\d+)/search/$', 'ain7.voyages.views.search'),
    (r'^(?P<travel_id>\d+)/subscribe/$', 'ain7.voyages.views.subscribe'),
    (r'^(?P<travel_id>\d+)/unsubscribe/(?P<participant_id>\d+)/$',
     'ain7.voyages.views.unsubscribe'),
    (r'^(?P<travel_id>\d+)/participants/$', 'ain7.voyages.views.participants'),
    (r'^(?P<travel_id>\d+)/responsibles/$', 'ain7.voyages.views.responsibles'),
    (r'^(?P<travel_id>\d+)/responsibles/add/$',
     'ain7.voyages.views.responsibles_add'),
    (r'^(?P<travel_id>\d+)/responsibles/(?P<responsible_id>\d+)/delete/$',
     'ain7.voyages.views.responsibles_delete'),
    (r'^(?P<travel_id>\d+)/delete/$', 'ain7.voyages.views.delete'),

)
