# -*- coding: utf-8
#
# association/urls.py
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

from ain7.association.views import *

urlpatterns = patterns('',

    (r'^$', index),
    (r'^board/$', board),
    (r'^board/edit/(?P<all_current>\w+)/$', edit_board),
    (r'^board/(?P<role_id>\d+)/changedates/(?P<all_current>\w+)/$', change_board_dates),
    (r'^board/(?P<role_type>\d+)/add/(?P<all_current>\w+)/$', add_board_role),
    (r'^board/(?P<role_id>\d+)/delete/(?P<all_current>\w+)/$', delete_board_role),
    (r'^council/$', council),
    (r'^council/edit/(?P<all_current>\w+)/$', edit_council),
    (r'^council/(?P<role_id>\d+)/changedates/(?P<all_current>\w+)/$', change_council_dates),
    (r'^council/(?P<role_type>\d+)/add/(?P<all_current>\w+)/$', add_council_role),
    (r'^council/(?P<role_id>\d+)/delete/(?P<all_current>\w+)/$', delete_council_role),
    (r'^contact/$', contact),
    (r'^status/$', status),

)
