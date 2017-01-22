# -*- coding: utf-8
"""
 ain7/manage/urls.py
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

from ain7.manage import views

urlpatterns = [
    url(r'^$', views.index),

    # Errors
    url(r'^errors/$', views.errors_index, name='errors-index'),
    url(r'^errors/(?P<error_id>\d+)/$', views.error_details, name='error-details'),

    # Payment
    url(r'^payments/$', views.payments_index, name='payments-index'),
    url(r'^payments/add/$', views.payment_edit),
    url(r'^payments/(?P<payment_id>\d+)/$', views.payment_details, name='payment-details'),
    url(r'^payments/(?P<payment_id>\d+)/edit/$', views.payment_edit, name='payment-edit'),
    url(r'^payments/deposit/$', views.payments_deposit_index, name='payments-deposit-index'),
    url(r'^payments/deposit/(?P<deposit_id>\d+)/$', views.payments_deposit, name='payments-deposit-details'),
    url(r'^payments/deposit/(?P<deposit_id>\d+)/deposited/(?P<last_deposit_id>\d+)/$', views.payments_mark_deposited, name='payments-mark-deposited'),

    # Registrations
    url(r'^registrations/$', views.registrations_index, name='registrations-index'),
    url(r'^registrations/(?P<person_id>\d+)/validate/$', views.registration_validate, name='registration-validate'),
    url(r'^registrations/(?P<person_id>\d+)/delete/$', views.registration_delete, name='registration-delete'),

    # Subscriptions
    url(r'^subscriptions/$', views.subscriptions_stats,
        name='subscriptions-stats'),
    url(
        r'^subscriptions/(?P<the_year>\d+)/$', views.subscriptions_stats,
        name='subscriptions-stats-per-year',
    ),
    url(
        r'^subscriptions/(?P<the_year>\d+)/csv/$', views.subscribers_csv,
        name='subscribers-csv',
    ),
    url(
        r'^subscriptions/(?P<the_year>\d+)/students/csv/$', views.subscribers_csv,
        {'normal': False, 'students': True}, name='subscribers-students-csv',
    ),
    url(
        r'^subscriptions/(?P<the_year>\d+)/magazine/csv/$', views.subscribers_csv,
        {'normal': False, 'magazine': True}, name='subscribers-magazine-csv',
    ),

    url(r'^sitestats/$', views.site_stats, name='site-stats'),

    # mailings
    url(r'^mailings/$', views.mailings_index, name='mailings-index'),
    url(r'^mailings/add/$', views.mailing_edit, name='mailing-add'),
    url(r'^mailings/(?P<mailing_id>\d+)/$', views.mailing_edit, name='mailing-edit'),
    url(r'^mailings/(?P<mailing_id>\d+)/test/$', views.mailing_send, name='mailing-test-send'),
    url(r'^mailings/(?P<mailing_id>\d+)/testteam/$', views.mailing_sendteam, name='mailing-test-send-team'),
    url(r'^mailings/(?P<mailing_id>\d+)/send/$', views.mailing_ready, name='mailing-send'),
    url(r'^mailings/(?P<mailing_id>\d+)/csv/$', views.mailing_export, name='mailing-csv'),
    url(r'^mailings/(?P<mailing_id>\d+)/view/$', views.mailing_view, name='mailing-view'),
]
