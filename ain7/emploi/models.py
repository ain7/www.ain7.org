# -*- coding: utf-8
"""
 ain7/emploi/models.py
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

import datetime

from django.db import models
from django.utils.translation import ugettext as _

from ain7.utils import LoggedClass


class JobOffer(LoggedClass):
    """job offer"""

    JOB_TYPES = (
        (0, 'CDI'),
        (1, 'CDD'),
        (2, 'Stage'),
    )

    reference = models.CharField(
        verbose_name=_('Reference'), max_length=50, blank=True, null=True
    )
    title = models.CharField(verbose_name=_('Title'), max_length=200)
    description = models.TextField(
        verbose_name=_('Description'), blank=True, null=True
    )
    experience = models.CharField(
        verbose_name=_('Experience'), max_length=50, blank=True, null=True
    )
    contract_type = models.IntegerField(
        verbose_name=_('Contract type'), choices=JOB_TYPES,
    )
    office = models.ForeignKey('organizations.Office')
    contact_name = models.CharField(
        verbose_name=_('Contact name'), max_length=80, blank=True, null=True
    )
    contact_email = models.EmailField(
        verbose_name=_('email'), blank=True, null=True
    )
    activity_field = models.ForeignKey(
        'organizations.OrganizationActivityField',
        verbose_name=_('Activity field'), related_name='jobs',
        blank=True, null=True
    )
    checked_by_secretariat = models.BooleanField(
        verbose_name=_('checked by secretariat'), default=False
    )
    obsolete = models.BooleanField(
        verbose_name=_('Job offer is obsolete'), default=False
    )

    created_at = models.DateTimeField(editable=False)
    created_by = models.ForeignKey(
        'annuaire.Person', verbose_name=_('author'),
        related_name='job_offers_created', editable=False, null=True
    )

    modified_at = models.DateTimeField(editable=False)
    modified_by = models.ForeignKey(
        'annuaire.Person', verbose_name=_('author'),
        related_name='job_offers_modified', editable=False, null=True
    )

    class Meta:
        """job offer meta"""
        verbose_name = _('Job Offer')
        ordering = ['-id']

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.now()
        self.modified_at = datetime.datetime.now()
        return super(JobOffer, self).save(*args, **kwargs)

    def __unicode__(self):
        """job offer unicode"""
        return (
            self.reference + " " + self.title + " (" +
            unicode(self.office) + ")"
        )

    def mark_obsolete(self):
        """mark a job offer as obsolote"""
        self.obsolete = True
        self.save()


class JobOfferView(models.Model):
    """job offer view"""

    job_offer = models.ForeignKey('emploi.JobOffer')
    person = models.ForeignKey('annuaire.Person')
    timestamp = models.DateTimeField()

    def save(self, *args, **kwargs):
        """custom save method to save consultation timestamp"""
        if not self.timestamp:
            self.timestamp = datetime.datetime.now()
        return super(JobOfferView, self).save(*args, **kwargs)

    def __unicode__(self):
        """job offer view unicode"""
        return self.job_offer + _('viewed by') + self.person + _('at') + \
            self.timestamp
