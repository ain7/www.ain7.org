# -*- coding: utf-8
"""
 ain7/manage/urls.py
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

urlpatterns = patterns('ain7.manage.views',
    (r'^$', 'index'),
    # Organizations
    (r'^organizations/$', 'organizations_search'),
    (r'^organizations/csv/$', 'export_csv'),
    (r'^organizations/adv_search/$', 'organizations_adv_search'),
    (r'^organizations/adv_search/csv/$', 'adv_export_csv'),
    (r'^organizations/adv_search/filter/new/$', 'filter_new'),
    (r'^organizations/adv_search/filter/register/$', 'filter_register'),
    (r'^organizations/adv_search/filter/(?P<filter_id>\d+)/$', 
        'filter_details'),
    (r'^organizations/adv_search/filter/(?P<filter_id>\d+)/edit/$', 
        'filter_edit'),
    (r'^organizations/adv_search/filter/(?P<filter_id>\d+)/reset/$', 
        'filter_reset'),
    (r'^organizations/adv_search/filter/(?P<filter_id>\d+)/delete/$', 
        'filter_delete'),
    (r'^organizations/adv_search/filter/(?P<filter_id>\d*)/swapOp/$', 
        'filter_swap_op'),
    (r'^organizations/adv_search/filter/(?P<filter_id>\d*)/criterion/add/$',
        'criterion_add'),
    (r'^organizations/adv_search/filter/(?P<filter_id>\d*)/criterion/\
add/field/$',
     'criterion_add', {'criterion_type': 'field'}),
    (r'^organizations/adv_search/filter/(?P<filter_id>\d*)/criterion/add/\
filter/$',
     'criterion_add', {'criterion_type': 'filter'}),
    (r'^organizations/adv_search/filter/(?P<filter_id>\d+)/criterion/edit/\
field/$',
     'criterion_field_edit'),
    (r'^organizations/adv_search/filter/(?P<filter_id>\d+)/criterion/edit/\
filter/$',
     'criterion_filter_edit'),
    (r'^organizations/adv_search/filter/(?P<filter_id>\d+)/criterion/\
(?P<criterion_id>\d+)/edit/field/$',
     'criterion_field_edit'),
    (r'^organizations/adv_search/filter/(?P<filter_id>\d+)/criterion/\
(?P<criterion_id>\d+)/edit/filter/$',
     'criterion_filter_edit'),
    (r'^organizations/adv_search/filter/(?P<filtr_id>\d+)/criterion/\
(?P<crit_id>\d+)/delete/field/$',
     'criterion_delete', {'crit_type': 'field'}, "criterionField_delete"),
    (r'^organizations/adv_search/filter/(?P<filtr_id>\d+)/criterion/\
(?P<crit_id>\d+)/delete/filter/$',
     'criterion_delete', {'crit_type': 'filter'}, "criterionFilter_delete"),
    (r'^organizations/register/$', 'organization_edit'),
    (r'^organizations/(?P<organization_id>\d+)/$', 'organization_details'),
    (r'^organizations/(?P<organization_id>\d+)/edit/$', 'organization_edit'),
    (r'^organizations/(?P<organization_id>\d+)/delete/$', \
        'organization_delete'),
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
    (r'^offices/(?P<office1_id>\d+)/merge/(?P<office2_id>\d+)/$', \
         'office_do_merge'),
    (r'^offices/proposals/register/(?P<proposal_id>\d+)/$', \
         'office_register_proposal'),
    (r'^offices/proposals/edit/(?P<proposal_id>\d+)/$', \
         'office_edit_proposal'),
    (r'^offices/proposals/delete/(?P<proposal_id>\d+)/$', \
         'office_delete_proposal'),
                       
    # Users
    (r'^users/$', 'users_search'),
    (r'^users/register/$', 'user_register'),

    # Roles
    (r'^roles/$', 'roles_index'),
    (r'^roles/register/$', 'role_register'),
    (r'^roles/(?P<role_id>[A-Za-z0-9.\-_]+)/$', 'role_details'),
    (r'^roles/(?P<role_id>[A-Za-z0-9.\-_]+)/member/(?P<member_id>\d+)/delete/$'\
         , 'role_member_delete'),
    (r'^roles/(?P<role_id>[A-Za-z0-9.\-_]+)/member/add/$', 'role_member_add'),

    # Notifications
    (r'^notification/add/$', 'notification_add'),
    (r'^notification/(?P<notif_id>\d+)/edit/$', 'notification_edit'),
    (r'^notification/(?P<notif_id>\d+)/delete/$', 'notification_delete'),

    # Nationality
    (r'^nationality/add/$', 'nationality_add'),

    # Errors
    (r'^errors/$', 'errors_index'),
    (r'^errors/(?P<error_id>\d+)/$', 'error_details'),
    (r'^errors/edit_range/$', 'errors_edit_range'),
    (r'^errors/(?P<error_id>\d+)/swap/$', 'error_swap'),

    # Payment
    (r'^payments/$', 'payments_index'),
    (r'^payments/add/$', 'payment_add'),
    (r'^payments/(?P<payment_id>\d+)/$', 'payment_details'),
    (r'^payments/(?P<payment_id>\d+)/edit/$', 'payment_edit'),
    (r'^payments/deposit/$', 'payments_deposit_index'),
    (r'^payments/deposit/(?P<deposit_id>\d+)/$', 'payments_deposit'),
    (r'^payments/deposit/(?P<deposit_id>\d+)/deposited/\
(?P<last_deposit_id>\d+)/$', 'payments_mark_deposited'),

)

