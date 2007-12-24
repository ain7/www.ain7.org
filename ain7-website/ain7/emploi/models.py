# -*- coding: utf-8
#
# emploi/models.py
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

import datetime

from django.db import models

from ain7.annuaire.models import Person, AIn7Member, Track
from ain7.annuaire.models import Country

# ???
class CompanyField(models.Model):

    field = models.CharField(verbose_name=_('field'), maxlength=100)

    def __str__(self):
        return self.field

    class Admin:
        pass

    class Meta:
        verbose_name = _('field')

# Company informations
class Company(models.Model):

    COMPANY_SIZE = (
                    (0, _('Micro (0)')),
                    (1, _('Small (1-9)')),
                    (2, _('Medium (10-499)')),
                    (3, _('Large (500+)')),
                    )

    name = models.CharField(verbose_name=_('name'), maxlength=50, core=True)
    size = models.IntegerField(verbose_name=_('size'), choices=COMPANY_SIZE, blank=True, null=True)
    field = models.ForeignKey(CompanyField, verbose_name=_('field'), related_name='companies')

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)

    def __str__(self):
        return self.name

    def save(self):
        self.modification_date = datetime.datetime.today()
        return super(Company, self).save()

    class Meta:
        verbose_name = _('company')

    class Admin:
        pass

# A company office informations
class Office(models.Model):

    company = models.ForeignKey(Company, verbose_name=_('company'), related_name='offices', edit_inline=models.STACKED)

    name = models.CharField(verbose_name=_('name'), maxlength=50, core=True)

    number = models.CharField(verbose_name=_('number'), maxlength=50, blank=True, null=True)
    street = models.CharField(verbose_name=_('street'), maxlength=100, blank=True, null=True)
    zip_code = models.CharField(verbose_name=_('zip code'), maxlength=20, blank=True, null=True)
    city = models.CharField(verbose_name=_('city'), maxlength=50, blank=True, null=True)
    country = models.ForeignKey(Country, verbose_name=_('country'), blank=True, null=True)

    phone_number = models.CharField(verbose_name=_('phone number'), maxlength=20, blank=True, null=True)
    web_site = models.CharField(verbose_name=_('web site'), maxlength=100, blank=True, null=True)

    is_valid = models.BooleanField(verbose_name=_('is valid'), default=True)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)

    def __str__(self):
        return self.name

    def save(self):
        self.modification_date = datetime.datetime.today()
        return super(Office, self).save()

    class Admin:
        pass

    class Meta:
        verbose_name = _('office')
        verbose_name_plural = _('offices')

# A position occupied by a person.
class Position(models.Model):

    fonction = models.CharField(verbose_name=_('fonction'), maxlength=50, core=True)
    service = models.CharField(verbose_name=_('service'), maxlength=50, blank=True, null=True)
    description = models.TextField(verbose_name=_('description'), blank=True, null=True)
    phone_number = models.CharField(verbose_name=_('phone number'), maxlength=20, blank=True, null=True)
    email = models.EmailField(verbose_name=_('email'), blank=True, null=True)
    start_date = models.DateField(verbose_name=_('start date'), core=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)
    is_regie = models.BooleanField(verbose_name=_('regie'), default=False)

    office = models.ForeignKey(Office, verbose_name=_('office'), related_name='positions')
    ain7member = models.ForeignKey(AIn7Member, related_name='positions', edit_inline=models.STACKED, num_in_admin=1)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)

    def __str__(self):
        description  = self.fonction + " " + _("for") + " " + str(self.office)
        description += " (" + str(self.office.company) +")"
        return description

    def save(self):
        self.modification_date = datetime.datetime.today()
        return super(Position, self).save()

    class Meta:
        verbose_name = _('position')
        ordering = ['-start_date']

# An education item in the CV of a person.
class EducationItem(models.Model):

    school = models.CharField(verbose_name=_('school'), maxlength=150, core=True)
    diploma = models.CharField(verbose_name=_('diploma'), maxlength=150, blank=True, null=True)
    details = models.TextField(verbose_name=_('description'), blank=True, null=True)
    start_date = models.DateField(verbose_name=_('start date'), core=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)
    ain7member = models.ForeignKey(AIn7Member, related_name='education', edit_inline=models.STACKED, num_in_admin=1)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)

    def save(self):
        self.modification_date = datetime.datetime.today()
        return super(EducationItem, self).save()

    class Meta:
        verbose_name = _('Education item')
        ordering = ['-start_date']

# A leisure item in the CV of a person.
# For instance: title="Culture" detail="Japanim"
#               title="Sport" detail="Judo, Pastis, Pétanque"
class LeisureItem(models.Model):

    title = models.CharField(verbose_name=_('Title'), maxlength=50, core=True)
    detail = models.TextField(verbose_name=_('Detail'), blank=True, null=True)
    ain7member = models.ForeignKey(AIn7Member, related_name='leisure', edit_inline=models.STACKED, num_in_admin=1)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)

    def save(self):
        self.modification_date = datetime.datetime.today()
        return super(LeisureItem, self).save()

    class Meta:
        verbose_name = _('Leisure item')
        ordering = ['title']

# An publication item in the CV of a person.
class PublicationItem(models.Model):

    title = models.CharField(verbose_name=_('Title'), maxlength=50, core=True)
    details = models.TextField(verbose_name=_('Detail'), blank=True, null=True)
    date = models.DateField()
    ain7member = models.ForeignKey(AIn7Member, related_name='publication', edit_inline=models.STACKED, num_in_admin=1)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)

    def save(self):
        self.modification_date = datetime.datetime.today()
        return super(PublicationItem, self).save()

    class Meta:
        verbose_name = _('Publication item')

    class Admin:
        pass

class JobOffer(models.Model):

    JOB_TYPES = (
        (0,'CDI'),
        (1,'CDD'),
        (2,'Stage'),
    )

    reference = models.CharField(verbose_name=_('Reference'), maxlength=50, blank=True, null=True)
    title = models.CharField(verbose_name=_('Title'), maxlength=100, core=True)
    description = models.TextField(verbose_name=_('Description'), blank=True, null=True)
    experience = models.CharField(verbose_name=_('Experience'), maxlength=50, blank=True, null=True)
    contract_type = models.IntegerField(verbose_name=_('Contract type'), choices=JOB_TYPES, blank=True, null=True)
    is_opened = models.BooleanField(verbose_name=_('Job offer is opened'), default=False)
    office = models.ForeignKey(Office, blank=True, null=True)
    contact = models.ForeignKey(Person, blank=True, null=True)
    track = models.ManyToManyField(Track, verbose_name=_('Track'), related_name='jobs', blank=True, null=True, filter_interface=models.HORIZONTAL)
    nb_views = models.IntegerField(verbose_name=_('Number of views'), default=0, editable=False)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)

    def __str__(self):
        return self.reference + " " + self.title + " ("+ str(self.office) + ")"

    def save(self):
        self.modification_date = datetime.datetime.today()
        return super(JobOffer, self).save()

    class Admin:
        pass

