# -*- coding: utf-8
"""
 ain7/annuaire/urls.py
"""
#
#   Copyright © 2007-2016 AIn7 Devel Team
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

urlpatterns = patterns('ain7.annuaire.views',
    # Annuaire
    url(r'^$', 'search', name='annuaire-search'),
    url(r'^search/$', 'search_adv', name='annuaire-search-advanced'),
    url(r'^add/$', 'add', name='member-add'),
    url(r'^(?P<user_id>\d+)/$', 'details', name='member-details'),
    # Edition
    url(r'^(?P<user_id>\d+)/edit/$', 'edit', name='annuaire-edit'),
    url(r'^(?P<user_id>\d+)/credentials/$', 'change_credentials'),
    url(r'^(?P<user_id>\d+)/sendcredentials/$', 'send_new_credentials', name='send-new-credentials'),
    url(r'^(?P<user_id>\d+)/person/edit/$', 'person_edit', name='member-person-edit'),
    url(r'^(?P<user_id>\d+)/personprivate/edit/$', 'personprivate_edit', name='member-personprivate-edit'),
    url(r'^(?P<user_id>\d+)/ain7member/edit/$', 'ain7member_edit', name='member-ain7member-edit'),
    # Promos
    (r'^(?P<user_id>\d+)/promo/(?P<promo_id>\d+)/delete/$', 'promo_delete'),
    (r'^(?P<user_id>\d+)/promo/add/$', 'promo_edit'),
    # Adresses
    (r'^(?P<user_id>\d+)/address/(?P<address_id>\d+)/edit/$', 'address_edit'),
    (r'^(?P<user_id>\d+)/address/(?P<address_id>\d+)/delete/$',
        'address_delete'),
    (r'^(?P<user_id>\d+)/address/add/$', 'address_edit'),
    # Phone numbers
    (r'^(?P<user_id>\d+)/phone/(?P<phone_id>\d+)/edit/$', 'phone_edit'),
    (r'^(?P<user_id>\d+)/phone/(?P<phone_id>\d+)/delete/$', 'phone_delete'),
    (r'^(?P<user_id>\d+)/phone/add/$', 'phone_edit'),
    # Email
    (r'^(?P<user_id>\d+)/email/(?P<email_id>\d+)/edit/$', 'email_edit'),
    (r'^(?P<user_id>\d+)/email/(?P<email_id>\d+)/delete/$', 'email_delete'),
    (r'^(?P<user_id>\d+)/email/add/$', 'email_edit'),
    # Instant messaging
    (r'^(?P<user_id>\d+)/im/(?P<im_id>\d+)/edit/$', 'im_edit'),
    (r'^(?P<user_id>\d+)/im/(?P<im_id>\d+)/delete/$', 'im_delete'),
    (r'^(?P<user_id>\d+)/im/add/$', 'im_edit'),
    # Sites Web
    (r'^(?P<user_id>\d+)/website/(?P<website_id>\d+)/edit/$', 'website_edit'),
    (r'^(?P<user_id>\d+)/website/(?P<website_id>\d+)/delete/$',
        'website_delete'),
    (r'^(?P<user_id>\d+)/website/add/$', 'website_edit'),
    # Activités associatives n7
    (r'^(?P<user_id>\d+)/club_membership/(?P<club_membership_id>\d+)/edit/$',
        'club_membership_edit'),
    (r'^(?P<user_id>\d+)/club_membership/(?P<club_membership_id>\d+)/delete/$',
        'club_membership_delete'),
    (r'^(?P<user_id>\d+)/club_membership/add/$', 'club_membership_edit'),
    # positions
    url(r'^(?P<user_id>\d+)/position/(?P<position_id>\d+)/edit/$',
        'position_edit', name='position-edit'),
    url(r'^(?P<user_id>\d+)/position/(?P<position_id>\d+)/delete/$',
        'position_delete', name='position-delete'),
    url(r'^(?P<user_id>\d+)/position/add/$', 'position_edit',
        name='position-add'),
    # education
    url(r'^(?P<user_id>\d+)/education/(?P<education_id>\d+)/edit/$',
        'education_edit', name='education-edit'),
    url(r'^(?P<user_id>\d+)/education/(?P<education_id>\d+)/delete/$',
        'education_delete', name='education-delete'),
    url(r'^(?P<user_id>\d+)/cv/education/add/$', 'education_edit',
        name='education-add'),
    # leisures
    url(r'^(?P<user_id>\d+)/leisure/(?P<leisure_id>\d+)/edit/$',
        'leisure_edit', name='leisure-edit'),
    url(r'^(?P<user_id>\d+)/leisure/(?P<leisure_id>\d+)/delete/$',
        'leisure_delete', name='leisure-delete'),
    url(r'^(?P<user_id>\d+)/cv/leisure/add/$', 'leisure_edit',
        name='leisure-add'),
    # publications
    url(r'^(?P<user_id>\d+)/publication/(?P<publication_id>\d+)/delete/$',
        'publication_delete', name='publication-delete'),
    url(r'^(?P<user_id>\d+)/publication/(?P<publication_id>\d+)/edit/$',
        'publication_edit', name='publication-edit'),
    url(r'^(?P<user_id>\d+)/publication/add/$', 'publication_edit',
        name='publication-add'),
    # vCard
    (r'^(?P<user_id>\d+)/vcard/$', 'vcard'),

)
