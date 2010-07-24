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

from ain7.annuaire.models import Person, AIn7Member
from ain7.annuaire.models import Country
from ain7.utils import LoggedClass, isAdmin


ACTIONS = (
    (0, _('Create')),
    (1, _('Modify')),
    (2, _('Remove')),
)

class ActivityField(models.Model):
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


class OrganizationManager(models.Manager):
    """ A manager for organizations"""

    def valid_organizations(self):
        """valid organizations"""
        return self.filter(is_a_proposal=False).filter(is_valid=True)

    def editable_organizations(self, ain7member):
        """edit organizations"""
        organizations = []
        # on ajoute les organisations dans lequel le membre a déjà travaillé
        for position in ain7member.positions.all():
            org = position.office.organization
            if org in self.valid_organizations() and \
                   not (org.id,org) in organizations:
                organizations.append((org.id, org))
        # on ajoute aussi les organisations qui n'ont aucun bureau,
        # sinon il est impossible d'y ajouter un premier bureau
        for org in self.valid_organizations():
            if (not (org.id, org) in organizations) and org.offices.count()==0:
                organizations.append((org.id, org))
        return organizations

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
        if isAdmin(user):
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
    activity_field = models.ForeignKey(ActivityField,
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
        for office in self.offices.all(): office.delete()
        self.is_valid = False
        return super(Organization, self).save()
        
    def really_delete(self):
        """really delete organization"""
        return super(Organization, self).delete()
        
    def merge(self, org2):
        """ Replaces all references to org2 by reference to this organization.
        Then org2 is removed."""
        for propos in org2.organization_proposals.all():
            propos.original = self
            propos.save()
        for office in org2.offices.all():
            office.organization = self
            office.save()
        return org2.delete()
        
    class Meta:
        """organization meta"""
        verbose_name = _('organization')


class OrganizationProposal(LoggedClass):
    """
    A proposal for creating, modifying or deleting an organization
    Actually, it is only used for proposing a creation.
    """

    author = models.ForeignKey(Person, verbose_name=_('author'),
                               related_name='organization_proposals')
    original = models.ForeignKey(Organization,
                                 verbose_name=_('original organization'),
                                 related_name='organization_proposals',
                                 blank=True, null=True)
    modified = models.ForeignKey(Organization,
                                 verbose_name=_('modified organization'),
                                 blank=True, null=True)
    action = models.IntegerField(verbose_name=_('action'), choices=ACTIONS,
                                 blank=True, null=True)

    def __unicode__(self):
        """organization proposal unicode"""
        act = ""
        for (actnum, actname) in ACTIONS:
            if actnum == self.action:
                act = actname
        return act + ' ' + _('the organization') + ' ' + self.modified.name

    class Meta:
        """organization proposal meta"""
        verbose_name = _('organization modification proposal')

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
        if isAdmin(user):
            crits.extend(crits_for_admin)
        return crits

class Office(LoggedClass):
    """ A organization office informations """

    # For potential backward compatibility
    old_id = models.IntegerField(verbose_name='old id', blank=True,
        null=True, unique=True)

    organization = models.ForeignKey(Organization, 
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
    country = models.ForeignKey(Country, verbose_name=_('country'),
        blank=True, null=True)
    phone_number = models.CharField(verbose_name=_('phone number'),
        max_length=20, blank=True, null=True)
    web_site = models.CharField(verbose_name=_('web site'), max_length=100,
        blank=True, null=True)

    # invalid offices are out-of-date (closed) ones
    # we keep them as they are used for old positions, etc.
    is_valid = models.BooleanField(verbose_name=_('is valid'), default=True)
    is_a_proposal = models.BooleanField(verbose_name=_('is a proposal'), 
        default=False)
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
        
    def really_delete(self):
        """office really delete"""
        return super(Office, self).delete()
        
    def merge(self, office2):
        """ Replaces all references to office2 by reference to
        this organization. Then office2 is removed."""
        for propos in office2.office_proposals.all():
            propos.original = self
            propos.save()
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
        return JobOffer.objects.filter(office=self, checked_by_secretariat=True)

    class Meta:
        """office meta"""
        verbose_name = _('office')
        verbose_name_plural = _('offices')


class OfficeProposal(LoggedClass):
    """
    A proposal for creating, modifying or deleting an office
    Actually, it is only used for proposing a creation.
    """

    author = models.ForeignKey(Person, verbose_name=_('author'),
                               related_name='office_proposals')
    original = models.ForeignKey(Office, verbose_name=_('original office'),
                                 related_name='office_proposals',
                                 null=True)
    modified = models.ForeignKey(Office, verbose_name=_('modified office'),
                                 blank=True, null=True)
    action = models.IntegerField(verbose_name=_('action'), choices=ACTIONS,
                                 blank=True, null=True)

    def __unicode__(self):
        """office proposal unicode"""
        act = ""
        for (actnum, actname) in ACTIONS:
            if actnum == self.action:
                act = actname
        return act +' ' +  _('the office') + ' ' + self.modified.name

    class Meta:
        """office proposal meta"""
        verbose_name = _('office modification proposal')


class Position(LoggedClass):
    """
    A position occupied by a person.
    """

    ain7member = models.ForeignKey(AIn7Member, related_name='positions')
    office = models.ForeignKey(Office, verbose_name=_('office'),
        related_name='positions')

    fonction = models.CharField(verbose_name=_('fonction'), max_length=80,
        blank=True, null=True)
    service = models.CharField(verbose_name=_('service'), max_length=80,
        blank=True, null=True)
    phone_number = models.CharField(verbose_name=_('phone'),
        max_length=20, blank=True, null=True)
    email = models.EmailField(verbose_name=_('email'), blank=True, null=True)
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

    ain7member = models.ForeignKey(AIn7Member, related_name='education')

    school = models.CharField(verbose_name=_('school'), max_length=150)
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

class DiplomaItem(LoggedClass):
    """A diploma item in the CV of a person."""

    diploma = models.CharField(verbose_name=_('diploma'), max_length=150)
    ain7member = models.ForeignKey(AIn7Member, related_name='diploma')

    def __unicode__(self):
        """diploma item unicode"""
        return self.diploma

    class Meta:
        """diploma item meta"""
        verbose_name = _('Diploma item')

class LeisureItem(LoggedClass):
    """
    A leisure item in the CV of a person.
    For instance: title="Culture" detail="Japanim"
               title="Sport" detail="Judo, Pastis, Pétanque"
    """

    title = models.CharField(verbose_name=_('Title'), max_length=50)
    detail = models.TextField(verbose_name=_('Detail'), blank=True, null=True)
    ain7member = models.ForeignKey(AIn7Member, related_name='leisure')

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
    ain7member = models.ForeignKey(AIn7Member, related_name='publication')

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
    office = models.ForeignKey(Office, blank=True, null=True)
    contact_name = models.CharField(verbose_name=_('Contact name'),
        max_length=80, blank=True, null=True)
    contact_email = models.EmailField(verbose_name=_('email'), blank=True,
        null=True)
    activity_field = models.ForeignKey(ActivityField,
        verbose_name=_('Activity field'), related_name='jobs',
        blank=True, null=True)
    checked_by_secretariat = models.BooleanField(
        verbose_name=_('checked by secretariat'), default=False)
    nb_views = models.IntegerField(verbose_name=_('Number of views'),
        default=0, editable=False)
    obsolete = models.BooleanField(verbose_name=_('Job offer is obsolete'),
        default=False)

    created_at = models.DateTimeField(editable=False)
    created_by = models.ForeignKey(Person, verbose_name=_('author'),
        related_name='job_offers_created', null=True)

    modified_at = models.DateTimeField(editable=False)
    modified_by = models.ForeignKey(Person, verbose_name=_('author'),
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

class JobOfferView(models.Model):
    """job offer view"""

    job_offer = models.ForeignKey(JobOffer)
    person = models.ForeignKey(Person)
    timestamp = models.DateTimeField()

    def save(self, *args, **kwargs):
        """custom save method to save consultation timestamp"""
        if not self.timestamp:
            self.timestamp = datetime.datetime.now()
        return super(JobOfferView, self).save(*args, **kwargs)

    def __unicode__(self):
        """job offer view unicode"""
        return self.job_offer + _('viewed by') + self.person + _('at') + self.timestamp

