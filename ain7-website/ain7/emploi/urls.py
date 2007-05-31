# -*- coding: utf-8
#
# emploi/urls.py
#
#   Copyright (C) 2007 AIn7
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

urlpatterns = patterns('',

    # Emploi
    (r'^$', 'ain7.emploi.views.index'),
    (r'^search/$', 'ain7.emploi.views.search'),
    # CV
    (r'^(?P<user_id>\d+)/cv/$', 'ain7.emploi.views.cv_details'),
    (r'^(?P<user_id>\d+)/cv/edit/$', 'ain7.emploi.views.cv_edit'),
    (r'^(?P<user_id>\d+)/cv/edit/position/(?P<position_id>\d+)/$',
     'ain7.emploi.views.position_edit'),
    (r'^(?P<user_id>\d+)/cv/delete/position/(?P<position_id>\d+)/$',
     'ain7.emploi.views.position_delete'),
    (r'^(?P<user_id>\d+)/cv/add/position/$',
     'ain7.emploi.views.position_add'),
    (r'^(?P<user_id>\d+)/cv/edit/education/(?P<education_id>\d+)/$',
     'ain7.emploi.views.education_edit'),
    (r'^(?P<user_id>\d+)/cv/delete/education/(?P<education_id>\d+)/$',
     'ain7.emploi.views.education_delete'),
    (r'^(?P<user_id>\d+)/cv/add/education/$',
     'ain7.emploi.views.education_add'),
    (r'^(?P<user_id>\d+)/cv/edit/leisure/(?P<leisure_id>\d+)/$',
     'ain7.emploi.views.leisure_edit'),
    (r'^(?P<user_id>\d+)/cv/delete/leisure/(?P<leisure_id>\d+)/$',
     'ain7.emploi.views.leisure_delete'),
    (r'^(?P<user_id>\d+)/cv/add/leisure/$',
     'ain7.emploi.views.leisure_add'),
    (r'^(?P<user_id>\d+)/cv/create/office/$',
     'ain7.emploi.views.office_create'),
    (r'^(?P<user_id>\d+)/cv/create/company/$',
     'ain7.emploi.views.company_create'),
    # Job offers
    (r'^job/register/$', 'ain7.emploi.views.job_register'),
    (r'^job/search/$', 'ain7.emploi.views.job_search'),
    (r'^job/(?P<emploi_id>\d+)/$', 'ain7.emploi.views.job_details'),
    (r'^job/(?P<emploi_id>\d+)/edit/$', 'ain7.emploi.views.job_edit'),
    # Company
    (r'^societe/(?P<company_id>\d+)/$', 'ain7.emploi.views.company_details'),

)
