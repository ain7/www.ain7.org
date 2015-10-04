# -*- coding: utf-8
"""
 ain7/adhesions/models.py
"""
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

import datetime
import uuid

from django.db import models
from django.utils.translation import ugettext as _

from ain7.utils import LoggedClass


class Subscription(LoggedClass):
    """
    AIn7Member Subscription
    """

    TENDER_TYPE_CASH = 1
    TENDER_TYPE_CHECK = 2
    TENDER_TYPE_CARD = 4
    TENDER_TYPE_WIRE_TRANSFER = 5
    TENDER_TYPE_OTHER = 6
    TENDER_TYPE = (
        (1, _('Cash')),
        (2, _('Cheque')),
        (4, _('Card')),
        (5, _('Transfer')),
        (6, _('Other')),
    )

    # For potential backward compatibility
    old_id = models.IntegerField(
        verbose_name='old id', blank=True, null=True, unique=True
    )

    member = models.ForeignKey(
        'annuaire.AIn7Member', verbose_name=_('member'),
        related_name='subscriptions',
    )

    payment = models.ForeignKey(
        'shop.Payment', verbose_name=_('payment'),
        null=True, related_name='subscriptions',
    )

    dues_amount = models.FloatField(verbose_name=_('Dues amount'))
    newspaper_amount = models.FloatField(
        verbose_name=_('Newspaper amount'), null=True, blank=True,
    )
    tender_type = models.IntegerField(
        verbose_name=_('Tender type'), choices=TENDER_TYPE,
    )
    validated = models.BooleanField(verbose_name=_('validated'), default=False)

    date = models.DateTimeField(
        verbose_name=_('subscription date'), null=True, blank=True,
    )

    start_year = models.IntegerField(verbose_name=_('start year'))
    end_year = models.IntegerField(verbose_name=_('end year'))

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    configuration = models.ForeignKey(
        'SubscriptionConfiguration', blank=True, null=True
    )

    def __unicode__(self):
        """unicode string for subscription object"""
        return u'%s %s → %s' % (self.member, self.start_year, self.end_year)

    class Meta:
        """Meta"""
        verbose_name = _('Subscription')
        ordering = ['id']


class SubscriptionConfiguration(models.Model):
    """
    AIn7Member Subscription Configuration
    """

    TYPE_REGULAR = 0
    TYPE_LAST_PROMOS = 1
    TYPE_RETIRED = 2
    TYPE_DONATOR = 3
    TYPE_UNEMPLOYED = 4
    TYPE_STUDENT_3Y = 5
    TYPE_STUDENT_2Y = 6
    TYPE_STUDENT_1Y = 7
    TYPE_PARTNERS = 7
    TYPE = (
        (0, _('Promotions before %(year)s') % {
            'year': datetime.date.today().year-5
            }),
        (1, _('Promotions from %(start_year)s to %(end_year)s') % {
            'start_year': datetime.date.today().year-5,
            'end_year': datetime.date.today().year-1,
            }),
        (2, _('Retired')),
        (3, _('Donator')),
        (4, _('Unemployed (with voucher)')),
        (5, _('Student, for three years')),
        (6, _('Student, for two years')),
        (7, _('Student, for one year')),
        (8, _('Couple')),
        (9, _('Support')),
    )

    type = models.IntegerField(verbose_name=_('Type'), choices=TYPE)
    dues_amount = models.IntegerField(verbose_name=_('Dues amount'))
    newspaper_amount = models.IntegerField(
        verbose_name=_('Newspaper amount'), null=True, blank=True,
    )
    duration = models.IntegerField(verbose_name=_('Duration'), default=1)
    year = models.IntegerField(verbose_name=_('Year'))

    def __unicode__(self):
        """unicode string for subscriptionconfiguration object"""
        return self.get_type_display()

    class Meta:
        """Meta"""
        verbose_name = _('Configuration')


#class SubscriptionKey(models.Model):
#
#    person = models.ForeignKey('annuaire.Person', null=False)
#    key = models.UUIDField(default=uuid.uuid4, editable=False)
#    created_at = models.DateTimeField(auto_now_add=True, editable=False)
#    expire_at = models.DateTimeField(editable=False)
