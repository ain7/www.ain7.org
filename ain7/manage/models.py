# -*- coding: utf-8
"""
 ain7/manage/models.py
"""
#
#   Copyright © 2007-2010 AIn7 Devel Team
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

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from ain7.annuaire.models import Person
from ain7.emploi.models import OrganizationProposal, OfficeProposal, JobOffer
from ain7.utils import LoggedClass


class Notification(LoggedClass):
    """notification"""

    PROPOSAL_TYPE = (
        (0, _('organization')),
        (1, _('office')),
        )

    title = models.CharField(verbose_name=_('title'), max_length=50)
    details = models.TextField(verbose_name=_('Notes'),
        blank=True, null=True)
    organization_proposal = models.ForeignKey(
        OrganizationProposal, verbose_name=_('organization proposal'),
        blank=True, null=True)
    office_proposal = models.ForeignKey(
        OfficeProposal, verbose_name=_('organization proposal'),
        blank=True, null=True)
    job_proposal = models.ForeignKey( JobOffer, blank=True, null=True,
        verbose_name = _('job offer proposal'), related_name='notification')

    def __unicode__(self):
        """notification unicode method"""
        return self.title

    class Meta:
        """notification meta information"""
        verbose_name = _('notification')

class PortalError(models.Model):
    """portal error"""

    title = models.CharField(verbose_name=_('title'), max_length=200, 
        null=True, blank=True)
    user = models.ForeignKey(User, verbose_name=_('user'), 
        blank=True, null=True)
    date = models.DateTimeField(verbose_name=_('Date'))
    url = models.CharField(verbose_name=_('url'), max_length=500)
    referer = models.CharField(verbose_name=_('Referrer'), max_length=200,
        null=True, blank=True)
    browser_info = models.CharField(verbose_name=_('Browser info'), 
        max_length=200, null=True, blank=True)
    client_address = models.CharField(verbose_name=_('Client address'), 
        max_length=200, null=True, blank=True)
    exception = models.TextField(verbose_name=_('Exception'))
    comment = models.TextField(verbose_name=_('Comment'), null=True, blank=True)
    issue = models.CharField(verbose_name=_('Issue'), max_length=20, 
        null=True, blank=True)
    fixed = models.BooleanField(verbose_name=_('fixed'), default=False)

class Payment(models.Model):
    """payment"""

    TYPE = (
        (0, _('Cash')),
        (1, _('Check CE')),
        (2, _('Check CCP')),
        (3, _('Card')),
        (4, _('Transfer CE')),
        (5, _('Transfer CCP')),
        (6, _('Other')),
    )

    person = models.ForeignKey(Person, blank=True, null=True)
    amount = models.FloatField(verbose_name=_('amount'))
    type = models.IntegerField(verbose_name=_('Type'), choices=TYPE)

    bank = models.CharField(verbose_name=_('Bank'), max_length=200, 
        null=True, blank=True)
    check_number = models.CharField(verbose_name=_('Check number'),
        max_length=200, null=True, blank=True)
    date = models.DateField(verbose_name=_('payment date'), null=True)
    validated = models.BooleanField(verbose_name=_('validated'), default=False)
    deposited = models.DateTimeField(verbose_name=_('deposit date'), 
        null=True, blank=True)

    created_at = models.DateTimeField(verbose_name=_('registration date'),
        editable=False)
    created_by = models.ForeignKey(Person, null=True, editable=False,
        related_name='payment_added')
    modified_at = models.DateTimeField(verbose_name=_('modification date'),
        editable=False)
    modified_by = models.ForeignKey(Person, null=True, editable=False,
        related_name='payment_modified')

    class Meta:
        """payment meta informations"""
        verbose_name = _('payment')
        ordering = ['id']

    def save(self, *args, **kwargs):
        """custom save method to save creation timesamp"""
        if not self.created_at:
            self.created_at = datetime.datetime.now()
        self.modified_at = datetime.datetime.now()
        return super(Payment, self).save(*args, **kwargs)

    def __unicode__(self):
        """payment unicode"""
        return _('payment from') + ' ' + self.person.complete_name
