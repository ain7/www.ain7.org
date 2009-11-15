# -*- coding: utf-8
#
# annuaire/models.py
#
#   Copyright © 2007-2009 AIn7 Devel Team
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

from ain7.utils import isAdmin, LoggedClass
from ain7.utils import ain7_website_confidential, CONFIDENTIALITY_LEVELS

# Country (used for adresses)
class Country(models.Model):

    name = models.CharField(verbose_name=_('name'), max_length=50)
    nationality = models.CharField(verbose_name=_('nationality'), max_length=50)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('country')

# Indicates the current status of a person: Student, Ingeneer
class PersonType(models.Model):

    type = models.CharField(verbose_name=_('type'), max_length=50)

    def __unicode__(self):
        return self.type

    class Meta:
        verbose_name = _('person type')
        verbose_name_plural = _('person types')

# Indicates the current relation with the association: actif member or ?
class MemberType(models.Model):

    type = models.CharField(verbose_name=_('type'), max_length=50)

    def __unicode__(self):
        return self.type

    class Meta:
        verbose_name = _('member type')

# Indicates the current main activity of the person: student, active retired, ...
class Activity(models.Model):

    activity = models.CharField(verbose_name=_('activity'), max_length=50)

    def __unicode__(self):
        return self.activity

    class Meta:
        verbose_name = _('activity')

# Indicates the current marital status of the person: single, married, ...
class MaritalStatus(models.Model):

    status = models.CharField(verbose_name=_('status'), max_length=50)

    def __unicode__(self):
        return self.status

    class Meta:
        verbose_name = _('marital status')

# Decoration received by people (war cross, etc.)
class Decoration(models.Model):

    decoration = models.CharField(verbose_name=_('decoration'), max_length=200)

    def __unicode__(self):
        return self.decoration

    class Meta:
        verbose_name = _('decoration')

# Honorific functions occupied by some persons
class CeremonialDuty(models.Model):

    ceremonial_duty = models.CharField(verbose_name=_('ceremonial duty'), max_length=200)

    def __unicode__(self):
        return self.ceremonial_duty

    class Meta:
        verbose_name = _('ceremonial duty')
        verbose_name_plural = _('ceremonial duties')

# School where users come from
class School(models.Model):

    name = models.CharField(verbose_name=_('name'), max_length=500)
    initials = models.CharField(verbose_name=_('initials'), max_length=20, blank=True, null=True)

    line1 = models.CharField(verbose_name=_('line1'), max_length=50, blank=True, null=True)
    line2 = models.CharField(verbose_name=_('line2'), max_length=100, blank=True, null=True)
    zip_code = models.CharField(verbose_name=_('zip code'), max_length=20, blank=True, null=True)
    city = models.CharField(verbose_name=_('city'), max_length=50, blank=True, null=True)
    country = models.ForeignKey(Country, verbose_name=_('country'), blank=True, null=True)

    phone_number = models.CharField(verbose_name=_('phone number'), max_length=30, blank=True, null=True)
    web_site = models.CharField(verbose_name=_('web site'), max_length=100, blank=True, null=True)
    email = models.EmailField(verbose_name=_('email'), blank=True, null=True)

    def __unicode__(self):
        if self.initials:
            return self.initials
        else:
            return self.name

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

    class Meta:
        verbose_name = _('Track')

class PromoYear(models.Model):
    year = models.IntegerField(verbose_name=_('year'))

    def __unicode__(self):
        return str(self.year)

    class Meta:
        verbose_name = _('Year')

# Promo the student get out from school
class Promo(models.Model):

    #year = models.IntegerField(verbose_name=_('year'))
    year = models.ForeignKey(PromoYear, verbose_name=_('Promo Year'), related_name='promosyear')
    track = models.ForeignKey(Track, verbose_name=_('Track'), related_name='promos')

    def __unicode__(self):
        return str(self.track) + " " + str(self.year.year)

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
            "birth_date", "death_date" , "sex" , "country" , 
            "notes" ]
        critsForAdmin = [
            "user" , "last_change_at" , "last_change_by" ]
        crits = critsForAll
        if isAdmin(user):
            crits.extend(critsForAdmin)
        return crits

# The main class for a person
class Person(LoggedClass):

    SEX = (
           ('M', _('Male')),
           ('F', _('Female')),
           )

    # User inheritance
    user = models.OneToOneField(User, verbose_name=_('user'))

    # from the old DB
    old_id = models.IntegerField(verbose_name='old id', blank=True, null=True)

    # Civility
    last_name = models.CharField(verbose_name=_('Last name'), max_length=50)
    first_name = models.CharField(verbose_name=_('First name'), max_length=50)
    complete_name = models.CharField(verbose_name=_('Complete name'), max_length=50)
    maiden_name = models.CharField(verbose_name=_('maiden name'), max_length=100, blank=True, null=True)
    birth_date = models.DateField(verbose_name=_('Birth date'), blank=True, null=True)
    death_date = models.DateField(verbose_name=_('death date'), blank=True, null=True)
    sex = models.CharField(verbose_name=_('sex'), max_length=1, choices=SEX)
    country = models.ForeignKey(Country, verbose_name=_('nationality'), blank=True, null=True)

    notes = models.TextField(verbose_name=_('Notes'), blank=True, null=True)

    objects = PersonManager()

    def __unicode__(self):
        return self.first_name + " " + self.last_name

    def send_mail(self, subject, message):

       mail_list = Email.objects.filter(person=self,preferred_email=True)
       if mail_list:
           mail = mail_list[0].email

           msg = """From: Association AIn7 <ain7@ain7.com>
To: """+self.first_name+' '+self.last_name+' <'+mail+'>'+"""
Subject: """+subject+"""
Mime-Version: 1.0
Content-Type: text/plain; charset="utf-8"
Date:  """+time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())+"""
X-Generated-By: AIn7 Web Portal

"""+message


           server = smtplib.SMTP('localhost')
           server.sendmail('ain7@ain7.com', mail, unicode(msg).encode('utf8'))
           server.quit()


    class Meta:
        verbose_name = _('person')
        ordering = ['last_name', 'first_name']

# a Manager for the class AIn7Member
class AIn7MemberManager(models.Manager):
    
    def adv_search_fields(self, user):
        """ Returns the list of field names that can be used as criteria
        in advanced search."""
        critsForAll  = [
            "activity" , "marital_status" , "children_count" , "nick_name" ,
            "promos"   , "decorations"    , "cv_title" , "ceremonial_duties" ]
        critsForAdmin = [
            "person" , "person_type" , "member_type" ,
            "display_cv_in_directory" , "display_cv_in_job_section" ,
            "receive_job_offers" , "receive_job_offers_for_tracks" ]
        crits = critsForAll
        if isAdmin(user):
            crits.extend(critsForAdmin)
        return crits

# AIn7 member
class AIn7Member(LoggedClass):

    person = models.OneToOneField(Person, verbose_name=_('person'))

    # Administration
    person_type = models.ForeignKey(PersonType, verbose_name=_('type'))
    member_type = models.ForeignKey(MemberType, verbose_name=_('member'))
    activity = models.ForeignKey(Activity, verbose_name=_('activity'), blank=True, null=True)

    # Family situation
    marital_status = models.ForeignKey(MaritalStatus, verbose_name=_('marital status'), blank=True, null=True)
    children_count = models.IntegerField(verbose_name=_('children number'), blank=True, null=True)

    # Other
    nick_name = models.CharField(verbose_name=_('Nick name'), max_length=50, blank=True, null=True)
    avatar = models.ImageField(verbose_name=_('avatar'), upload_to='data/', blank=True, null=True)

    # School situation
    promos = models.ManyToManyField(Promo, verbose_name=_('Promos'), related_name='students', blank=True, null=True)

    # Civil situation
    decorations = models.ManyToManyField(Decoration, verbose_name=_('decorations'), blank=True, null=True)
    ceremonial_duties = models.ManyToManyField(CeremonialDuty, verbose_name=_('ceremonial duties'), blank=True, null=True)

    # Curriculum Vitae and Job Service
    display_cv_in_directory = models.BooleanField(verbose_name=_('Display my professional cursus in the directory'), default=True)
    display_cv_in_job_section = models.BooleanField(verbose_name=_('Display my CV in the job service section'), default=False)
    receive_job_offers = models.BooleanField(verbose_name=_('Receive job offers by email'), default=False)
    receive_job_offers_for_tracks = models.ManyToManyField(
        Track,
        verbose_name=_('Tracks for which you would like to receive job offers'),
        blank=True, null=True)
    cv_title = models.CharField(verbose_name=_('CV title'), max_length=100, blank=True, null=True)
    
    # Internal
    objects = AIn7MemberManager()

    def interesting_jobs(self):
        """Si la personne souhaite recevoir les offres de certaines filières,
        renvoie les offres pour ces filières.
        Sinon, renvoie toutes les offres."""
        jobs = []
        if self.receive_job_offers_for_tracks.all():
            for track in self.receive_job_offers_for_tracks.all():
                jobs.extend(track.jobs.filter(checked_by_secretariat=True))
        else:
            for track in Track.objects.all():
                jobs.extend(track.jobs.filter(checked_by_secretariat=True))
        return jobs

    def __unicode__(self):
        return unicode(self.person)

    class Meta:
        verbose_name = _('AIn7 member')
        ordering = ['person']

# Phone number for a person
class PhoneNumber(LoggedClass):

    PHONE_NUMBER_TYPE = (
                         (1, _('Fix')),
                         (2, _('Fax')),
                         (3, _('Mobile')),
                         )

    person = models.ForeignKey(Person, related_name='phone_numbers')

    number = models.CharField(verbose_name=_('number'), max_length=30)
    type = models.IntegerField(verbose_name=_('type'), choices=PHONE_NUMBER_TYPE, default=1)
    confidentiality = models.IntegerField(verbose_name=_('confidentiality'),
        choices=CONFIDENTIALITY_LEVELS, default=0)

    def website_confidential(self):
        return ain7_website_confidential(self)

    def confidentiality_print(self):
        return CONFIDENTIALITY_LEVELS[self.confidentiality][1]

    def __unicode__(self):
        return self.number

    class Meta:
        verbose_name = _('phone number')

# Type of the address: can be parental, personal or business
class AddressType(models.Model):

    type = models.CharField(verbose_name=_('type'), max_length=50)

    def __unicode__(self):
        return self.type

    class Meta:
        verbose_name = _('address type')
        verbose_name_plural = _('address types')

# A person address
class Address(LoggedClass):

    person = models.ForeignKey(Person, related_name='addresses')

    line1 = models.CharField(verbose_name=_('address line1'), max_length=50)
    line2 = models.CharField(verbose_name=_('address line2'), max_length=100, blank=True, null=True)
    zip_code = models.CharField(verbose_name=_('zip code'), max_length=20)
    city = models.CharField(verbose_name=_('city'), max_length=50)
    country = models.ForeignKey(Country, verbose_name=_('country'))
    type = models.ForeignKey(AddressType, verbose_name=_('type'))
    confidentiality = models.IntegerField(verbose_name=_('confidentiality'),
        choices=CONFIDENTIALITY_LEVELS, default=0)
    is_valid = models.BooleanField(verbose_name=_('is valid'), default=True)

    def website_confidential(self):
        return ain7_website_confidential(self)

    def confidentiality_print(self):
        return CONFIDENTIALITY_LEVELS[self.confidentiality][1]

    def __unicode__(self):
        addr  = self.line1 + " " + self.line2 + " - "
        addr += self.zip_code + " " + self.city + " - "
        addr += self.country.name
        return addr

    class Meta:
        verbose_name = _('Address')

# e-mail address for a person
class Email(models.Model):

    person = models.ForeignKey(Person, related_name='emails')

    email = models.EmailField(verbose_name=_('email'))
    confidentiality = models.IntegerField(verbose_name=_('confidentiality'),
        choices=CONFIDENTIALITY_LEVELS, default=0)
    preferred_email = models.BooleanField(verbose_name=_('preferred'), default=False)

    def website_confidential(self):
        return ain7_website_confidential(self)

    def confidentiality_print(self):
        return CONFIDENTIALITY_LEVELS[self.confidentiality][1]

    def __unicode__(self):
        return self.email

    def save(self):
        # if we set "preferred" to True, then other are moved to False
        if self.preferred_email==True:
            for e in Email.objects.filter(person=self.person,preferred_email=True):
                if e is not self:
                    e.preferred_email = False
                    e.save()
        else:
            if Email.objects.filter(person=self.person,preferred_email=True).count() == 0:
                self.preferred_email = True
        return super(Email, self).save()

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

    person = models.ForeignKey(Person, related_name='instant_messagings')

    type = models.IntegerField(verbose_name=_('type'), choices=INSTANT_MESSAGING_TYPE)
    identifier = models.CharField(verbose_name=_('identifier'), max_length=40)
    confidentiality = models.IntegerField(verbose_name=_('confidentiality'),
        choices=CONFIDENTIALITY_LEVELS, default=0)

    def website_confidential(self):
        return ain7_website_confidential(self)

    def confidentiality_print(self):
        return CONFIDENTIALITY_LEVELS[self.confidentiality][1]

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

    person = models.ForeignKey(Person, related_name='web_sites')

    url = models.CharField(verbose_name=_('web site'), max_length=100)
    type = models.IntegerField(verbose_name=_('type'),choices=WEBSITE_TYPE)
    confidentiality = models.IntegerField(verbose_name=_('confidentiality'),
        choices=CONFIDENTIALITY_LEVELS, default=0)

    blog_is_agregated_on_planet = models.BooleanField(verbose_name=_('blog on planet'), default=False)

    def website_confidential(self):
        return ain7_website_confidential(self)

    def confidentiality_print(self):
        return CONFIDENTIALITY_LEVELS[self.confidentiality][1]

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

    person = models.ForeignKey(Person, related_name='ircs')

    network = models.CharField(verbose_name=_('network'), max_length=50)
    pseudo = models.CharField(verbose_name=_('pseudo'), max_length=20)
    channels = models.CharField(verbose_name=_('channels'), max_length=100)
    confidentiality = models.IntegerField(verbose_name=_('confidentiality'),
        choices=CONFIDENTIALITY_LEVELS, default=0)

    def website_confidential(self):
        return ain7_website_confidential(self)

    def confidentiality_print(self):
        return CONFIDENTIALITY_LEVELS[self.confidentiality][1]

    def __unicode__(self):
        return self.pseudo + "@" + self.channels

    class Meta:
        verbose_name = _('irc')

# N7 club
class Club(LoggedClass):

    name = models.CharField(verbose_name=('name'), max_length=20)
    description = models.CharField(verbose_name=_('description'), max_length=100)
    web_site = models.URLField(verbose_name=_('web site'), max_length=50, blank=True, null=True)
    email = models.EmailField(verbose_name=_('email'), max_length=50, blank=True, null=True)
    school = models.ForeignKey(School, verbose_name=_('school'), related_name='clubs')
    icon = models.ImageField(verbose_name=_('icon'), upload_to='data/', blank=True, null=True)

    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('club')

# Club membership for a person
class ClubMembership(models.Model):

    club = models.ForeignKey(Club, verbose_name=_('club'), related_name='memberships')
    member = models.ForeignKey(AIn7Member, verbose_name=_('member'), related_name='club_memberships')

    fonction = models.CharField(verbose_name=_('fonction'), max_length=50, blank=True, null=True)
    start_date = models.DateField(verbose_name=_('start date'), blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)

    def __unicode__(self):
        return str(self.club) + " " + self.fonction

    class Meta:
        verbose_name = _('club membership')
        verbose_name_plural = _('club memberships')
        ordering = ['start_date']

class UserActivity(models.Model):

    person = models.ForeignKey(Person, null=False)
    date = models.DateTimeField(verbose_name=_('start date'), null=False)
    client_host = models.CharField(max_length=256, blank=True, null=True)
    browser_info = models.TextField(null=True,blank=True)

    class Meta:
        verbose_name = _('user activity')
        verbose_name_plural = _('users activities')
        ordering = ['date']

