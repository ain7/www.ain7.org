# -*- coding: utf-8
#
# emploi/models.py
#
#   Copyright (C) 2007-2008 AIn7
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
from ain7.annuaire.models import Person, AIn7Member, Track
from ain7.annuaire.models import Country

ACTIONS = (
    (0, _('Create')),
    (1, _('Modify')),
    (2, _('Remove')),
)

# Activity field of an organization
class ActivityField(models.Model):

    field = models.CharField(verbose_name=_('field'), max_length=100)
    code = models.CharField(verbose_name=_('code'), max_length=100, unique=True)
    keywords = models.CharField(verbose_name=_('keywords'), max_length=100)
    label = models.CharField(verbose_name=_('label'), max_length=100)

    def __unicode__(self):
        return self.field

    def autocomplete_str(self):
        return self.label

    class Meta:
        verbose_name = _('Activity field')


# A manager for organizations
class OrganizationManager(models.Manager):

    def valid_organizations(self):
        return self.filter(is_a_proposal=False).filter(is_valid=True)

    def editable_organizations(self, ain7member):
        organizations = []
        # on ajoute les organisations dans lequel le membre a déjà travaillé
        for position in ain7member.positions.all():
            org = position.office.organization
            if org in self.valid_organizations() and \
                   not (org.id,org) in organizations:
                organizations.append((org.id,org))
        # on ajoute aussi les organisations qui n'ont aucun bureau,
        # sinon il est impossible d'y ajouter un premier bureau
        for org in self.valid_organizations():
            if (not (org.id,org) in organizations) and org.offices.count()==0:
                organizations.append((org.id,org))
        return organizations

    def adv_search_fields(self, user):
        """ Returns the list of field names that can be used as criteria
        in advanced search."""
        critsForAll  = [
            "name" , "size", "activity_field", "short_description" ,
            "long_description", ]
        critsForAdmin = [
            "is_valid" , "is_a_proposal" ,
            "last_change_at" , "last_change_by" ]
        crits = critsForAll
        if isAdmin(user):
            crits.extend(critsForAdmin)
        return crits


# Organization informations
class Organization(LoggedClass):

    ORGANIZATION_SIZE = (
                    (0, _('Micro (0)')),
                    (1, _('Small (1-9)')),
                    (2, _('Medium (10-499)')),
                    (3, _('Large (500+)')),
                    )

    name = models.CharField(verbose_name=_('name'), max_length=50)
    size = models.IntegerField(verbose_name=_('size'), choices=ORGANIZATION_SIZE, blank=True, null=True)
    activity_field = models.ForeignKey(ActivityField, verbose_name=_('Activity field'), related_name='organizations')
    short_description = models.CharField(verbose_name=_('short description'), max_length=50, blank=True, null=True)
    long_description = models.TextField(verbose_name=_('long description'), blank=True, null=True)
    is_a_proposal = models.BooleanField(verbose_name=_('is a proposal'), default=False)
    # invalid organizations are out-of-date (closed) ones
    # we keep them as they are used for old positions, etc.
    is_valid = models.BooleanField(verbose_name=_('is valid'), default=True)
    objects = OrganizationManager()

    def __unicode__(self):
        return self.name

    def autocomplete_str(self):
        return self.name

    def print_size(self):
        for size, size_label in self.ORGANIZATION_SIZE:
            if size == self.size: return size_label
        return None

    def delete(self):
        for office in self.offices.all(): office.delete()
        self.is_valid = False
        return super(Organization, self).save()
        
    def really_delete(self):
        return super(Organization, self).delete()
        
    def merge(self, org2):
        """ Replaces all references to org2 by reference to this organization.
        Then org2 is removed."""
        for propos in org2.organization_proposals.all():
            propos.original=self
            propos.save()
        for office in org2.offices.all():
            office.organization=self
            office.save()
        return org2.delete()
        
    class Meta:
        verbose_name = _('organization')


# A proposal for creating, modifying or deleting an organization
# Actually, it is only used for proposing a creation.
class OrganizationProposal(LoggedClass):

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
        act = ""
        for (actnum, actname) in ACTIONS:
            if actnum==self.action:
                act = actname
        return act + _(" the organization ") + self.modified.name

    class Meta:
        verbose_name = _('organization modification proposal')

# A manager for offices
class OfficeManager(models.Manager):

    def valid_offices(self):
        return self.filter(is_a_proposal=False).filter(is_valid=True)

    def adv_search_fields(self, user):
        """ Returns the list of field names that can be used as criteria
        in advanced search."""
        critsForAll  = [
            "organization" , "name" , "line1" , "line2" ,
            "zip_code", "city" , "country" , "phone_number" , "web_site", ]
        critsForAdmin = [
            "is_valid" , "is_a_proposal" ,
            "last_change_at" , "last_change_by" ]
        crits = critsForAll
        if isAdmin(user):
            crits.extend(critsForAdmin)
        return crits


# A organization office informations
class Office(LoggedClass):

    old_id = models.IntegerField(verbose_name='old id', blank=True, null=True, unique=True)

    organization = models.ForeignKey(Organization, verbose_name=_('organization'), related_name='offices')

    name = models.CharField(verbose_name=_('name'), max_length=50)

    line1 = models.CharField(verbose_name=_('line1'), max_length=50, blank=True, null=True)
    line2 = models.CharField(verbose_name=_('line2'), max_length=100, blank=True, null=True)
    zip_code = models.CharField(verbose_name=_('zip code'), max_length=20, blank=True, null=True)
    city = models.CharField(verbose_name=_('city'), max_length=50, blank=True, null=True)
    country = models.ForeignKey(Country, verbose_name=_('country'), blank=True, null=True)

    phone_number = models.CharField(verbose_name=_('phone number'), max_length=20, blank=True, null=True)
    web_site = models.CharField(verbose_name=_('web site'), max_length=100, blank=True, null=True)

    # invalid offices are out-of-date (closed) ones
    # we keep them as they are used for old positions, etc.
    is_valid = models.BooleanField(
        verbose_name=_('is valid'), default=True)
    is_a_proposal = models.BooleanField(
        verbose_name=_('is a proposal'), default=False)
    objects = OfficeManager()

    def __unicode__(self):
        return self.name

    def autocomplete_str(self):
        return self.organization.name + " - " + self.name

    def save(self):
        if self.web_site and \
           (not (self.web_site.startswith("http://") or \
                 (self.web_site.startswith("https://")))):
            self.web_site = "http://" + self.web_site
        return super(Office, self).save()

    def delete(self):
        self.is_valid = False
        return super(Office, self).save()
        
    def really_delete(self):
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
        for joboffer in office2.job_offers.all():
            joboffer.office = self
            joboffer.save() 
        return office2.delete()

    def current_n7_employees(self):
        liste_N7_current = []
        for position in self.positions.all():
            ain7member = position.ain7member
            today = datetime.datetime.now().date()
            if (not position.end_date) or position.end_date >= today:
                liste_N7_current.append(ain7member)
        return liste_N7_current

    def past_n7_employees(self):
        liste_N7_past = []
        liste_N7_current = self.current_n7_employees()
        for position in self.positions.all():
            ain7member = position.ain7member
            today = datetime.datetime.now().date()
            # je veille à ce qu'une personne actuellement dans cette société
            # n'apparaisse pas également dans la liste des précédents employés
            if not ain7member in liste_N7_current:
                liste_N7_past.append(ain7member)
        return liste_N7_past

    class Meta:
        verbose_name = _('office')
        verbose_name_plural = _('offices')


# A proposal for creating, modifying or deleting an office
# Actually, it is only used for proposing a creation.
class OfficeProposal(LoggedClass):

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
        act = ""
        for (actnum, actname) in ACTIONS:
            if actnum==self.action:
                act = actname
        return act + _(" the office ") + self.modified.name

    class Meta:
        verbose_name = _('office modification proposal')


# A position occupied by a person.
class Position(LoggedClass):

    office = models.ForeignKey(Office, verbose_name=_('office'), related_name='positions')
    fonction = models.CharField(verbose_name=_('fonction'), max_length=50)
    service = models.CharField(verbose_name=_('service'), max_length=50, blank=True, null=True)
    phone_number = models.CharField(verbose_name=_('phone number'), max_length=20, blank=True, null=True)
    email = models.EmailField(verbose_name=_('email'), blank=True, null=True)
    start_date = models.DateField(verbose_name=_('start date'), blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)
    is_regie = models.BooleanField(verbose_name=_('regie outside'), default=False)

    ain7member = models.ForeignKey(AIn7Member, related_name='positions')
    description = models.TextField(verbose_name=_('description'), blank=True, null=True)

    def __unicode__(self):
        description  = self.fonction + " " + _("for") + " " + unicode(self.office)
        description += " (" + unicode(self.office.organization) +")"
        return description

    class Meta:
        verbose_name = _('position')
        ordering = ['-start_date']

# An education item in the CV of a person.
class EducationItem(LoggedClass):

    school = models.CharField(verbose_name=_('school'), max_length=150)
    diploma = models.CharField(verbose_name=_('diploma'), max_length=150, blank=True, null=True)
    details = models.TextField(verbose_name=_('description'), blank=True, null=True)
    start_date = models.DateField(verbose_name=_('start date'))
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)
    ain7member = models.ForeignKey(AIn7Member, related_name='education')

    def __unicode__(self):
        return self.school

    class Meta:
        verbose_name = _('Education item')
        ordering = ['-start_date']

# A leisure item in the CV of a person.
# For instance: title="Culture" detail="Japanim"
#               title="Sport" detail="Judo, Pastis, Pétanque"
class LeisureItem(LoggedClass):

    title = models.CharField(verbose_name=_('Title'), max_length=50)
    detail = models.TextField(verbose_name=_('Detail'), blank=True, null=True)
    ain7member = models.ForeignKey(AIn7Member, related_name='leisure')

    def __unicode__(self):
        return self.title
        
    class Meta:
        verbose_name = _('Leisure item')
        ordering = ['title']

# An publication item in the CV of a person.
class PublicationItem(LoggedClass):

    title = models.CharField(verbose_name=_('Title'), max_length=50)
    details = models.TextField(verbose_name=_('Detail'), blank=True, null=True)
    date = models.DateField()
    ain7member = models.ForeignKey(AIn7Member, related_name='publication')

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Publication and patent')

class JobOffer(LoggedClass):

    JOB_TYPES = (
        (0,'CDI'),
        (1,'CDD'),
        (2,'Stage'),
    )

    reference = models.CharField(verbose_name=_('Reference'), max_length=50, blank=True, null=True)
    title = models.CharField(verbose_name=_('Title'), max_length=100)
    description = models.TextField(verbose_name=_('Description'), blank=True, null=True)
    experience = models.CharField(verbose_name=_('Experience'), max_length=50, blank=True, null=True)
    contract_type = models.IntegerField(verbose_name=_('Contract type'), choices=JOB_TYPES, blank=True, null=True)
    is_opened = models.BooleanField(verbose_name=_('Job offer is opened'), default=False)
    office = models.ForeignKey(Office, related_name='job_offers',
                               blank=True, null=True)
    contact_name = models.CharField(verbose_name=_('Contact name'), max_length=80, blank=True, null=True)
    contact_email = models.EmailField(verbose_name=_('email'), blank=True, null=True)
    track = models.ManyToManyField(Track, verbose_name=_('Track'), related_name='jobs', blank=True, null=True)
    nb_views = models.IntegerField(verbose_name=_('Number of views'), default=0, editable=False)

    def __unicode__(self):
        return self.reference + " " + self.title + " ("+ unicode(self.office) + ")"

