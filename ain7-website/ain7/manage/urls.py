# -*- coding: utf-8
#
# manage/urls.py
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

urlpatterns = patterns('ain7.manage.views',
    (r'^$', 'index'),
    (r'^companies/$', 'companies_search'),
    (r'^companies/(?P<company_id>\d+)/$', 'company_details'),
    (r'^users/$', 'users_search'),
    (r'^users/(?P<user_id>\d+)/$', 'user_details'),
    (r'^groups/$', 'groups_search'),
    (r'^groups/(?P<group_id>\d+)/$', 'group_details'),
    (r'^groups/(?P<group_id>\d+)/member/(?P<member_id>\d+)/delete/$', 'member_delete'),
    (r'^groups/(?P<group_id>\d+)/member/add/$', 'member_add'),
    (r'^groups/(?P<group_id>\d+)/perm/(?P<perm_id>\d+)/delete/$', 'perm_delete'),
    (r'^groups/(?P<group_id>\d+)/perm/add/$', 'perm_add'),
    (r'^permissions/$', 'permissions'),
    (r'^permissions/(?P<perm_id>\d+)/$', 'permission_details'),
    (r'^contributions/$', 'contributions'),
)

