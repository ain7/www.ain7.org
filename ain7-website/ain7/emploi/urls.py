# -*- coding: utf-8
#
# emploi/urls.py
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

from django.conf.urls.defaults import *


urlpatterns = patterns('ain7.emploi.views',

    # Emploi
    (r'^$', 'index'),
    # CV
    (r'^(?P<user_id>\d+)/cv/$', 'cv_details'),
    (r'^(?P<user_id>\d+)/cv/edit/$', 'cv_edit'),
    (r'^(?P<user_id>\d+)/cv/position/(?P<position_id>\d+)/edit/$', 'position_edit'),
    (r'^(?P<user_id>\d+)/cv/position/(?P<position_id>\d+)/delete/$', 'position_delete'),
    (r'^(?P<user_id>\d+)/cv/position/add/$', 'position_add'),
    (r'^(?P<user_id>\d+)/cv/education/(?P<education_id>\d+)/edit/$', 'education_edit'),
    (r'^(?P<user_id>\d+)/cv/education/(?P<education_id>\d+)/delete/$', 'education_delete'),
    (r'^(?P<user_id>\d+)/cv/education/add/$', 'education_add'),
    (r'^(?P<user_id>\d+)/cv/leisure/(?P<leisure_id>\d+)/edit/$', 'leisure_edit'),
    (r'^(?P<user_id>\d+)/cv/leisure/(?P<leisure_id>\d+)/delete/$', 'leisure_delete'),
    (r'^(?P<user_id>\d+)/cv/leisure/add/$', 'leisure_add'),
    (r'^(?P<user_id>\d+)/cv/publication/(?P<publication_id>\d+)/delete/$', 'publication_delete'),
    (r'^(?P<user_id>\d+)/cv/publication/(?P<publication_id>\d+)/edit/$', 'publication_edit'),
    (r'^(?P<user_id>\d+)/cv/publication/add/$', 'publication_add'),
    # Job offers
    (r'^job/register/$', 'job_register'),
    (r'^job/search/$', 'job_search'),
    (r'^job/(?P<emploi_id>\d+)/$', 'job_details'),
    (r'^job/(?P<emploi_id>\d+)/edit/$', 'job_edit'),
    # Organization
    (r'^organization/(?P<organization_id>\d+)/$', 'organization_details'),
    (r'^organization/edit/$', 'organization_choose', {'action': 'edit'}),
    (r'^organization/add/$', 'organization_add'),
    (r'^organization/delete/$', 'organization_choose', {'action': 'delete'}),
    (r'^organization/(?P<organization_id>\d+)/edit/$', 'organization_edit'),
    (r'^organization/(?P<organization_id>\d+)/editdata/$', 'organization_edit_data'),
    (r'^organization/(?P<organization_id>\d+)/delete/$', 'organization_delete'),
    # Offices
    (r'^office/(?P<office_id>\d+)/edit/$', 'office_edit'),
    (r'^office/(?P<office_id>\d+)/delete/$', 'office_delete'),
    (r'^organization/(?P<organization_id>\d+)/office/add/$', 'office_add'),
)
