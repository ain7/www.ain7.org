# -*- coding: utf-8
#
# sondages/urls.py
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

    # Sondage
    (r'^$', 'ain7.sondages.views.index'),
    (r'^(?P<survey_id>\d+)/vote/$', 'ain7.sondages.views.vote'),
    (r'^(?P<survey_id>\d+)/view/$', 'ain7.sondages.views.view'),

    # Edition
    (r'^create/$', 'ain7.sondages.views.create'),
    (r'^(?P<survey_id>\d+)/details/$', 'ain7.sondages.views.details'),
    (r'^(?P<survey_id>\d+)/edit/$', 'ain7.sondages.views.edit'),
    (r'^(?P<survey_id>\d+)/delete/$', 'ain7.sondages.views.delete'),
    (r'^(?P<survey_id>\d+)/choice/add/$', 'ain7.sondages.views.choice_add'),
    (r'^(?P<survey_id>\d+)/choice/(?P<choice_id>\d+)/edit/$', 'ain7.sondages.views.choice_edit'),
    (r'^(?P<survey_id>\d+)/choice/(?P<choice_id>\d+)/delete/$', 'ain7.sondages.views.choice_delete'),

)
