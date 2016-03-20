# -*- coding: utf-8
"""
 ain7/organizations/urls.py
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


from ain7.organizations import views

urlpatterns = [

    # Organizations
    url(r'^$', views.organization_search, name='organization-index'),
    url(r'^add/', views.organization_edit, name='organization-add'),
    url(
        r'^(?P<organization_id>\d+)/$',
        views.organization_details,
        name='organization-details'
    ),
    url(
        r'^(?P<organization_id>\d+)/edit/$',
        views.organization_edit,
        name='organization-edit'),
    url(r'^(?P<organization_id>\d+)/delete/$', views.organization_delete, name='organization-delete'),
    url(r'^(?P<organization_id>\d+)/undelete/$', views.organization_undelete, name='organization-undelete'),
    url(r'^(?P<organization_id>\d+)/merge/$', views.organization_merge, name='organization-merge'),
    url(
        r'^(?P<org1_id>\d+)/merge/(?P<org2_id>\d+)/$',
        views.organization_merge_perform,
        name='organization-merge-perform',
    ),

    # Offices
    url(
        r'^(?P<organization_id>\d+)/offices/add/$',
        views.office_edit,
        name='office-add'
    ),
    url(
        r'^(?P<organization_id>\d+)/offices/(?P<office_id>\d+)/edit/$',
        views.office_edit,
        name='office-edit'
    ),
    url(
        r'^(?P<organization_id>\d+)/offices/(?P<office_id>\d+)/delete/$',
        views.office_delete,
        name='office-delete',
    ),
    url(
        r'^(?P<organization_id>\d+)/offices/(?P<office_id>\d+)/undelete/$',
        views.organization_undelete,
        name='office-undelete',
    ),
    url(
        r'^(?P<organization_id>\d+)/offices/(?P<office_id>\d+)/merge/$',
        views.office_merge,
        name='office-merge',
    ),
    url(
        r'^(?P<organization_id>\d+)/offices/(?P<office1_id>\d+)/merge/(?P<office2_id>\d+)/$',
        views.office_merge_perform,
    ),

]
