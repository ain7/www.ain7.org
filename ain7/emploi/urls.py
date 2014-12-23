# -*- coding: utf-8
"""
 ain7/emploi/urls.py
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

from django.conf.urls import patterns


urlpatterns = patterns('ain7.emploi.views',

    # Emploi
    (r'^$', 'index'),
    # CV
    (r'^(?P<user_id>\d+)/cv/$', 'cv_details'),
    (r'^(?P<user_id>\d+)/cv/edit/$', 'cv_edit'),
    (r'^(?P<user_id>\d+)/cv/position/(?P<position_id>\d+)/edit/$',
        'position_edit'),
    (r'^(?P<user_id>\d+)/cv/position/(?P<position_id>\d+)/delete/$',
        'position_delete'),
    (r'^(?P<user_id>\d+)/cv/position/add/$', 'position_edit'),
    (r'^(?P<user_id>\d+)/cv/education/(?P<education_id>\d+)/edit/$',
        'education_edit'),
    (r'^(?P<user_id>\d+)/cv/education/(?P<education_id>\d+)/delete/$',
        'education_delete'),
    (r'^(?P<user_id>\d+)/cv/education/add/$', 'education_edit'),
    (r'^(?P<user_id>\d+)/cv/leisure/(?P<leisure_id>\d+)/edit/$',
        'leisure_edit'),
    (r'^(?P<user_id>\d+)/cv/leisure/(?P<leisure_id>\d+)/delete/$',
        'leisure_delete'),
    (r'^(?P<user_id>\d+)/cv/leisure/add/$', 'leisure_edit'),
    (r'^(?P<user_id>\d+)/cv/publication/(?P<publication_id>\d+)/delete/$',
        'publication_delete'),
    (r'^(?P<user_id>\d+)/cv/publication/(?P<publication_id>\d+)/edit/$',
        'publication_edit'),
    (r'^(?P<user_id>\d+)/cv/publication/add/$', 'publication_edit'),
    # Job offers
    (r'^job/add/$', 'job_register'),
    (r'^job/search/$', 'job_search'),
    (r'^job/(?P<emploi_id>\d+)/$', 'job_details'),
    (r'^job/(?P<emploi_id>\d+)/edit/$', 'job_edit'),
    (r'^job/proposals/$', 'jobs_proposals'),
    (r'^job/proposals/(?P<job_id>\d+)/validate/$', 'job_validate'),
    (r'^job/proposals/(?P<job_id>\d+)/delete/$', 'job_delete'),

)
