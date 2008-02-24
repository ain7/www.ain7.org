# -*- coding: utf-8
#
# groupes/urls.py
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

from ain7.groupes.views import *

urlpatterns = patterns('',

    # Groupes
    (r'^$', index),
    (r'^(?P<group_id>\d+)/$', detail),
    (r'^edit/(?P<group_id>\d+)/$', edit),
    (r'^(?P<group_id>\d+)/subscribe/$', subscribe),

)
