# -*- coding: utf-8
"""
 ain7/annuaire/urls.py
"""
#
#   Copyright © 2007-2017 AIn7 Devel Team
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

from ain7.annuaire import views

urlpatterns = [
    # Annuaire
    url(r'^$', views.search, name='annuaire-search'),
    url(r'^search/$', views.search_adv, name='annuaire-search-advanced'),
    url(r'^add/$', views.add, name='member-add'),
    url(r'^(?P<user_id>\d+)/$', views.details, name='member-details'),
    # Edition
    url(r'^(?P<user_id>\d+)/edit/$', views.edit, name='annuaire-edit'),
    url(r'^(?P<user_id>\d+)/credentials/$', views.change_credentials, name='change-credentials'),
    url(r'^(?P<user_id>\d+)/sendcredentials/$', views.send_new_credentials, name='send-new-credentials'),
    url(r'^(?P<user_id>\d+)/setcredentials/$', views.set_new_credentials, name='set-new-credentials'),
    url(r'^(?P<user_id>\d+)/person/edit/$', views.person_edit, name='member-person-edit'),
    url(r'^(?P<user_id>\d+)/personprivate/edit/$', views.personprivate_edit, name='member-personprivate-edit'),
    url(r'^(?P<user_id>\d+)/ain7member/edit/$', views.ain7member_edit, name='member-ain7member-edit'),
    # Promos
    url(r'^(?P<user_id>\d+)/promo/(?P<promo_id>\d+)/delete/$', views.promo_delete, name='member-promo-delete'),
    url(r'^(?P<user_id>\d+)/promo/add/$', views.promo_edit, name='member-promo-add'),
    # Adresses
    url(r'^(?P<user_id>\d+)/address/(?P<address_id>\d+)/edit/$', views.address_edit, name='member-address-edit'),
    url(r'^(?P<user_id>\d+)/address/(?P<address_id>\d+)/delete/$', views.address_delete, name='member-address-delete'),
    url(r'^(?P<user_id>\d+)/address/add/$', views.address_edit, name='member-address-add'),
    # Phone numbers
    url(r'^(?P<user_id>\d+)/phone/(?P<phone_id>\d+)/edit/$', views.phone_edit, name='member-phone-edit'),
    url(r'^(?P<user_id>\d+)/phone/(?P<phone_id>\d+)/delete/$', views.phone_delete, name='member-phone-delete'),
    url(r'^(?P<user_id>\d+)/phone/add/$', views.phone_edit, name='member-phone-add'),
    # Email
    url(r'^(?P<user_id>\d+)/email/(?P<email_id>\d+)/edit/$', views.email_edit, name='member-email-edit'),
    url(r'^(?P<user_id>\d+)/email/(?P<email_id>\d+)/delete/$', views.email_delete, name='member-email-delete'),
    url(r'^(?P<user_id>\d+)/email/add/$', views.email_edit, name='member-email-add'),
    # Instant messaging
    url(r'^(?P<user_id>\d+)/im/(?P<im_id>\d+)/edit/$', views.im_edit),
    url(r'^(?P<user_id>\d+)/im/(?P<im_id>\d+)/delete/$', views.im_delete),
    url(r'^(?P<user_id>\d+)/im/add/$', views.im_edit),
    # Sites Web
    url(r'^(?P<user_id>\d+)/website/(?P<website_id>\d+)/edit/$', views.website_edit, name='member-website-edit'),
    url(r'^(?P<user_id>\d+)/website/(?P<website_id>\d+)/delete/$', views.website_delete, name='member-website-delete'),
    url(r'^(?P<user_id>\d+)/website/add/$', views.website_edit, name='member-website-add'),
    # Activités associatives n7
    url(r'^(?P<user_id>\d+)/club_membership/(?P<club_membership_id>\d+)/edit/$', views.club_membership_edit, name='member-clubmembership-edit'),
    url(r'^(?P<user_id>\d+)/club_membership/(?P<club_membership_id>\d+)/delete/$', views.club_membership_delete, name='member-clubmembership-delete'),
    url(r'^(?P<user_id>\d+)/club_membership/add/$', views.club_membership_edit, name='member-clubmembership-add'),
    # positions
    url(r'^(?P<user_id>\d+)/position/(?P<position_id>\d+)/edit/$', views.position_edit, name='member-position-edit'),
    url(r'^(?P<user_id>\d+)/position/(?P<position_id>\d+)/delete/$', views.position_delete, name='member-position-delete'),
    url(r'^(?P<user_id>\d+)/position/add/$', views.position_edit, name='member-position-add'),
    # education
    url(r'^(?P<user_id>\d+)/education/(?P<education_id>\d+)/edit/$', views.education_edit, name='member-education-edit'),
    url(r'^(?P<user_id>\d+)/education/(?P<education_id>\d+)/delete/$', views.education_delete, name='member-education-delete'),
    url(r'^(?P<user_id>\d+)/cv/education/add/$', views.education_edit, name='member-education-add'),
    # leisures
    url(r'^(?P<user_id>\d+)/leisure/(?P<leisure_id>\d+)/edit/$', views.leisure_edit, name='member-leisure-edit'),
    url(r'^(?P<user_id>\d+)/leisure/(?P<leisure_id>\d+)/delete/$', views.leisure_delete, name='member-leisure-delete'),
    url(r'^(?P<user_id>\d+)/cv/leisure/add/$', views.leisure_edit, name='member-leisure-add'),
    # publications
    url(r'^(?P<user_id>\d+)/publication/(?P<publication_id>\d+)/delete/$', views.publication_delete, name='member-publication-delete'),
    url(r'^(?P<user_id>\d+)/publication/(?P<publication_id>\d+)/edit/$', views.publication_edit, name='member-publication-edit'),
    url(r'^(?P<user_id>\d+)/publication/add/$', views.publication_edit, name='member-publication-add'),
    # vCard
    url(r'^(?P<user_id>\d+)/vcard/$', views.vcard, name='member-vcard'),
]
