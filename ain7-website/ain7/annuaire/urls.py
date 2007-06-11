# -*- coding: utf-8
#
# annuaire/urls.py
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

    # Annuaire
    (r'^$', 'ain7.annuaire.views.search'),
    (r'^(?P<person_id>\d+)/$', 'ain7.annuaire.views.detail'),
    # Edition
    (r'^(?P<person_id>\d+)/edit/$', 'ain7.annuaire.views.edit'),
    (r'^(?P<user_id>\d+)/person/edit/$', 'ain7.annuaire.views.person_edit'),
    (r'^(?P<user_id>\d+)/ain7member/edit/$',
     'ain7.annuaire.views.ain7member_edit'),
    # Adresses
    (r'^(?P<user_id>\d+)/address/(?P<address_id>\d+)/edit/$',
     'ain7.annuaire.views.address_edit'),
    (r'^(?P<user_id>\d+)/address/(?P<address_id>\d+)/delete/$',
     'ain7.annuaire.views.address_delete'),
    (r'^(?P<user_id>\d+)/address/add/$', 'ain7.annuaire.views.address_add'),
    # Phone numbers
    (r'^(?P<user_id>\d+)/phone/(?P<phone_id>\d+)/edit/$',
     'ain7.annuaire.views.phone_edit'),
    (r'^(?P<user_id>\d+)/phone/(?P<phone_id>\d+)/delete/$',
     'ain7.annuaire.views.phone_delete'),
    (r'^(?P<user_id>\d+)/phone/add/$', 'ain7.annuaire.views.phone_add'),
    # Email
    (r'^(?P<user_id>\d+)/email/(?P<email_id>\d+)/edit/$',
     'ain7.annuaire.views.email_edit'),
    (r'^(?P<user_id>\d+)/email/(?P<email_id>\d+)/delete/$',
     'ain7.annuaire.views.email_delete'),
    (r'^(?P<user_id>\d+)/email/add/$', 'ain7.annuaire.views.email_add'),
    # Instant messaging
    (r'^(?P<user_id>\d+)/im/(?P<im_id>\d+)/edit/$',
     'ain7.annuaire.views.im_edit'),
    (r'^(?P<user_id>\d+)/im/(?P<im_id>\d+)/delete/$',
     'ain7.annuaire.views.im_delete'),
    (r'^(?P<user_id>\d+)/im/add/$', 'ain7.annuaire.views.im_add'),
    # Comptes IRC 
    (r'^(?P<user_id>\d+)/irc/(?P<irc_id>\d+)/edit/$',
     'ain7.annuaire.views.irc_edit'),
    (r'^(?P<user_id>\d+)/irc/(?P<irc_id>\d+)/delete/$',
     'ain7.annuaire.views.irc_delete'),
    (r'^(?P<user_id>\d+)/irc/add/$', 'ain7.annuaire.views.irc_add'),
    # Sites Web 
    (r'^(?P<user_id>\d+)/website/(?P<website_id>\d+)/edit/$',
     'ain7.annuaire.views.website_edit'),
    (r'^(?P<user_id>\d+)/website/(?P<website_id>\d+)/delete/$',
     'ain7.annuaire.views.website_delete'),
    (r'^(?P<user_id>\d+)/website/add/$', 'ain7.annuaire.views.website_add'),
    # Activités associatives n7
    (r'^(?P<user_id>\d+)/club_membership/(?P<club_membership_id>\d+)/edit/$',
     'ain7.annuaire.views.club_membership_edit'),
    (r'^(?P<user_id>\d+)/club_membership/(?P<club_membership_id>\d+)/delete/$',
     'ain7.annuaire.views.club_membership_delete'),
    (r'^(?P<user_id>\d+)/club_membership/add/$',
     'ain7.annuaire.views.club_membership_add'),

)
