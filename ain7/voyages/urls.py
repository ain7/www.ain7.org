# -*- coding: utf-8
"""
 ain7/voyages/urls.py
"""
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

from django.conf.urls.defaults import patterns

urlpatterns = patterns('ain7.voyages.views',

    # Voyages
    (r'^$', 'index'),
    (r'^search/$', 'search'),
    (r'^edit/$', 'edit'),
    (r'^add/$', 'edit'),
    (r'^list/$', 'list'),
    (r'^all/$', 'all'),
    (r'^(?P<travel_id>\d+)/$', 'details'),
    (r'^(?P<travel_id>\d+)/edit/$', 'edit'),
    (r'^(?P<travel_id>\d+)/thumbnail/delete/$', 'thumbnail_delete'),
    (r'^(?P<travel_id>\d+)/join/$', 'join'),
    (r'^(?P<travel_id>\d+)/search/$', 'search'),
    (r'^(?P<travel_id>\d+)/subscribe/$', 'subscribe'),
    (r'^(?P<travel_id>\d+)/unsubscribe/(?P<participant_id>\d+)/$',
        'unsubscribe'),
    (r'^(?P<travel_id>\d+)/participants/$', 'participants'),
    (r'^(?P<travel_id>\d+)/responsibles/$', 'responsibles'),
    (r'^(?P<travel_id>\d+)/responsibles/add/$', 'responsibles_add'),
    (r'^(?P<travel_id>\d+)/responsibles/(?P<responsible_id>\d+)/delete/$',
     'responsibles_delete'),
    (r'^(?P<travel_id>\d+)/delete/$', 'delete'),

)
