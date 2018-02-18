# -*- coding: utf-8
"""
 ain7/adhesions/urls.py
"""
#
#   Copyright © 2007-2018 AIn7 Devel Team
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

from ain7.adhesions import views


urlpatterns = [
    url(r'^$', views.index, name='subscriptions'),
    url(r'^subscriptions/to_validate$', views.subscriptions, {'to_validate': True}, 'to_validate_subscriptions'),
    url(r'^subscriptions/(?P<subscription_id>\d+)/validate/$', views.subscription_validate, name='subscription-validate'),
    url(r'^subscriptions/(?P<subscription_id>\d+)/delete/$', views.subscription_delete, name='subscription-delete'),
    url(r'^(?P<person_id>\d+)/subscriptions/$', views.user_subscriptions, name='user-subscriptions'),
    url(r'^(?P<person_id>\d+)/subscriptions/add/$', views.subscription_add, name='subscription-add'),
    url(r'^configurations/$', views.configurations, name='configurations'),
    url(r'^configurations/(?P<year>\d+)/$', views.configurations, name='configurations-details'),
    url(r'^configurations/(?P<year>\d+)/(?P<config_id>\d+)/edit/$', views.configuration_edit, name='configuration-edit'),
    url(r'^configurations/(?P<year>\d+)/(?P<config_id>\d+)/delete/$', views.configuration_delete, name='configuration-delete'),
    url(r'^configurations/add/$', views.configuration_edit, {}, 'configuration_add'),
    url(r'^welcome/(?P<person_id>\d+)/$', views.welcome_subscription, name='subscription-welcome'),
    url(r'^notification/$', views.notification),
    url(r'^subscribe/$', views.subscription_add, name='subscribe-public'),
]
