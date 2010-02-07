# -*- coding: utf-8
"""
 ain7/association/urls.py
"""
#
#   Copyright © 2007-2009 AIn7 Devel Team
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


urlpatterns = patterns('ain7.association.views',
    (r'^$', 'index'),
    (r'^council/$', 'council'),
    (r'^council/edit/(?P<all_current>\w+)/$', 'edit_council'),
    (r'^council/(?P<role_id>\d+)/changedates/(?P<all_current>\w+)/$',
        'change_council_dates'),
    (r'^council/(?P<role_type>\d+)/add/(?P<all_current>\w+)/$',
        'add_council_role'),
    (r'^council/(?P<role_id>\d+)/delete/(?P<all_current>\w+)/$',
        'delete_council_role'),
    (r'^contact/$', 'contact'),
    (r'^status/$', 'status'),
    (r'^activites/$', 'activites'),

)
