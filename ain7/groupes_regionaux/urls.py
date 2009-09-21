# -*- coding: utf-8
#
# groupes_regionaux/urls.py
#
#   Copyright © 2007-2009 AIn7 Devel Team
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


urlpatterns = patterns('ain7.groupes_regionaux.views',
    # Groupes Regionaux
    (r'^$', 'index'),
    (r'^(?P<group_id>\d+)/$', 'details'),
    (r'^(?P<group_id>\d+)/edit/$', 'edit'),
    (r'^(?P<group_id>\d+)/join/$', 'join'),
    (r'^(?P<group_id>\d+)/quit/$', 'quit'),
    (r'^(?P<group_id>\d+)/roles/edit/(?P<all_current>\w+)/$', 'edit_roles'),
    (r'^(?P<group_id>\d+)/roles/(?P<role_id>\d+)/changedates/(?P<all_current>\w+)/$', 'change_dates'),
    (r'^(?P<group_id>\d+)/roles/(?P<type>\d+)/add/(?P<all_current>\w+)/$', 'add_role'),
    (r'^(?P<group_id>\d+)/roles/(?P<role_id>\d+)/delete/(?P<all_current>\w+)/$', 'delete_role'),
)

