# -*- coding: utf-8
"""
 ain7/association/urls.py
"""
#
#   Copyright © 2007-2017 AIn7 Devel Team
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

from ain7.association import views


urlpatterns = [
    url(r'^$', views.index, name='association-index'),
    url(r'^council/$', views.council, name='council-details'),
    url(r'^council/add/$', views.edit_council_role, name='council-role-add'),
    url(r'^council/edit/(?P<role_id>\d+)/$', views.edit_council_role, name='council-role-edit'),
    url(r'^council/delete/(?P<role_id>\d+)/$', views.delete_council_role, name='council-role-delete'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^status/$', views.status, name='status'),
    url(r'^internalrules/$', views.internalrules, name='internalrules'),
]
