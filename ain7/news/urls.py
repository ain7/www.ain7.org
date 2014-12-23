# -*- coding: utf-8
"""
 ain7/news/urls.py
"""
#
#   Copyright © 2007-2011 AIn7 Devel Team
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


urlpatterns = patterns('ain7.news.views',
    # Evenements
    (r'^$', 'index'),
    (r'^new/$', 'edit'),
    (r'^search/$', 'search'),
    (r'^(?P<news_slug>[\w\-]+)/$', 'details'),
    (r'^(?P<news_slug>[\w\-]+)/edit/$', 'edit'),
    (r'^(?P<news_slug>[\w\-]+)/delete/$', 'delete'),
    (r'^(?P<news_slug>[\w\-]+)/image/delete/$', 'image_delete'),

)
