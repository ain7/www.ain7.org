# -*- coding: utf-8
"""
 ain7/manage/urls.py
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

urlpatterns = patterns('ain7.manage.views',
    (r'^$', 'index'),
                      
    # Users
    (r'^users/$', 'users_search'),
    (r'^users/register/$', 'user_register'),

    # Errors
    url(r'^errors/$', 'errors_index', name='errors-index'),
    url(r'^errors/(?P<error_id>\d+)/$', 'error_details', name='error-details'),
    (r'^errors/edit_range/$', 'errors_edit_range'),
    (r'^errors/(?P<error_id>\d+)/swap/$', 'error_swap'),

    # Payment
    (r'^payments/$', 'payments_index'),
    (r'^payments/add/$', 'payment_edit'),
    url(r'^payments/(?P<payment_id>\d+)/$', 'payment_details', name='payment-details'),
    (r'^payments/(?P<payment_id>\d+)/edit/$', 'payment_edit'),
    url(r'^payments/deposit/$', 'payments_deposit_index', name='payments-deposit-index'),
    (r'^payments/deposit/(?P<deposit_id>\d+)/$', 'payments_deposit'),
    (r'^payments/deposit/(?P<deposit_id>\d+)/deposited/'
     +r'(?P<last_deposit_id>\d+)/$', 'payments_mark_deposited'),

    # Registrations
    url(r'^registrations/$', 'registrations_index', name='registrations-index'),
    url(r'^registrations/(?P<person_id>\d+)/validate/$', 'registration_validate', name='registration-validate'),
    url(r'^registrations/(?P<person_id>\d+)/delete/$', 'registration_delete', name='registration-delete'),

    # Subscriptions
    url(r'^subscriptions/$', 'subscriptions_stats'),
    url(
        r'^subscriptions/(?P<the_year>\d+)/$', 'subscriptions_stats',
        name='subscriptions-stats-per-year',
    ),
    url(
        r'^subscriptions/(?P<the_year>\d+)/csv/$', 'subscribers_csv',
        name='subscribers-csv',
    ),
    url(
        r'^subscriptions/(?P<the_year>\d+)/students/csv/$', 'subscribers_csv',
        {'normal': False, 'students': True}, name='subscribers-students-csv',
    ),
    url(
        r'^subscriptions/(?P<the_year>\d+)/magazine/csv/$', 'subscribers_csv',
        {'normal': False, 'magazine': True}, name='subscribers-magazine-csv',
    ),

    url(r'^sitestats/$', 'site_stats'),

    # mailings
    url(r'^mailings/$', 'mailings_index', name='mailings-index'),
    url(r'^mailings/add/$', 'mailing_edit', name='mailing-add'),
    url(r'^mailings/(?P<mailing_id>\d+)/$', 'mailing_edit', name='mailing-edit'),
    (r'^mailings/(?P<mailing_id>\d+)/test/$', 'mailing_send'),
    (r'^mailings/(?P<mailing_id>\d+)/testteam/$', 'mailing_sendteam'),
    (r'^mailings/(?P<mailing_id>\d+)/send/$', 'mailing_ready'),
    (r'^mailings/(?P<mailing_id>\d+)/csv/$', 'mailing_export'),
    (r'^mailings/(?P<mailing_id>\d+)/view/$', 'mailing_view'),

)

