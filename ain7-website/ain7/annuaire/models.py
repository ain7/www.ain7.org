# -*- coding: utf-8
#
# annuaire/models.py
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
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Country (used for adresses)
class Country(models.Model):

    name = models.CharField(verbose_name=_('name'), maxlength=50)
    nationality = models.CharField(verbose_name=_('nationality'), maxlength=50)

    def __str__(self):
        return self.name

    class Admin:
        pass

    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('country')

# Indicates the current status of a person: Student, Ingeneer
class PersonType(models.Model):

    type = models.CharField(verbose_name=_('type'), maxlength=50)

    def __str__(self):
        return self.type

    class Admin:
        pass

    class Meta:
        verbose_name = _('person type')
        verbose_name_plural = _('person types')

# Indicates the current relation with the association: actif member or ?
class MemberType(models.Model):

    type = models.CharField(verbose_name=_('type'), maxlength=50)

    def __str__(self):
        return self.type

    class Admin:
        pass

    class Meta:
        verbose_name = _('member type')

# Indicates the current main activity of the person: student, active retired, ... 
class Activity(models.Model):

    activity = models.CharField(verbose_name=_('activity'), maxlength=50)

    def __str__(self):
        return self.activity

    class Admin:
        pass

    class Meta:
        verbose_name = _('activity')

# Diploma received
class Diploma(models.Model):

    diploma = models.CharField(verbose_name=_('diploma'), maxlength=100, core=True)
    initials = models.CharField(verbose_name=_('initials'), maxlength=10, core=True, blank=True, null=True)

    def __str__(self):
        return self.diploma

    class Admin:
        pass

    class Meta:
        verbose_name = _('diploma')

# Decoration received by people (war cross, etc.)
class Decoration(models.Model):

    decoration = models.CharField(verbose_name=_('decoration'), maxlength=200, core=True)

    def __str__(self):
        return self.decoration

    class Admin:
        pass

    class Meta:
        verbose_name = _('decoration')

# Honorific functions occupied by some persons
class CeremonialDuty(models.Model):

    ceremonial_duty = models.CharField(verbose_name=_('ceremonial duty'), maxlength=200, core=True)

    def __str__(self):
        return self.ceremonial_duty

    class Admin:
        pass

    class Meta:
        verbose_name = _('ceremonial duty')
        verbose_name_plural = _('ceremonial duties')

# School where users come from
class School(models.Model):

    name = models.CharField(verbose_name=_('name'), maxlength=500)
    initials = models.CharField(verbose_name=_('initials'), maxlength=10, blank=True, null=True)

    number = models.CharField(verbose_name=_('number'), maxlength=50, blank=True, null=True)
    street = models.CharField(verbose_name=_('street'), maxlength=100, blank=True, null=True)
    zip_code = models.CharField(verbose_name=_('zip code'), maxlength=20, blank=True, null=True)
    city = models.CharField(verbose_name=_('city'), maxlength=50, blank=True, null=True)
    country = models.ForeignKey(Country, verbose_name=_('country'), blank=True, null=True)

    phone_number = models.CharField(verbose_name=_('phone number'), maxlength=20, blank=True, null=True)
    web_site = models.CharField(verbose_name=_('web site'), maxlength=100, blank=True, null=True)
    email = models.EmailField(verbose_name=_('email'), blank=True, null=True)

    def __str__(self):
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

    name = models.CharField(verbose_name=_('name'), maxlength=100)
    initials = models.CharField(verbose_name=_('initials'), maxlength=10, blank=True, null=True)
    email = models.EmailField(verbose_name=_('email'), blank=True, null=True)

    active = models.BooleanField(verbose_name=_('active'))

    school = models.ForeignKey(School, verbose_name=_('school'), related_name='tracks')

    def __str__(self):
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

    def __str__(self):
        return str(self.track) + " " + str(self.year)

    class Admin:
        pass

    class Meta:
        verbose_name = _('Promo')
        ordering = ['year']

# The main class for a person
class Person(models.Model):

    SEX = (
           ('M', _('Male')),
           ('F', _('Female')),
           )

    # User inheritance
    user = models.OneToOneField(User, verbose_name=_('user'))

    # Civility
    sex = models.CharField(verbose_name=_('sex'), maxlength=1, choices=SEX, radio_admin=True)
    last_name = models.CharField(verbose_name=_('Last name'), maxlength=50)
    first_name = models.CharField(verbose_name=_('First name'), maxlength=50)
    maiden_name = models.CharField(verbose_name=_('maiden name'), maxlength=100, blank=True, null=True)
    birth_date = models.DateField(verbose_name=_('Birth date'), blank=True, null=True)
    death_date = models.DateField(verbose_name=_('death date'), blank=True, null=True)
    country = models.ForeignKey(Country, verbose_name=_('nationality'))
    
    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)
    modifier = models.IntegerField(editable=False)

    def __str__(self):
        return self.first_name + " " + self.last_name

    def save(self):
        self.modification_date = datetime.datetime.today()
        self.modifier = 1 # TODO
        return super(Person, self).save()

    class Admin:
        list_display = ('last_name', 'first_name')
        search_fields = ['last_name', 'first_name']

    class Meta:
        verbose_name = _('person')

# AIn7 member
class AIn7Member(models.Model):

    person = models.OneToOneField(Person, verbose_name=_('person'))

    # Administration
    person_type = models.ForeignKey(PersonType, verbose_name=_('type'))
    member_type = models.ForeignKey(MemberType, verbose_name=_('member'))
    activity = models.ForeignKey(Activity, verbose_name=_('activity'))

    # Family situation
    is_married = models.BooleanField(verbose_name=_('married'), core=True, default=False)
    children_count = models.IntegerField(verbose_name=_('children number'), blank=True, null=True)

    # Other
    nick_name = models.CharField(verbose_name=_('Nick name'), maxlength=50, blank=True, null=True)
    avatar = models.ImageField(verbose_name=_('avatar'), upload_to='data/', blank=True, null=True)
    blog = models.URLField(verbose_name=_('blog'), maxlength=80, verify_exists=True, blank=True, core=True)
    blog_is_agregated_on_planet = models.BooleanField(verbose_name=_('blog on planet'), core=True, default=False)

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
    cvTitle = models.CharField(verbose_name=_('CV title'), maxlength=100, blank=True, null=True)

    def __str__(self):
        return str(self.person)

    class Admin:
        pass

    class Meta:
        verbose_name = _('AIn7 member')

# Phone number for a person
class PhoneNumber(models.Model):

    PHONE_NUMBER_TYPE = (
                         (1, _('Fix')),
                         (2, _('Fax')),
                         (3, _('Mobile')),
                         )

    number = models.CharField(verbose_name=_('number'), maxlength=20, core=True)
    type = models.IntegerField(verbose_name=_('type'), choices=PHONE_NUMBER_TYPE, default=1)
    is_confidential = models.BooleanField(verbose_name=_('confidential'), default=False)

    person = models.ForeignKey(Person, related_name='phone_numbers', edit_inline=models.TABULAR, num_in_admin=2)

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

    type = models.CharField(verbose_name=_('type'), maxlength=50)

    def __str__(self):
        return self.type

    class Admin:
        pass

    class Meta:
        verbose_name = _('address type')
        verbose_name_plural = _('address types')

# A person address
class Address(models.Model):

    number = models.CharField(verbose_name=_('number'), maxlength=50, core=True)
    street = models.CharField(verbose_name=_('street'), maxlength=100, core=True)
    zip_code = models.CharField(verbose_name=_('zip code'), maxlength=20, core=True)
    city = models.CharField(verbose_name=_('city'), maxlength=50, core=True)
    country = models.ForeignKey(Country, verbose_name=_('country'))
    type = models.ForeignKey(AddressType, verbose_name=_('type'))
    is_confidential = models.BooleanField(verbose_name=_('confidential'), default=False)

    person = models.ForeignKey(Person, related_name='addresses', edit_inline=models.STACKED, num_in_admin=2)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)

    def __str__(self):
        addr  = self.number + " " + self.street + " - "
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

    email = models.EmailField(verbose_name=_('email'), core=True)
    is_confidential = models.BooleanField(verbose_name=_('confidential'), default=False)

    person = models.ForeignKey(Person, related_name='emails', edit_inline=models.TABULAR, num_in_admin=1)

    def __str__(self):
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

    type = models.IntegerField(verbose_name=_('type'), choices=INSTANT_MESSAGING_TYPE, core=True)
    identifier = models.CharField(verbose_name=_('identifier'), maxlength=40, core=True)

    person = models.ForeignKey(Person, related_name='instant_messagings', edit_inline=models.TABULAR, num_in_admin=1)

    def __str__(self):
        return self.identifier

    class Meta:
        verbose_name = _('instant_messaging')

# Website for a person
class WebSite(models.Model):

    url = models.CharField(verbose_name=_('web site'), maxlength=100, core=True)

    person = models.ForeignKey(Person, related_name='web_sites', edit_inline=models.TABULAR, num_in_admin=1)

    def __str__(self):
        return self.url

    class Meta:
        verbose_name = _('web site')

# IRC contact for a person
class IRC(models.Model):

    network = models.CharField(verbose_name=_('network'), maxlength=50, core=True)
    pseudo = models.CharField(verbose_name=_('pseudo'), maxlength=20, core=True)
    channels = models.CharField(verbose_name=_('channels'), maxlength=100)

    person = models.ForeignKey(Person, related_name='ircs', edit_inline=models.TABULAR, num_in_admin=1)

    def __str__(self):
        return self.pseudo + "@" + self.channels

    class Meta:
        verbose_name = _('irc')

# N7 club
class Club(models.Model):

    name = models.CharField(verbose_name=('name'), maxlength=20)
    description = models.CharField(verbose_name=_('description'), maxlength=100)
    web_site = models.URLField(verbose_name=_('web site'), maxlength=50, blank=True, null=True)
    email = models.EmailField(verbose_name=_('email'), maxlength=50, blank=True, null=True)
    creation_date = models.DateField(verbose_name=_('creation date'), blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)

    school = models.ForeignKey(School, verbose_name=_('school'), related_name='clubs')

    def __str__(self):
        return self.name

    class Admin:
        pass

    class Meta:
        verbose_name = _('club')

# Club membership for a person
class ClubMembership(models.Model):

    fonction = models.CharField(verbose_name=_('fonction'), maxlength=50, core=True)
    start_date = models.DateField(verbose_name=_('start date'), blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)

    club = models.ForeignKey(Club, verbose_name=_('club'), related_name='memberships', edit_inline=models.TABULAR, num_in_admin=1)
    member = models.ForeignKey(AIn7Member, verbose_name=_('member'), related_name='club_memberships', edit_inline=models.TABULAR, num_in_admin=1)

    def __str__(self):
        return str(self.club) + " " + self.fonction

    class Meta:
        verbose_name = _('club membership')
        verbose_name_plural = _('club memberships')
        ordering = ['start_date']

# A profile indicates which rights has a user
class Profile(models.Model):

    name = models.CharField(verbose_name=_('name'), maxlength=50)
    description = models.TextField(verbose_name=_('description'), blank=True, null=True)
    
    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)

    def __str__(self):
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

    def __str__(self):
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
