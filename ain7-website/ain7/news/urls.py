# -*- coding: utf-8
#
# news/urls.py
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

    # Evenements
    (r'^$', 'ain7.news.views.index'),
    (r'^write/$', 'ain7.news.views.write'),
    (r'^search/$', 'ain7.news.views.search'),
    (r'^(?P<news_id>\d+)/$', 'ain7.news.views.details'),
    (r'^(?P<news_id>\d+)/edit/$', 'ain7.news.views.edit'),
    (r'^(?P<news_id>\d+)/image/edit/$', 'ain7.news.views.image_edit'),

)
