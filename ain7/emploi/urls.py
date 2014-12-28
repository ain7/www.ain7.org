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

from django.conf.urls import patterns, url


urlpatterns = patterns('ain7.emploi.views',

    # Emploi
    url(r'^$', 'index', name='job-index'),
    # CV
    url(r'^(?P<user_id>\d+)/cv/$', 'cv_details', name='cv-details'),
    url(r'^(?P<user_id>\d+)/cv/edit/$', 'cv_edit', name='cv-edit'),
    url(r'^(?P<user_id>\d+)/cv/position/(?P<position_id>\d+)/edit/$',
        'position_edit', name='position-edit'),
    url(r'^(?P<user_id>\d+)/cv/position/(?P<position_id>\d+)/delete/$',
        'position_delete', name='position-delete'),
    url(r'^(?P<user_id>\d+)/cv/position/add/$', 'position_edit', name='position-add'),
    url(r'^(?P<user_id>\d+)/cv/education/(?P<education_id>\d+)/edit/$',
        'education_edit', name='education-edit'),
    url(r'^(?P<user_id>\d+)/cv/education/(?P<education_id>\d+)/delete/$',
        'education_delete', name='education-delete'),
    url(r'^(?P<user_id>\d+)/cv/education/add/$', 'education_edit', name='education-add'),
    url(r'^(?P<user_id>\d+)/cv/leisure/(?P<leisure_id>\d+)/edit/$',
        'leisure_edit', name='leisure-edit'),
    url(r'^(?P<user_id>\d+)/cv/leisure/(?P<leisure_id>\d+)/delete/$',
        'leisure_delete', name='leisure-delete'),
    url(r'^(?P<user_id>\d+)/cv/leisure/add/$', 'leisure_edit', name='leisure-add'),
    url(r'^(?P<user_id>\d+)/cv/publication/(?P<publication_id>\d+)/delete/$',
        'publication_delete', name='publication-delete'),
    url(r'^(?P<user_id>\d+)/cv/publication/(?P<publication_id>\d+)/edit/$',
        'publication_edit', name='publication-edit'),
    url(r'^(?P<user_id>\d+)/cv/publication/add/$', 'publication_edit', name='publication-add'),
    # Job offers
    (r'^job/add/$', 'job_edit'),
    url(r'^job/search/$', 'job_search', name='jobs-search'),
    url(r'^job/(?P<job_id>\d+)/$', 'job_details', name='job-details'),
    url(r'^job/(?P<job_id>\d+)/edit/$', 'job_edit', name='job-edit'),
    url(r'^job/proposals/$', 'jobs_proposals', name='jobs-proposals'),
    url(r'^job/proposals/(?P<job_id>\d+)/validate/$', 'job_validate', name='job-validate'),
    url(r'^job/proposals/(?P<job_id>\d+)/delete/$', 'job_delete', name='job-delete'),

)
