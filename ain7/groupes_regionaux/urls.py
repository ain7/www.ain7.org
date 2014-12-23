# -*- coding: utf-8
"""
 ain7/groupes_regionaux/urls.py
"""
#
#   Copyright © 2007-2015 AIn7 Devel Team
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

from django.conf.urls import patterns


urlpatterns = patterns('ain7.groupes_regionaux.views',
    # Groupes Regionaux
    (r'^$', 'index'),
    (r'^(?P<slug>\w+)/$', 'details'),
    (r'^(?P<slug>\w+)/edit/$', 'edit'),
    (r'^(?P<slug>\w+)/join/$', 'join'),
    (r'^(?P<slug>\w+)/quit/$', 'quit'),
    (r'^(?P<slug>\w+)/roles/(?P<role_id>\d+)/edit/$', 'edit_role'),
    (r'^(?P<slug>\w+)/roles/add/$', 'edit_role'),
    (r'^(?P<slug>\w+)/roles/(?P<role_id>\d+)/delete/$', 'delete_role'),
)

