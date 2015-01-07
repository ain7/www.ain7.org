# -*- coding: utf-8
"""
 ain7/organizations/urls.py
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

from django.conf.urls import patterns, url

urlpatterns = patterns('ain7.organizations.views',
    # Organizations
    url(r'^$', 'organization_search'),
    url(r'^add/', 'organization_edit'),
    url(r'^(?P<organization_id>\d+)/$', 'organization_details', name='organization-details'),
    url(r'^(?P<organization_id>\d+)/edit/$', 'organization_edit', name='organization-edit'),
    url(r'^(?P<organization_id>\d+)/delete/$', 'organization_delete'),
    (r'^(?P<organization_id>\d+)/undelete/$', 'organization_undelete'),
    (r'^(?P<org1_id>\d+)/merge/(?P<org2_id>\d+)/$', 'organization_merge_perform'),

    # Offices
    url(r'^(?P<organization_id>\d+)/offices/add/$', 'office_edit', name='office-add'),
    url(r'^(?P<organization_id>\d+)/offices/(?P<office_id>\d+)/edit/$', 'office_edit', name='office-edit'),
    (r'^(?P<organization_id>\d+)/offices/(?P<office_id>\d+)/delete/$', 'office_delete'),
    (r'^(?P<organization_id>\d+)/offices/(?P<office_id>\d+)/undelete/$', 'organization_undelete'),
    (r'^(?P<organization_id>\d+)/offices/(?P<office_id>\d+)/merge/$', 'office_merge'),
    (r'^(?P<organization_id>\d+)/offices/(?P<office1_id>\d+)/merge/(?P<office2_id>\d+)/$', 'office_merge_perform'),

)
