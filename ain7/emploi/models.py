# -*- coding: utf-8
"""
 ain7/emploi/models.py
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

from ain7.utils import LoggedClass, isAdmin


class Position(LoggedClass):
    """
    A position occupied by a person.
    """

    ain7member = models.ForeignKey('annuaire.AIn7Member', 
        related_name='positions')
    office = models.ForeignKey('organizations.Office', verbose_name=_('office'),
        related_name='positions')

    fonction = models.CharField(verbose_name=_('fonction'), max_length=80,
        blank=True, null=True)
    service = models.CharField(verbose_name=_('service'), max_length=80,
        blank=True, null=True)
    phone_number = models.CharField(verbose_name=_('phone'),
        max_length=20, blank=True, null=True)
    is_regie = models.BooleanField(verbose_name=_('regie outside'),
        default=False)
    begin = models.IntegerField(verbose_name=_('startyear'),
        blank=True, null=True)
    end = models.IntegerField(verbose_name=_('end year'), blank=True,
        null=True)

    description = models.TextField(verbose_name=_('description'), blank=True,
        null=True)

    def __unicode__(self):
        """position unicode"""
        description = ''
        if self.fonction:
            description += self.fonction
        description += " " + unicode(self.office)
        description += " (" + unicode(self.office.organization) +")"
        return description

    class Meta:
        """position meta"""
        verbose_name = _('position')
        ordering = ['-begin']

class EducationItem(LoggedClass):
    """ An education item in the CV of a person."""

    ain7member = models.ForeignKey('annuaire.AIn7Member',
        related_name='education')

    school = models.CharField(verbose_name=_('school'), max_length=150,
        blank=True, null=True)
    diploma = models.CharField(verbose_name=_('diploma'), max_length=150,
        blank=True, null=True)
    details = models.TextField(verbose_name=_('description'), blank=True,
        null=True)
    begin = models.IntegerField(verbose_name=_('start year'),
        blank=True, null=True)
    end = models.IntegerField(verbose_name=_('end year'), blank=True,
        null=True)

    def __unicode__(self):
        """education item unicode"""
        return self.school

    class Meta:
        """education item meta"""
        verbose_name = _('Education item')
        ordering = ['-begin']

class LeisureItem(LoggedClass):
    """
    A leisure item in the CV of a person.
    For instance: title="Culture" detail="Japanim"
               title="Sport" detail="Judo, Pastis, Pétanque"
    """

    title = models.CharField(verbose_name=_('Title'), max_length=50)
    detail = models.TextField(verbose_name=_('Detail'), blank=True, null=True)
    ain7member = models.ForeignKey('annuaire.AIn7Member', 
        related_name='leisure')

    def __unicode__(self):
        """leisure item unicode"""
        return self.title
        
    class Meta:
        """leisure item meta"""
        verbose_name = _('Leisure item')
        ordering = ['title']

class PublicationItem(LoggedClass):
    """An publication item in the CV of a person."""

    title = models.CharField(verbose_name=_('Title'), max_length=50)
    details = models.TextField(verbose_name=_('Detail'), blank=True, null=True)
    date = models.DateField()
    ain7member = models.ForeignKey('annuaire.AIn7Member', 
        related_name='publication')

    def __unicode__(self):
        """publication item unicode"""
        return self.title

    class Meta:
        """publication item meta"""
        verbose_name = _('Publication and patent')

class JobOffer(LoggedClass):
    """job offer"""

    JOB_TYPES = (
        (0,'CDI'),
        (1,'CDD'),
        (2,'Stage'),
    )

    reference = models.CharField(verbose_name=_('Reference'), max_length=50,
        blank=True, null=True)
    title = models.CharField(verbose_name=_('Title'), max_length=200)
    description = models.TextField(verbose_name=_('Description'), blank=True,
        null=True)
    experience = models.CharField(verbose_name=_('Experience'), max_length=50,
        blank=True, null=True)
    contract_type = models.IntegerField(verbose_name=_('Contract type'),
        choices=JOB_TYPES, blank=True, null=True)
    office = models.ForeignKey('organizations.Office', blank=True, null=True)
    contact_name = models.CharField(verbose_name=_('Contact name'),
        max_length=80, blank=True, null=True)
    contact_email = models.EmailField(verbose_name=_('email'), blank=True,
        null=True)
    activity_field = models.ForeignKey('organizations.OrganizationActivityField',
        verbose_name=_('Activity field'), related_name='jobs',
        blank=True, null=True)
    checked_by_secretariat = models.BooleanField(
        verbose_name=_('checked by secretariat'), default=False)
    obsolete = models.BooleanField(verbose_name=_('Job offer is obsolete'),
        default=False)

    created_at = models.DateTimeField(editable=False)
    created_by = models.ForeignKey('annuaire.Person', verbose_name=_('author'),
        related_name='job_offers_created', null=True)

    modified_at = models.DateTimeField(editable=False)
    modified_by = models.ForeignKey('annuaire.Person', verbose_name=_('author'),
        related_name='job_offers_modified', null=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.now()
        self.modified_at = datetime.datetime.now()
        return super(JobOffer, self).save(*args, **kwargs)

    def __unicode__(self):
        """job offer unicode"""
        return self.reference + " " + self.title + " ("+\
             unicode(self.office) + ")"

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

