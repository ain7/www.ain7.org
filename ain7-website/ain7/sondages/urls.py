# -*- coding: utf-8
#
# sondages/urls.py
#
#   Copyright (C) 2007-2009 AIn7
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


urlpatterns = patterns('ain7.sondages.views',

    # Sondage
    (r'^$', 'index'),
    (r'^(?P<survey_id>\d+)/vote/$', 'vote'),
    (r'^(?P<survey_id>\d+)/view/$', 'view'),

    # Survey edition
    (r'^create/$', 'create'),
    (r'^(?P<survey_id>\d+)/details/$', 'details'),
    (r'^(?P<survey_id>\d+)/edit/$', 'edit'),
    (r'^(?P<survey_id>\d+)/delete/$', 'delete'),

    # Choice edition
    (r'^(?P<survey_id>\d+)/choice/add/$', 'choice_add'),
    (r'^(?P<survey_id>\d+)/choice/(?P<choice_id>\d+)/edit/$', 'choice_edit'),
    (r'^(?P<survey_id>\d+)/choice/(?P<choice_id>\d+)/delete/$', 'choice_delete'),

)
