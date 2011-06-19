# -*- coding: utf-8
"""
 ain7/organizations/models.py
"""
#
#   Copyright © 2007-2011 AIn7 Devel Team
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

from ain7.utils import LoggedClass, is_admin


class OrganizationSize(models.Model):

    size = models.CharField(verbose_name=_('size'), max_length=20)
    description = models.CharField(verbose_name=_('description'), 
        max_length=100)

class OrganizationActivityField(models.Model):
    """ Activity field of an organization"""

    field = models.CharField(verbose_name=_('field'), max_length=100)
    code = models.CharField(verbose_name=_('code'), max_length=100, unique=True)
    keywords = models.CharField(verbose_name=_('keywords'), max_length=100)
    label = models.CharField(verbose_name=_('label'), max_length=100)

    def __unicode__(self):
        """activity field unicode"""
        return self.field

    class Meta:
        """activity field meta"""
        verbose_name = _('Activity field')
        ordering = ['label']

class OrganizationManager(models.Manager):
    """ A manager for organizations"""

    def valid_organizations(self):
        """valid organizations"""
        return self.filter(is_a_proposal=False).filter(is_valid=True)

    def adv_search_fields(self, user):
        """ Returns the list of field names that can be used as criteria
        in advanced search."""
        crits_for_all  = [
            "name" , "size", "activity_field", "short_description" ,
            "long_description", ]
        crits_for_admin = [
            "is_valid" , "is_a_proposal" ,
            "last_change_at" , "last_change_by" ]
        crits = crits_for_all
        if is_admin(user):
            crits.extend(crits_for_admin)
        return crits


class Organization(LoggedClass):
    """ Organization informations"""

    ORGANIZATION_SIZE = (
                    (0, _('Micro (0)')),
                    (1, _('Small (1-9)')),
                    (2, _('Medium (10-499)')),
                    (3, _('Large (500+)')),
                    (10, _('Unknown')),
                    )

    name = models.CharField(verbose_name=_('name'), max_length=100)
    size = models.IntegerField(verbose_name=_('size'),
        choices=ORGANIZATION_SIZE, blank=True, null=True)
    # TODO: do not allow null=True, but mandatory for import right now
    activity_field = models.ForeignKey(
         'organizations.OrganizationActivityField',
         verbose_name=_('Activity field'), related_name='organizations',
         null=True, blank=True)
    short_description = models.CharField(verbose_name=_('short description'),
         max_length=50, blank=True, null=True)
    long_description = models.TextField(verbose_name=_('long description'),
         blank=True, null=True)
    employment_agency = models.BooleanField(verbose_name=_('employment agency'),
         default=False)
    is_a_proposal = models.BooleanField(verbose_name=_('is a proposal'),
         default=False)
    # invalid organizations are out-of-date (closed) ones
    # we keep them as they are used for old positions, etc.
    is_valid = models.BooleanField(verbose_name=_('is valid'),
         default=True)
    objects = OrganizationManager()

    modification_of = models.ForeignKey('organizations.Organization',
        null=True, blank=True)
    modification_date = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        """organization unicode"""
        return self.name

    def print_size(self):
        """print organization size"""
        for size, size_label in self.ORGANIZATION_SIZE:
            if size == self.size: return size_label
        return None

    def delete(self):
        """delete organization"""
        for office in self.offices.all():
            office.delete()
        self.is_valid = False
        return super(Organization, self).save()

    def purge(self):
        """purge organization"""
        return super(Organization, self).delete()

    def merge(self, org2):
        """ Replaces all references to org2 by reference to this organization.
        Then org2 is removed."""
        for office in org2.offices.all():
            office.organization = self
            office.save()
        return org2.delete()

    class Meta:
        """organization meta"""
        verbose_name = _('organization')


class OfficeManager(models.Manager):
    """ A manager for offices """

    def valid_offices(self):
        """office manager valid offices"""
        return self.filter(is_a_proposal=False).filter(is_valid=True)

    def adv_search_fields(self, user):
        """ Returns the list of field names that can be used as criteria
        in advanced search."""
        crits_for_all  = [
            "organization" , "name" , "line1" , "line2" ,
            "zip_code", "city" , "country" , "phone_number" , "web_site", ]
        crits_for_admin = [
            "is_valid" , "is_a_proposal" ,
            "last_change_at" , "last_change_by" ]
        crits = crits_for_all
        if is_admin(user):
            crits.extend(crits_for_admin)
        return crits

class Office(LoggedClass):
    """ A organization office informations """

    # For potential backward compatibility
    old_id = models.IntegerField(verbose_name='old id', blank=True,
        null=True, unique=True)

    organization = models.ForeignKey('organizations.Organization',
        verbose_name=_('organization'), related_name='offices')

    name = models.CharField(verbose_name=_('name'), max_length=100,
        blank=True, null=True)

    line1 = models.CharField(verbose_name=_('line1'), max_length=50,
        blank=True, null=True)
    line2 = models.CharField(verbose_name=_('line2'), max_length=100,
        blank=True, null=True)
    zip_code = models.CharField(verbose_name=_('zip code'), max_length=20,
        blank=True, null=True)
    city = models.CharField(verbose_name=_('city'), max_length=50,
        blank=True, null=True)
    country = models.ForeignKey('annuaire.Country', verbose_name=_('country'),
        blank=True, null=True)
    phone_number = models.CharField(verbose_name=_('phone number'),
        max_length=20, blank=True, null=True)
    fax_number = models.CharField(verbose_name=_('fax number'),
        max_length=20, blank=True, null=True)
    web_site = models.CharField(verbose_name=_('web site'), max_length=100,
        blank=True, null=True)

    # invalid offices are out-of-date (closed) ones
    # we keep them as they are used for old positions, etc.
    is_valid = models.BooleanField(verbose_name=_('is valid'), default=True)
    is_a_proposal = models.BooleanField(verbose_name=_('is a proposal'),
        default=False)


    modification_of = models.ForeignKey('organizations.Office',
        null=True, blank=True)
    modification_date = models.DateTimeField(null=True, blank=True)

    objects = OfficeManager()

    def __unicode__(self):
        """office unicode"""
        if self.organization.name == self.name:
            return ''
        else:
            return self.name

    def save(self):
        """office save"""
        if self.web_site and \
           (not (self.web_site.startswith("http://") or \
                 (self.web_site.startswith("https://")))):
            self.web_site = "http://" + self.web_site
        return super(Office, self).save()

    def delete(self):
        """office delete"""
        self.is_valid = False
        return super(Office, self).save()

    def purge(self):
        """office purge"""
        return super(Office, self).delete()

    def merge(self, office2):
        """ Replaces all references to office2 by reference to
        this organization. Then office2 is removed."""

        from ain7.emploi.models import JobOffer

        for position in office2.positions.all():
            position.office = self
            position.save()
        for joboffer in JobOffer.objects.filter(office=office2):
            joboffer.office = self
            joboffer.save()
        return office2.delete()

    def current_n7_employees(self):
        """current N7 employees"""
        liste_n7_current = []
        for position in self.positions.all():
            ain7member = position.ain7member
            today = datetime.datetime.now().date()
            if (not position.end) or position.end >= today.year:
                liste_n7_current.append(ain7member)
        return liste_n7_current

    def past_n7_employees(self):
        """past n7 employees"""
        liste_n7_past = []
        liste_n7_current = self.current_n7_employees()
        for position in self.positions.all():
            ain7member = position.ain7member
            # je veille à ce qu'une personne actuellement dans cette société
            # n'apparaisse pas également dans la liste des précédents
            # employés
            if not ain7member in liste_n7_current:
                liste_n7_past.append(ain7member)
        return liste_n7_past

    def job_offers(self):
        """job offers"""

        from ain7.emploi.models import JobOffer

        return JobOffer.objects.filter(office=self, checked_by_secretariat=True)

    class Meta:
        """office meta"""
        verbose_name = _('office')
        verbose_name_plural = _('offices')

