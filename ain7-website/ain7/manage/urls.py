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
                       
    # Organizations
    (r'^organizations/$', 'organizations_search'),
    (r'^organizations/register/$', 'organization_edit'),
    (r'^organizations/(?P<organization_id>\d+)/$', 'organization_details'),
    (r'^organizations/(?P<organization_id>\d+)/edit/$', 'organization_edit'),
    (r'^organizations/(?P<organization_id>\d+)/delete/$', 'organization_delete'),
    (r'^organizations/(?P<organization_id>\d+)/merge/$', 'organization_merge'),
    (r'^organizations/(?P<org1_id>\d+)/merge/(?P<org2_id>\d+)/$',
     'organization_do_merge'),
    (r'^organizations/proposals/register/(?P<proposal_id>\d+)/$',
     'organization_register_proposal'),
    (r'^organizations/proposals/edit/(?P<proposal_id>\d+)/$',
     'organization_edit_proposal'),
    (r'^organizations/proposals/delete/(?P<proposal_id>\d+)/$',
     'organization_delete_proposal'),
                       
    # Offices
    (r'^offices/register/(?P<organization_id>\d+)/$', 'office_edit'),
    (r'^offices/(?P<office_id>\d+)/$', 'office_details'),
    (r'^offices/(?P<office_id>\d+)/edit/$', 'office_edit'),
    (r'^offices/(?P<office_id>\d+)/delete/$', 'office_delete'),
    (r'^offices/(?P<office_id>\d+)/merge/$', 'office_merge'),
    (r'^offices/(?P<office1_id>\d+)/merge/(?P<office2_id>\d+)/$','office_do_merge'),
    (r'^offices/proposals/register/(?P<proposal_id>\d+)/$','office_register_proposal'),
    (r'^offices/proposals/edit/(?P<proposal_id>\d+)/$','office_edit_proposal'),
    (r'^offices/proposals/delete/(?P<proposal_id>\d+)/$','office_delete_proposal'),
                       
    # Users
    (r'^users/$', 'users_search'),
    (r'^users/register/$', 'user_register'),
    (r'^users/(?P<user_id>\d+)/$', 'user_details'),
    (r'^users/(?P<user_id>\d+)/edit/$', 'user_edit'),
    (r'^users/(?P<user_id>\d+)/person/edit/$', 'user_person_edit'),
    # Adresses
    (r'^users/(?P<user_id>\d+)/address/(?P<address_id>\d+)/edit/$', 'user_address_edit'),
    (r'^users/(?P<user_id>\d+)/address/(?P<address_id>\d+)/delete/$', 'user_address_delete'),
    (r'^users/(?P<user_id>\d+)/address/add/$', 'user_address_edit'),
    # Phone numbers
    (r'^users/(?P<user_id>\d+)/phone/(?P<phone_id>\d+)/edit/$', 'user_phone_edit'),
    (r'^users/(?P<user_id>\d+)/phone/(?P<phone_id>\d+)/delete/$', 'user_phone_delete'),
    (r'^users/(?P<user_id>\d+)/phone/add/$', 'user_phone_edit'),
    # Email
    (r'^users/(?P<user_id>\d+)/email/(?P<email_id>\d+)/edit/$', 'user_email_edit'),
    (r'^users/(?P<user_id>\d+)/email/(?P<email_id>\d+)/delete/$', 'user_email_delete'),
    (r'^users/(?P<user_id>\d+)/email/add/$', 'user_email_edit'),
    # vCard
    #(r'^users/(?P<user_id>\d+)/vcard/$', 'user_vcard'),
                       
    # Roles
    (r'^roles/$', 'roles_search'),
    (r'^roles/register/$', 'role_register'),
    (r'^roles/(?P<role_id>\d+)/$', 'role_details'),
    (r'^roles/(?P<role_id>\d+)/member/(?P<member_id>\d+)/delete/$', 'role_member_delete'),
    (r'^roles/(?P<role_id>\d+)/member/add/$', 'role_member_add'),
    #(r'^roles/(?P<role_id>\d+)/perm/(?P<perm_id>\d+)/delete/$', 'role_perm_delete'),
    (r'^roles/(?P<role_id>\d+)/perm/add/$', 'role_perm_add'),

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

    # Nationality
    (r'^nationality/add/$', 'nationality_add'),

    # Office
    #(r'^office/add/$', 'office_add'),
)

