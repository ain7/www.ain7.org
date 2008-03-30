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
from ain7.manage.views import *

urlpatterns = patterns('ain7.manage.views',
    (r'^$', 'index'),
                       
    # Companies
    (r'^companies/$', 'companies_search'),
    (r'^companies/register/$', 'company_edit'),
    (r'^companies/(?P<company_id>\d+)/$', 'company_details'),
    (r'^companies/(?P<company_id>\d+)/edit/$', 'company_edit'),
    (r'^companies/(?P<company_id>\d+)/delete/$', 'company_delete'),
    (r'^companies/(?P<organization_id>\d+)/merge/$', 'organization_merge'),
    (r'^companies/(?P<org1_id>\d+)/merge/(?P<org2_id>\d+)/$',
     'organization_do_merge'),
    (r'^organizations/proposals/register/(?P<proposal_id>\d+)/$',
     'organization_register_proposal'),
                       
    # Offices
    (r'^offices/register/(?P<organization_id>\d+)/$', 'office_edit'),
    (r'^offices/(?P<office_id>\d+)/$', 'office_details'),
    (r'^offices/(?P<office_id>\d+)/edit/$', 'office_edit'),
    (r'^offices/(?P<office_id>\d+)/delete/$', 'office_delete'),
    (r'^offices/(?P<office_id>\d+)/merge/$', 'office_merge'),
    (r'^offices/(?P<office1_id>\d+)/merge/(?P<office2_id>\d+)/$',
     'office_do_merge'),
    (r'^offices/proposals/register/(?P<proposal_id>\d+)/$',
     'office_register_proposal'),
                       
    # Users
    (r'^users/$', 'users_search'),
    (r'^users/register/$', 'user_register'),
    (r'^users/(?P<user_id>\d+)/$', 'user_details'),
                       
    # Groups
    (r'^groups/$', 'groups_search'),
    (r'^groups/register/$', 'group_register'),
    (r'^groups/(?P<group_id>\d+)/$', 'group_details'),
    (r'^groups/(?P<group_id>\d+)/member/(?P<member_id>\d+)/delete/$', 'member_delete'),
    (r'^groups/(?P<group_id>\d+)/member/add/$', 'member_add'),
    (r'^groups/(?P<group_id>\d+)/perm/(?P<perm_id>\d+)/delete/$', 'perm_delete'),
    (r'^groups/(?P<group_id>\d+)/perm/add/$', 'perm_add'),
                       
    # Permissions
    (r'^permissions/$', 'permissions'),
    (r'^permissions/register/$', 'permission_register'),
    (r'^permissions/(?P<perm_id>\d+)/$', 'permission_details'),
                       
    # Contributions
    (r'^contributions/$', 'contributions'),
                       
    # Notifications
    (r'^notification/add/$', 'notification_add'),
    (r'^notification/(?P<notif_id>\d+)/edit/$', 'notification_edit'),
    (r'^notification/(?P<notif_id>\d+)/delete/$', 'notification_delete'),
)

