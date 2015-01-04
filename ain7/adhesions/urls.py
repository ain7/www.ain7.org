# -*- coding: utf-8
"""
 ain7/adhesions/urls.py
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


urlpatterns = patterns('ain7.adhesions.views',
    url(r'^$', 'index', name='adhesions-index'),
    url(r'^subscriptions/to_validate$', 'subscriptions', {'to_validate': True}, 'to_validate_subscriptions'),
    url(r'^subscriptions/(?P<subscription_id>\d+)/validate/$', 'subscription_validate'),
    url(r'^subscriptions/(?P<subscription_id>\d+)/delete/$', 'subscription_delete'),
    url(r'^(?P<user_id>\d+)/subscriptions/$', 'user_subscriptions'),
    url(r'^(?P<user_id>\d+)/subscriptions/add/$', 'subscription_add'),
    url(r'^configurations/$', 'configurations', name='configurations'),
    url(r'^configurations/(?P<year>\d+)/$', 'configurations', name='configurations-details'),
    url(r'^configurations/(?P<year>\d+)/(?P<config_id>\d+)/edit/$', 'configuration_edit'),
    url(r'^configurations/(?P<year>\d+)/(?P<config_id>\d+)/delete/$', 'configuration_delete'),
    url(r'^configurations/add/$', 'configuration_edit', {}, 'configuration_add'),
    url(r'^notification/$', 'notification'),

)
