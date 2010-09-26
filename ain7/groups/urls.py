# -*- coding: utf-8
"""
 ain7/groups/urls.py
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


urlpatterns = patterns('ain7.groups.views',
    # Groupes Regionaux
    (r'^$', 'index'),
    (r'^add/$', 'edit'),
    (r'^(?P<slug>[A-Za-z0-9.\-_]+)/$', 'details'),
    (r'^(?P<slug>[A-Za-z0-9.\-_]+)/edit/$', 'edit'),
    (r'^(?P<slug>[A-Za-z0-9.\-_]+)/join/$', 'join'),
    (r'^(?P<slug>[A-Za-z0-9.\-_]+)/quit/$', 'quit'),
    (r'^(?P<slug>[A-Za-z0-9.\-_]+)/members/$', 'members'),
    (r'^(?P<slug>[A-Za-z0-9.\-_]+)/members/(?P<member_id>\d+)/delete/$', 'member_delete'),
    (r'^(?P<slug>[A-Za-z0-9.\-_]+)/members/(?P<member_id>\d+)/edit/$', 'member_edit'),
    (r'^(?P<slug>[A-Za-z0-9.\-_]+)/members/add/$', 'member_edit'),
    (r'^(?P<slug>[A-Za-z0-9.\-_]+)/role/(?P<role_id>\d+)/edit/$', 'role_edit'),
    (r'^(?P<slug>[A-Za-z0-9.\-_]+)/role/add/$', 'role_edit'),
    (r'^(?P<slug>[A-Za-z0-9.\-_]+)/role/(?P<role_id>\d+)/delete/$', 'role_delete'),
)

