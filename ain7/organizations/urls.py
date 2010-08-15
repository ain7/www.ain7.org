# -*- coding: utf-8
"""
 ain7/organizations/urls.py
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

urlpatterns = patterns('ain7.organizations.views',
    # Organizations
    (r'^$', 'organization_search'),
    (r'^add/', 'organization_edit'),
    (r'^(?P<organization_id>\d+)/$', 'organization_details'),
    (r'^(?P<organization_id>\d+)/edit/$', 'organization_edit'),
    (r'^(?P<organization_id>\d+)/delete/$', 'organization_delete'),
    (r'^(?P<org1_id>\d+)/merge/(?P<org2_id>\d+)/$',
     'organization_merge_perform'),

    # Offices
    (r'^(?P<organization_id>\d+)/offices/add/$', 'office_edit'),
    (r'^(?P<organization_id>\d+)/offices/(?P<office_id>\d+)/edit/$', 'office_edit'),
    (r'^(?P<organization_id>\d+)/offices/(?P<office_id>\d+)/delete/$', 'office_delete'),
    (r'^(?P<organization_id>\d+)/offices/(?P<office_id>\d+)/merge/$', 'office_merge'),
    (r'^(?P<organization_id>\d+)/offices/(?P<office1_id>\d+)/merge/(?P<office2_id>\d+)/$', \
         'office_merge_perform'),

)

