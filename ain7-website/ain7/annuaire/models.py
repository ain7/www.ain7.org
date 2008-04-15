# -*- coding: utf-8
#
# annuaire/models.py
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
import smtplib
import time

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from ain7.utils import isAdmin

# Country (used for adresses)
class Country(models.Model):

    name = models.CharField(verbose_name=_('name'), max_length=50)
    nationality = models.CharField(verbose_name=_('nationality'), max_length=50)

    def __unicode__(self):
        return self.name

    class Admin:
        pass

    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('country')

# Indicates the current status of a person: Student, Ingeneer
class PersonType(models.Model):

    type = models.CharField(verbose_name=_('type'), max_length=50)

    def __unicode__(self):
        return self.type

    class Admin:
        pass

    class Meta:
        verbose_name = _('person type')
        verbose_name_plural = _('person types')

# Indicates the current relation with the association: actif member or ?
class MemberType(models.Model):

    type = models.CharField(verbose_name=_('type'), max_length=50)

    def __unicode__(self):
        return self.type

    class Admin:
        pass

    class Meta:
        verbose_name = _('member type')

# Indicates the current main activity of the person: student, active retired, ...
class Activity(models.Model):

    activity = models.CharField(verbose_name=_('activity'), max_length=50)

    def __unicode__(self):
        return self.activity

    class Admin:
        pass

    class Meta:
        verbose_name = _('activity')

# Indicates the current marital status of the person: single, married, ...
class MaritalStatus(models.Model):

    status = models.CharField(verbose_name=_('status'), max_length=50)

    def __unicode__(self):
        return self.status

    class Admin:
        pass

    class Meta:
        verbose_name = _('marital status')

# Diploma received
class Diploma(models.Model):

    diploma = models.CharField(verbose_name=_('diploma'), max_length=100, core=True)
    initials = models.CharField(verbose_name=_('initials'), max_length=10, core=True, blank=True, null=True)

    def __unicode__(self):
        return self.diploma

    class Admin:
        pass

    class Meta:
        verbose_name = _('diploma')

# Decoration received by people (war cross, etc.)
class Decoration(models.Model):

    decoration = models.CharField(verbose_name=_('decoration'), max_length=200, core=True)

    def __unicode__(self):
        return self.decoration

    class Admin:
        pass

    class Meta:
        verbose_name = _('decoration')

# Honorific functions occupied by some persons
class CeremonialDuty(models.Model):

    ceremonial_duty = models.CharField(verbose_name=_('ceremonial duty'), max_length=200, core=True)

    def __unicode__(self):
        return self.ceremonial_duty

    class Admin:
        pass

    class Meta:
        verbose_name = _('ceremonial duty')
        verbose_name_plural = _('ceremonial duties')

# School where users come from
class School(models.Model):

    name = models.CharField(verbose_name=_('name'), max_length=500)
    initials = models.CharField(verbose_name=_('initials'), max_length=10, blank=True, null=True)

    line1 = models.CharField(verbose_name=_('line1'), max_length=50, blank=True, null=True)
    line2 = models.CharField(verbose_name=_('line2'), max_length=100, blank=True, null=True)
    zip_code = models.CharField(verbose_name=_('zip code'), max_length=20, blank=True, null=True)
    city = models.CharField(verbose_name=_('city'), max_length=50, blank=True, null=True)
    country = models.ForeignKey(Country, verbose_name=_('country'), blank=True, null=True)

    phone_number = models.CharField(verbose_name=_('phone number'), max_length=20, blank=True, null=True)
    web_site = models.CharField(verbose_name=_('web site'), max_length=100, blank=True, null=True)
    email = models.EmailField(verbose_name=_('email'), blank=True, null=True)

    def __unicode__(self):
        if self.initials:
            return self.initials
        else:
            return self.name

    class Admin:
        pass

    class Meta:
        verbose_name = _('school')

# Speciality the student has studied during his cursus
class Track(models.Model):

    name = models.CharField(verbose_name=_('name'), max_length=100)
    initials = models.CharField(verbose_name=_('initials'), max_length=10, blank=True, null=True)
    email = models.EmailField(verbose_name=_('email'), blank=True, null=True)

    active = models.BooleanField(verbose_name=_('active'))

    school = models.ForeignKey(School, verbose_name=_('school'), related_name='tracks')

    def __unicode__(self):
        if self.initials:
            return self.initials
        else:
            return self.name

    class Admin:
        pass

    class Meta:
        verbose_name = _('Track')

# Promo the student get out from school
class Promo(models.Model):

    year = models.IntegerField(verbose_name=_('year'))
    track = models.ForeignKey(Track, verbose_name=_('Track'), related_name='promos')

    def __unicode__(self):
        return str(self.track) + " " + str(self.year)

    class Admin:
        pass

    class Meta:
        verbose_name = _('Promo')
        ordering = ['year']


# a Manager for the class Person
class PersonManager(models.Manager):
    
    def adv_search_fields(self, user):
        """ Returns the list of field names that can be used as criteria
        in advanced search."""
        critsForAll  = [
            "last_name" , "first_name" , "complete_name" , "maiden_name" ,
            "birth_date", "death_date" , "sex" , "country" , "wiki_name" ,
            "notes" ]
        critsForAdmin = [
            "user" , "creation_date" , "modification_date" , "modifier" ]
        crits = critsForAll
        if isAdmin(user):
            crits.extend(critsForAdmin)
        return crits

# The main class for a person
class Person(models.Model):

    SEX = (
           ('M', _('Male')),
           ('F', _('Female')),
           )

    # User inheritance
    user = models.OneToOneField(User, verbose_name=_('user'))

    # Civility
    last_name = models.CharField(verbose_name=_('Last name'), max_length=50)
    first_name = models.CharField(verbose_name=_('First name'), max_length=50)
    complete_name = models.CharField(verbose_name=_('Complete name'), max_length=50)
    maiden_name = models.CharField(verbose_name=_('maiden name'), max_length=100, blank=True, null=True)
    birth_date = models.DateField(verbose_name=_('Birth date'), blank=True, null=True)
    death_date = models.DateField(verbose_name=_('death date'), blank=True, null=True)
    sex = models.CharField(verbose_name=_('sex'), max_length=1, choices=SEX, radio_admin=True)
    country = models.ForeignKey(Country, verbose_name=_('nationality'))

    wiki_name = models.CharField(verbose_name=_('Wiki name'), max_length=50, blank=True, null=True)

    notes = models.TextField(verbose_name=_('Notes'), blank=True, null=True)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)
    modifier = models.IntegerField(editable=False)
    objects = PersonManager()

    def __unicode__(self):
        return self.first_name + " " + self.last_name

    def save(self):
        self.modification_date = datetime.datetime.today()
        self.modifier = 1 # TODO
        return super(Person, self).save()

    def send_mail(self, subject, message):

       mail_list = Email.objects.filter(person=self,preferred_email=True)
       if mail_list:
           mail = mail_list[0].email

           msg = """From: AIn7 <ain7@ain7.info>
To: """+self.first_name+' '+self.last_name+' <'+mail+'>'+"""
Subject: """+subject+"""
Mime-Version: 1.0
Content-Type: text/plain; charset="utf-8"
Date:  """+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())+"""
X-Generated-By: AIn7 Web Portal

"""+message+"""
--
Vous pouvez acceder a vos donnees sur le portail: http://www.ain7.com
"""

           server = smtplib.SMTP('localhost')
           server.sendmail('ain7@ain7.info', mail, msg)
           server.quit()


    class Admin:
        list_display = ('last_name', 'first_name')
        search_fields = ['last_name', 'first_name']

    class Meta:
        verbose_name = _('person')

# a Manager for the class AIn7Member
class AIn7MemberManager(models.Manager):
    
    def adv_search_fields(self, user):
        """ Returns the list of field names that can be used as criteria
        in advanced search."""
        critsForAll  = [
            "activity" , "marital_status" , "children_count" , "nick_name" ,
            "promos"   , "diplomas"       , "decorations"    , "cv_title"  ,
            "ceremonial_duties" ]
        critsForAdmin = [
            "person" , "person_type" , "member_type" ,
            "display_cv_in_directory" , "display_cv_in_job_section" ,
            "receive_job_offers" , "receive_job_offers_for_tracks" ]
        crits = critsForAll
        if isAdmin(user):
            crits.extend(critsForAdmin)
        return crits

# AIn7 member
class AIn7Member(models.Model):

    person = models.OneToOneField(Person, verbose_name=_('person'))

    # Administration
    person_type = models.ForeignKey(PersonType, verbose_name=_('type'))
    member_type = models.ForeignKey(MemberType, verbose_name=_('member'))
    activity = models.ForeignKey(Activity, verbose_name=_('activity'))

    # Family situation
    marital_status = models.ForeignKey(MaritalStatus, verbose_name=_('marital status'), blank=True, null=True)
    children_count = models.IntegerField(verbose_name=_('children number'), blank=True, null=True)

    # Other
    nick_name = models.CharField(verbose_name=_('Nick name'), max_length=50, blank=True, null=True)
    avatar = models.ImageField(verbose_name=_('avatar'), upload_to='data/', blank=True, null=True)

    # School situation
    promos = models.ManyToManyField(Promo, verbose_name=_('Promos'), related_name='students', blank=True, null=True, filter_interface=models.HORIZONTAL)
    diplomas = models.ManyToManyField(Diploma, verbose_name=_('diplomas'), related_name='graduates', blank=True, null=True, filter_interface=models.HORIZONTAL)

    # Civil situation
    decorations = models.ManyToManyField(Decoration, verbose_name=_('decorations'), blank=True, null=True, filter_interface=models.HORIZONTAL)
    ceremonial_duties = models.ManyToManyField(CeremonialDuty, verbose_name=_('ceremonial duties'), blank=True, null=True, filter_interface=models.HORIZONTAL)

    # Curriculum Vitae and Job Service
    display_cv_in_directory = models.BooleanField(verbose_name=_('Display my CV in the directory'), core=True, default=False)
    display_cv_in_job_section = models.BooleanField(verbose_name=_('Display my CV in the job service section'), core=True, default=True)
    receive_job_offers = models.BooleanField(verbose_name=_('Receive job offers by email'), core=True, default=False)
    receive_job_offers_for_tracks = models.ManyToManyField(
        Track,
        verbose_name=_('Tracks for which you would like to receive job offers'),
        blank=True, null=True, filter_interface=models.HORIZONTAL)
    cv_title = models.CharField(verbose_name=_('CV title'), max_length=100, blank=True, null=True)
    
    # Internal
    objects = AIn7MemberManager()

    def karma(self):
        karma = 0
        list_contrib = UserContribution.objects.filter(user=self)
        for contrib in list_contrib:
            karma = karma + UserContributionType.objects.filter(key=contrib.type.key)[0].points
        return karma

    def __unicode__(self):
        return str(self.person)

    class Admin:
        pass

    class Meta:
        verbose_name = _('AIn7 member')

class AIn7Subscription(models.Model):
    member = models.ForeignKey(AIn7Member)
    year = models.IntegerField()
    date = models.DateTimeField()
    amount = models.IntegerField()

    class Admin:
        pass

# Phone number for a person
class PhoneNumber(models.Model):

    PHONE_NUMBER_TYPE = (
                         (1, _('Fix')),
                         (2, _('Fax')),
                         (3, _('Mobile')),
                         )

    person = models.ForeignKey(Person, related_name='phone_numbers', edit_inline=models.TABULAR, num_in_admin=2)

    number = models.CharField(verbose_name=_('number'), max_length=20, core=True)
    type = models.IntegerField(verbose_name=_('type'), choices=PHONE_NUMBER_TYPE, default=1)
    is_confidential = models.BooleanField(verbose_name=_('confidential'), default=False)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)

    def save(self):
        self.modification_date = datetime.datetime.today()
        return super(PhoneNumber, self).save()

    class Meta:
        verbose_name = _('phone number')

# Type of the address: can be parental, personal or business
class AddressType(models.Model):

    type = models.CharField(verbose_name=_('type'), max_length=50)

    def __unicode__(self):
        return self.type

    class Admin:
        pass

    class Meta:
        verbose_name = _('address type')
        verbose_name_plural = _('address types')

# A person address
class Address(models.Model):

    person = models.ForeignKey(Person, related_name='addresses', edit_inline=models.STACKED, num_in_admin=2)

    line1 = models.CharField(verbose_name=_('line1'), max_length=50, core=True)
    line2 = models.CharField(verbose_name=_('line2'), max_length=100, blank=True, null=True, core=True)
    zip_code = models.CharField(verbose_name=_('zip code'), max_length=20, core=True)
    city = models.CharField(verbose_name=_('city'), max_length=50, core=True)
    country = models.ForeignKey(Country, verbose_name=_('country'))
    type = models.ForeignKey(AddressType, verbose_name=_('type'))
    is_confidential = models.BooleanField(verbose_name=_('confidential'), default=False)
    is_valid = models.BooleanField(verbose_name=_('is valid'), default=True)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)

    def __unicode__(self):
        addr  = self.line1 + " " + self.line2 + " - "
        addr += self.zip_code + " " + self.city + " - "
        addr += self.country.name
        return addr

    def save(self):
        self.modification_date = datetime.datetime.today()
        return super(Address, self).save()

    class Meta:
        verbose_name = _('Address')

# e-mail address for a person
class Email(models.Model):

    person = models.ForeignKey(Person, related_name='emails', edit_inline=models.TABULAR, num_in_admin=1)

    email = models.EmailField(verbose_name=_('email'), core=True)
    is_confidential = models.BooleanField(verbose_name=_('confidential'), default=False)
    preferred_email = models.BooleanField(verbose_name=_('preferred'), default=False)

    def __unicode__(self):
        return self.email

    class Meta:
        verbose_name = _('email')

# instant messanger contact for a person
class InstantMessaging(models.Model):

    INSTANT_MESSAGING_TYPE = (
                              (1,'ICQ'),
                              (2,'MSN'),
                              (3,'AIM'),
                              (4,'Yahoo'),
                              (5,'Jabber'),
                              (6,'Gadu-Gadu'),
                              (7,'Skype'),
                              )

    person = models.ForeignKey(Person, related_name='instant_messagings', edit_inline=models.TABULAR, num_in_admin=1)

    type = models.IntegerField(verbose_name=_('type'), choices=INSTANT_MESSAGING_TYPE, core=True)
    identifier = models.CharField(verbose_name=_('identifier'), max_length=40, core=True)

    def __unicode__(self):
        return self.identifier

    class Meta:
        verbose_name = _('instant_messaging')

# Website for a person
class WebSite(models.Model):

    WEBSITE_TYPE = (
                    (0,'web'),
                    (1,'blog'),
                    (2,'gallery'),
                    (3,'linkedin'),
                    (4,'viadeo'),
                    (5,'flickr'),
                    (6,'facebook'),
                    (7,'twitter'),
                    (8,'myspace'),
                    (100,'Other'),
                   )

    person = models.ForeignKey(Person, related_name='web_sites', edit_inline=models.TABULAR, num_in_admin=1)

    url = models.CharField(verbose_name=_('web site'), max_length=100, core=True)
    type = models.IntegerField(verbose_name=_('type'),choices=WEBSITE_TYPE, core=True)

    blog_is_agregated_on_planet = models.BooleanField(verbose_name=_('blog on planet'), core=True, default=False)

    def __unicode__(self):
        return self.url

    def save(self):
        if not self.url.startswith('http://'):
            self.url = 'http://'+self.url
        return super(WebSite, self).save()

    class Meta:
        verbose_name = _('web site')

# IRC contact for a person
class IRC(models.Model):

    person = models.ForeignKey(Person, related_name='ircs', edit_inline=models.TABULAR, num_in_admin=1)

    network = models.CharField(verbose_name=_('network'), max_length=50, core=True)
    pseudo = models.CharField(verbose_name=_('pseudo'), max_length=20, core=True)
    channels = models.CharField(verbose_name=_('channels'), max_length=100)

    def __unicode__(self):
        return self.pseudo + "@" + self.channels

    class Meta:
        verbose_name = _('irc')

# N7 club
class Club(models.Model):

    name = models.CharField(verbose_name=('name'), max_length=20)
    description = models.CharField(verbose_name=_('description'), max_length=100)
    web_site = models.URLField(verbose_name=_('web site'), max_length=50, blank=True, null=True)
    email = models.EmailField(verbose_name=_('email'), max_length=50, blank=True, null=True)
    school = models.ForeignKey(School, verbose_name=_('school'), related_name='clubs')
    icon = models.ImageField(verbose_name=_('icon'), upload_to='data/', blank=True, null=True)

    # Internal
    creation_date = models.DateField(verbose_name=_('creation date'), blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Admin:
        pass

    class Meta:
        verbose_name = _('club')

# Club membership for a person
class ClubMembership(models.Model):

    club = models.ForeignKey(Club, verbose_name=_('club'), related_name='memberships', edit_inline=models.TABULAR, num_in_admin=1)
    member = models.ForeignKey(AIn7Member, verbose_name=_('member'), related_name='club_memberships', edit_inline=models.TABULAR, num_in_admin=1)

    fonction = models.CharField(verbose_name=_('fonction'), max_length=50, core=True)
    start_date = models.DateField(verbose_name=_('start date'), blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)

    def __unicode__(self):
        return str(self.club) + " " + self.fonction

    class Meta:
        verbose_name = _('club membership')
        verbose_name_plural = _('club memberships')
        ordering = ['start_date']

# A profile indicates which rights has a user
class Profile(models.Model):

    name = models.CharField(verbose_name=_('name'), max_length=50)
    description = models.TextField(verbose_name=_('description'), blank=True, null=True)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)

    def __unicode__(self):
        return self.name

    def save(self):
        self.modification_date = datetime.datetime.today()
        return super(Profile, self).save()

    class Admin:
        pass

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

# This class links Users with their Profiles
class ProfileMembership(models.Model):

    user = models.ForeignKey(User, verbose_name=_('user'),
                             related_name='profiles')
    profile = models.ForeignKey(Profile, verbose_name=_('profile'),
                                related_name='memberships')

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)
    modifier = models.IntegerField(editable=False)

    def __unicode__(self):
        return str(self.user) + ": " + str(self.profile)

    def save(self):
        self.modification_date = datetime.datetime.today()
        self.modifier = 1 # TODO
        return super(ProfileMembership, self).save()

    class Admin:
        pass

    class Meta:
        verbose_name = _('profile membership')
        verbose_name_plural = _('profiles memberships')

class UserContributionType(models.Model):
     key = models.CharField(verbose_name=_('key'),max_length=10)
     name = models.CharField(verbose_name=_('name'), max_length=50)
     points = models.IntegerField(verbose_name=_('number of points'))

     class Admin:
         pass

class UserContribution(models.Model):
     user = models.ForeignKey(Person, verbose_name=_('user'))
     type = models.ForeignKey(UserContributionType, verbose_name=_('type'))
     date = models.DateTimeField(verbose_name=_('date of contribution'), default=datetime.datetime.now, editable=False)

     class Admin:
         pass


# For advanced search : filters !

class SearchFilterManager(models.Manager):
    
    def get_registered(self, person):
        return self.filter(registered=True).filter(user=person)
    
    def get_unregistered(self, person):
        unregs = self.filter(registered=False).filter(user=person)
        if unregs:
            assert(unregs.count()<2)
            return unregs[0]
        return None

class SearchFilter(models.Model):
    OPERATORS = [ ('and', _('and')),
                  ('or', _('or')) ]
    name = models.CharField(verbose_name=_('name'), max_length=20)
    operator = models.CharField(verbose_name=_('operator'),
                                max_length=3, choices=OPERATORS)
    user = models.ForeignKey(Person, verbose_name=_('user'),
                             related_name='filters')
    registered = models.BooleanField(default=True)
    objects = SearchFilterManager()

    def __unicode__(self):
        return self.name

    def save(self):
        self.modification_date = datetime.datetime.today()
        return super(SearchFilter, self).save()

    class Admin:
        pass

    class Meta:
        verbose_name = _('filter')
        verbose_name_plural = _('filters')

class SearchCriterionField(models.Model):
    searchFilter = models.ForeignKey(SearchFilter,
                                     related_name='criteriaField')
    fieldName = models.CharField(max_length=30)
    fieldVerboseName = models.CharField(max_length=50)
    fieldClass = models.CharField(max_length=30)
    comparatorName = models.CharField(max_length=2)
    comparatorVerboseName = models.CharField(max_length=20)
    value = models.CharField(max_length=50)
    displayedValue = models.CharField(max_length=50)
    # Example: for a criterion 'prénom égale Toto'
    #     fieldName = 'last_name'
    #     fieldVerboseName = 'prénom'
    #     fieldClass = 'Person'
    #     comparatorName = 'EQ'
    #     comparatorVerboseName = 'égale'
    #     value = 'Toto'
    #     displayedValue = 'Toto'

    def __unicode__(self):
        return self.fieldVerboseName + " " \
               + self.comparatorVerboseName + " " \
               + self.displayedValue

    def save(self):
        self.modification_date = datetime.datetime.today()
        return super(SearchCriterionField, self).save()


class SearchCriterionFilter(models.Model):
    searchFilter = models.ForeignKey(SearchFilter,
        related_name='criteriaFilter', core=True)
    filterCriterion = models.ForeignKey(SearchFilter,
        related_name='used_as_criterion')
    is_in = models.BooleanField(default=True)

    def __unicode__(self):
        return str(filterCriterion)

    def save(self):
        self.modification_date = datetime.datetime.today()
        return super(SearchCriterionFilter, self).save()

