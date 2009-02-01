# -*- coding: utf-8
#
# ajax/urls.py
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

from django.conf.urls.defaults import *

urlpatterns = patterns('ain7.ajax.views',
    (r'^person/$', 'person'),
    (r'^nationality/$', 'nationality'),
    (r'^promoyear/$', 'promoyear'),
    (r'^track/$', 'track'),
    (r'^organization/$', 'organization'),
    (r'^activity_field/$', 'activity_field'),
    (r'^activitycode/$', 'activitycode'),
    (r'^permission/$', 'permission'),
    (r'^office/$', 'office'),
)

