# -*- coding: utf-8
"""
 ain7/groups/urls.py
"""
#
#   Copyright © 2007-2016 AIn7 Devel Team
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

from django.conf.urls import url

from ain7.groups import views


urlpatterns = [
    url(r'^$', views.index, name='groups-index'),
    url(r'^add/$', views.edit, name='group-edit'),
    url(r'^(?P<slug>[A-Za-z0-9.\-_]+)/$', views.details, name='group-details'),
    url(r'^(?P<slug>[A-Za-z0-9.\-_]+)/edit/$', views.edit, name='group-edit'),
    url(r'^(?P<slug>[A-Za-z0-9.\-_]+)/join/$', views.join, name='group-join'),
    url(r'^(?P<slug>[A-Za-z0-9.\-_]+)/quit/$', views.quit, name='group-quit'),
    url(r'^(?P<slug>[A-Za-z0-9.\-_]+)/members/$', views.members, name='group-members'),
    url(r'^(?P<slug>[A-Za-z0-9.\-_]+)/members/(?P<member_id>\d+)/delete/$', views.member_delete, name='group-member-delete'),
    url(r'^(?P<slug>[A-Za-z0-9.\-_]+)/members/(?P<member_id>\d+)/edit/$', views.member_edit, name='group-member-edit'),
    url(r'^(?P<slug>[A-Za-z0-9.\-_]+)/members/add/$', views.member_edit, name='group-member-add'),
    url(r'^(?P<slug>[A-Za-z0-9.\-_]+)/role/(?P<role_id>\d+)/edit/$', views.role_edit, name='group-role-edit'),
    url(r'^(?P<slug>[A-Za-z0-9.\-_]+)/role/add/$', views.role_edit, name='group-role-add'),
    url(r'^(?P<slug>[A-Za-z0-9.\-_]+)/role/(?P<role_id>\d+)/delete/$', views.role_delete, name='group-role-delete'),
]
