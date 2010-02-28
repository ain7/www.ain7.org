# -*- coding: utf-8
"""
 ain7/annuaire/models.py
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

import smtplib
import time

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from ain7.utils import isAdmin, LoggedClass
from ain7.utils import ain7_website_confidential, CONFIDENTIALITY_LEVELS

class Country(models.Model):
    """ Country (used for adresses)"""

    name = models.CharField(verbose_name=_('name'), max_length=50)
    nationality = models.CharField(verbose_name=_('nationality'), max_length=50)

    def __unicode__(self):
        """country unicode"""
        return self.name

    class Meta:
        """country meta"""
        verbose_name = _('country')
        verbose_name_plural = _('country')

class PersonType(models.Model):
    """Indicates the current status of a person: Student, Ingeneer"""

    type = models.CharField(verbose_name=_('type'), max_length=50)

    def __unicode__(self):
        """person type unicode"""
        return self.type

    class Meta:
        """person type meta"""
        verbose_name = _('person type')
        verbose_name_plural = _('person types')

class MemberType(models.Model):
    """
    Indicates the current relation with the association: actif member or ?
    """

    type = models.CharField(verbose_name=_('type'), max_length=50)

    def __unicode__(self):
        """member type unicode"""
        return self.type

    class Meta:
        """member type meta"""
        verbose_name = _('member type')

class Activity(models.Model):
    """
    Indicates the current main activity of the person: student,
    active retired, ...
    """

    activity = models.CharField(verbose_name=_('activity'), max_length=50)

    def __unicode__(self):
        """activity unicode"""
        return self.activity

    class Meta:
        """activity meta"""
        verbose_name = _('activity')

class MaritalStatus(models.Model):
    """
    Indicates the current marital status of the person:
    single, married, ...
    """

    status = models.CharField(verbose_name=_('status'), max_length=50)

    def __unicode__(self):
        """marital status unicode"""
        return self.status

    class Meta:
        """marital status meta"""
        verbose_name = _('marital status')

class Decoration(models.Model):
    """Decoration received by people (war cross, etc.)"""

    decoration = models.CharField(verbose_name=_('decoration'), max_length=200)

    def __unicode__(self):
        """decoration univode"""
        return self.decoration

    class Meta:
        """decoration meta"""
        verbose_name = _('decoration')

class CeremonialDuty(models.Model):
    """Honorific functions occupied by some persons"""

    ceremonial_duty = models.CharField(verbose_name=_('ceremonial duty'),
        max_length=200)

    def __unicode__(self):
        """ceremonial duty unicode"""
        return self.ceremonial_duty

    class Meta:
        """ceremonial duty meta"""
        verbose_name = _('ceremonial duty')
        verbose_name_plural = _('ceremonial duties')

class School(models.Model):
    """school where users come from"""

    name = models.CharField(verbose_name=_('name'), max_length=500)
    initials = models.CharField(verbose_name=_('initials'), max_length=20,
        blank=True, null=True)

    line1 = models.CharField(verbose_name=_('line1'), max_length=50,
        blank=True, null=True)
    line2 = models.CharField(verbose_name=_('line2'), max_length=100,
        blank=True, null=True)
    zip_code = models.CharField(verbose_name=_('zip code'), max_length=20,
        blank=True, null=True)
    city = models.CharField(verbose_name=_('city'), max_length=50, blank=True,
        null=True)
    country = models.ForeignKey(Country, verbose_name=_('country'), blank=True,
        null=True)

    phone_number = models.CharField(verbose_name=_('phone number'),
        max_length=30, blank=True, null=True)
    web_site = models.CharField(verbose_name=_('web site'), max_length=100,
        blank=True, null=True)
    email = models.EmailField(verbose_name=_('email'), blank=True, null=True)

    def __unicode__(self):
        """school unicode"""
        if self.initials:
            return self.initials
        else:
            return self.name

    class Meta:
        """school meta"""
        verbose_name = _('school')

class Track(models.Model):
    """Speciality the student has studied during his cursus"""

    name = models.CharField(verbose_name=_('name'), max_length=100)
    initials = models.CharField(verbose_name=_('initials'), max_length=10,
        blank=True, null=True)
    email = models.EmailField(verbose_name=_('email'), blank=True, null=True)

    active = models.BooleanField(verbose_name=_('active'))

    school = models.ForeignKey(School, verbose_name=_('school'),
        related_name='tracks')

    def __unicode__(self):
        """track unicode"""
        if self.initials:
            return self.initials
        else:
            return self.name

    class Meta:
        """track meta"""
        verbose_name = _('Track')

class PromoYear(models.Model):
    year = models.IntegerField(verbose_name=_('year'))

    def __unicode__(self):
        """promo year unicode"""
        return str(self.year)

    class Meta:
        """promo year meta"""
        verbose_name = _('Year')

class Promo(models.Model):
    """Promo the student get out from school"""

    year = models.ForeignKey(PromoYear, verbose_name=_('Promo Year'),
        related_name='promosyear')
    track = models.ForeignKey(Track, verbose_name=_('Track'),
        related_name='promos')

    def __unicode__(self):
        """promo unicode"""
        return str(self.track) + " " + str(self.year.year)

    class Meta:
        """promo meta"""
        verbose_name = _('Promo')
        ordering = ['year']


class PersonManager(models.Manager):
    """a Manager for the class Person"""
    
    def adv_search_fields(self, user):
        """ Returns the list of field names that can be used as criteria
        in advanced search."""
        crits_for_all  = [
            "last_name" , "first_name" , "complete_name" , "maiden_name" ,
            "birth_date", "death_date" , "sex" , "country" , 
            "notes" ]
        crits_for_admin = [
            "user" , "last_change_at" , "last_change_by" ]
        crits = crits_for_all
        if isAdmin(user):
            crits.extend(crits_for_admin)
        return crits

class Person(LoggedClass):
    """The main class for a person"""

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
    complete_name = models.CharField(verbose_name=_('Complete name'),
        max_length=50)
    maiden_name = models.CharField(verbose_name=_('maiden name'),
        max_length=100, blank=True, null=True)
    birth_date = models.DateField(verbose_name=_('Birth date'), blank=True,
        null=True)
    sex = models.CharField(verbose_name=_('sex'), max_length=1, choices=SEX)
    country = models.ForeignKey(Country, verbose_name=_('nationality'),
        blank=True, null=True)

    objects = PersonManager()

    def __unicode__(self):
        """person unicode"""
        return self.first_name + " " + self.last_name

    def send_mail(self, subject, message):
        """person send a mail"""

        mail_list = Email.objects.filter(person=self, preferred_email=True)
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
        """person meta"""
        verbose_name = _('person')
        ordering = ['last_name', 'first_name']

class PersonPrivate(LoggedClass):
    """private data for a person"""

    person = models.OneToOneField(Person, verbose_name=_('person'))

    # Administration
    person_type = models.ForeignKey(PersonType, verbose_name=_('type'))
    member_type = models.ForeignKey(MemberType, verbose_name=_('member'))
    activity = models.ForeignKey(Activity, verbose_name=_('activity'),
        blank=True, null=True)
    death_date = models.DateField(verbose_name=_('death date'), blank=True,
        null=True)
    notes = models.TextField(verbose_name=_('Notes'), blank=True, null=True)

    def __unicode__(self):
        """AIn7 member unicode"""
        return unicode(self.person)

    class Meta:
        """Person Private Data"""
        verbose_name = _('Person Private Data')
        ordering = ['person']


class AIn7MemberManager(models.Manager):
    """a Manager for the class AIn7Member"""
    
    def adv_search_fields(self, user):
        """ Returns the list of field names that can be used as criteria
        in advanced search."""
        crits_for_all  = [
            "activity" , "marital_status" , "children_count" , "nick_name" ,
            "promos"   , "decorations"    , "cv_title" , "ceremonial_duties" ]
        crits_for_admin = [
            "person" , "person_type" , "member_type" ,
            "display_cv_in_directory" , "display_cv_in_job_section" ,
            "receive_job_offers" ]
        crits = crits_for_all
        if isAdmin(user):
            crits.extend(crits_for_admin)
        return crits

class AIn7Member(LoggedClass):
    """AIn7 member"""

    person = models.OneToOneField(Person, verbose_name=_('person'))

    # Family situation
    marital_status = models.ForeignKey(MaritalStatus,
        verbose_name=_('marital status'), blank=True, null=True)
    children_count = models.IntegerField(verbose_name=_('children number'),
        blank=True, null=True)

    # Other
    nick_name = models.CharField(verbose_name=_('Nick name'), max_length=50,
        blank=True, null=True)
    avatar = models.ImageField(verbose_name=_('avatar'), upload_to='data/',
        blank=True, null=True)

    # School situation
    promos = models.ManyToManyField(Promo, verbose_name=_('Promos'),
        related_name='students', blank=True, null=True)

    # Civil situation
    decorations = models.ManyToManyField(Decoration,
        verbose_name=_('decorations'), blank=True, null=True)
    ceremonial_duties = models.ManyToManyField(CeremonialDuty,
        verbose_name=_('ceremonial duties'), blank=True, null=True)

    # Curriculum Vitae and Job Service
    display_cv_in_directory = models.BooleanField(
        verbose_name=_('Display my professional cursus in the directory'),
        default=True)
    display_cv_in_job_section = models.BooleanField(
        verbose_name=_('Display my CV in the job service section'),
        default=False)
    receive_job_offers = models.BooleanField(
         verbose_name=_('Receive job offers by email'), default=False)
    cv_title = models.CharField(verbose_name=_('CV title'), max_length=100,
        blank=True, null=True)
    
    # Internal
    objects = AIn7MemberManager()

    def interesting_jobs(self):
        """
        Si la personne souhaite recevoir les offres de certaines filières,
        renvoie les offres pour ces filières.
        Sinon, renvoie toutes les offres.
        """
        jobs = []
        for track in Track.objects.all():
            jobs.extend(track.jobs.filter(checked_by_secretariat=True))
        return jobs

    def __unicode__(self):
        """AIn7 member unicode"""
        return unicode(self.person)

    class Meta:
        """AIn7 member meta"""
        verbose_name = _('AIn7 member')
        ordering = ['person']

class PhoneNumber(LoggedClass):
    """Phone number for a person"""

    PHONE_NUMBER_TYPE = (
                         (1, _('Fix')),
                         (2, _('Fax')),
                         (3, _('Mobile')),
                         )

    person = models.ForeignKey(Person, related_name='phone_numbers', editable=False)

    number = models.CharField(verbose_name=_('number'), max_length=30)
    type = models.IntegerField(verbose_name=_('type'),
        choices=PHONE_NUMBER_TYPE, default=1)
    confidentiality = models.IntegerField(verbose_name=_('confidentiality'),
        choices=CONFIDENTIALITY_LEVELS, default=0)

    def website_confidential(self):
        """web site confidential""" 
        return ain7_website_confidential(self)

    def confidentiality_print(self):
        """print phone number confidentiality"""
        return CONFIDENTIALITY_LEVELS[self.confidentiality][1]

    def __unicode__(self):
        """phone number unicode"""
        return self.number

    class Meta:
        """phone number meta"""
        verbose_name = _('phone number')

class AddressType(models.Model):
    """Type of the address: can be parental, personal or business"""

    type = models.CharField(verbose_name=_('type'), max_length=50)

    def __unicode__(self):
        """address type unicode"""
        return self.type

    class Meta:
        """address type meta"""
        verbose_name = _('address type')
        verbose_name_plural = _('address types')

class Address(LoggedClass):
    """A person address"""

    person = models.ForeignKey(Person, related_name='addresses', editable=False)

    line1 = models.CharField(verbose_name=_('address line1'), max_length=50)
    line2 = models.CharField(verbose_name=_('address line2'), max_length=100,
        blank=True, null=True)
    zip_code = models.CharField(verbose_name=_('zip code'), max_length=20)
    city = models.CharField(verbose_name=_('city'), max_length=50)
    country = models.ForeignKey(Country, verbose_name=_('country'))
    type = models.ForeignKey(AddressType, verbose_name=_('type'))
    confidentiality = models.IntegerField(verbose_name=_('confidentiality'),
        choices=CONFIDENTIALITY_LEVELS, default=0)
    is_valid = models.BooleanField(verbose_name=_('is valid'), default=True)

    def website_confidential(self):
        """address confidentiality"""
        return ain7_website_confidential(self)

    def confidentiality_print(self):
        """address confidentiality print"""
        return CONFIDENTIALITY_LEVELS[self.confidentiality][1]

    def __unicode__(self):
        """address unicode"""
        addr  = self.line1 + " " + self.line2 + " - "
        addr += self.zip_code + " " + self.city + " - "
        addr += self.country.name
        return addr

    class Meta:
        """address meta"""
        verbose_name = _('Address')

class Email(models.Model):
    """e-mail address for a person"""

    person = models.ForeignKey(Person, related_name='emails', editable=False)

    email = models.EmailField(verbose_name=_('email'))
    confidentiality = models.IntegerField(verbose_name=_('confidentiality'),
        choices=CONFIDENTIALITY_LEVELS, default=0)
    preferred_email = models.BooleanField(verbose_name=_('preferred'),
        default=False)

    def website_confidential(self):
        """email confidentiality for the website"""
        return ain7_website_confidential(self)

    def confidentiality_print(self):
        """email confidentiality print"""
        return CONFIDENTIALITY_LEVELS[self.confidentiality][1]

    def __unicode__(self):
        """email unicode"""
        return self.email

    def save(self):
        """ if we set "preferred" to True, then other are moved to False"""
        if self.preferred_email == True:
            for email in Email.objects.filter(person=self.person, \
                preferred_email=True):
                if email is not self:
                    email.preferred_email = False
                    email.save()
        else:
            if Email.objects.filter(person=self.person, \
                preferred_email=True).count() == 0:
                self.preferred_email = True
        return super(Email, self).save()

    class Meta:
        """email meta"""
        verbose_name = _('email')

class InstantMessaging(models.Model):
    """instant messanger contact for a person"""

    INSTANT_MESSAGING_TYPE = (
                              (1,'ICQ'),
                              (2,'MSN'),
                              (3,'AIM'),
                              (4,'Yahoo'),
                              (5,'Jabber'),
                              (6,'Gadu-Gadu'),
                              (7,'Skype'),
                              )

    person = models.ForeignKey(Person, related_name='instant_messagings',
         editable=False)

    type = models.IntegerField(verbose_name=_('type'), 
        choices=INSTANT_MESSAGING_TYPE)
    identifier = models.CharField(verbose_name=_('identifier'), max_length=40)
    confidentiality = models.IntegerField(verbose_name=_('confidentiality'),
        choices=CONFIDENTIALITY_LEVELS, default=0)

    def website_confidential(self):
        """instant messaging confidentiality on the website"""
        return ain7_website_confidential(self)

    def confidentiality_print(self):
        """print instant messenger confidentiality"""
        return CONFIDENTIALITY_LEVELS[self.confidentiality][1]

    def __unicode__(self):
        """instant messenger unicode"""
        return self.identifier

    class Meta:
        """instant messanger meta"""
        verbose_name = _('instant_messaging')

class WebSite(models.Model):
    """Website for a person"""

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

    person = models.ForeignKey(Person, related_name='web_sites',
        editable=False)

    url = models.CharField(verbose_name=_('web site'), max_length=100)
    type = models.IntegerField(verbose_name=_('type'), choices=WEBSITE_TYPE)
    confidentiality = models.IntegerField(verbose_name=_('confidentiality'),
        choices=CONFIDENTIALITY_LEVELS, default=0)

    blog_is_agregated_on_planet = models.BooleanField(
        verbose_name=_('blog on planet'), default=False)

    def website_confidential(self):
        """website confidentiality on website"""
        return ain7_website_confidential(self)

    def confidentiality_print(self):
        """print website confidentiality"""
        return CONFIDENTIALITY_LEVELS[self.confidentiality][1]

    def __unicode__(self):
        """website unicode"""
        return self.url

    def save(self):
        """website save"""
        if not self.url.startswith('http://'):
            self.url = 'http://'+self.url
        return super(WebSite, self).save()

    class Meta:
        """website meta"""
        verbose_name = _('web site')

class IRC(models.Model):
    """IRC contact for a person"""

    person = models.ForeignKey(Person, related_name='ircs', editable=False)

    network = models.CharField(verbose_name=_('network'), max_length=50)
    pseudo = models.CharField(verbose_name=_('pseudo'), max_length=20)
    channels = models.CharField(verbose_name=_('channels'), max_length=100)
    confidentiality = models.IntegerField(verbose_name=_('confidentiality'),
        choices=CONFIDENTIALITY_LEVELS, default=0)

    def website_confidential(self):
        """irc confidentiality on the website"""
        return ain7_website_confidential(self)

    def confidentiality_print(self):
        """print irc confidentiality"""
        return CONFIDENTIALITY_LEVELS[self.confidentiality][1]

    def __unicode__(self):
        """irc unicode"""
        return self.pseudo + "@" + self.channels

    class Meta:
        """irc meta"""
        verbose_name = _('irc')

class Club(LoggedClass):
    """N7 club"""

    name = models.CharField(verbose_name=('name'), max_length=20)
    description = models.CharField(verbose_name=_('description'),
        max_length=100)
    web_site = models.URLField(verbose_name=_('web site'), max_length=50,
        blank=True, null=True)
    email = models.EmailField(verbose_name=_('email'), max_length=50,
         blank=True, null=True)
    school = models.ForeignKey(School, verbose_name=_('school'),
         related_name='clubs')
    icon = models.ImageField(verbose_name=_('icon'), upload_to='data/',
         blank=True, null=True)

    end_date = models.DateField(verbose_name=_('end date'), blank=True,
         null=True)

    def __unicode__(self):
        """club unicode"""
        return self.name

    class Meta:
        """club meta"""
        verbose_name = _('club')

class ClubMembership(models.Model):
    """Club membership for a person"""

    club = models.ForeignKey(Club, verbose_name=_('club'),
        related_name='memberships')
    member = models.ForeignKey(AIn7Member, verbose_name=_('member'),
        related_name='club_memberships', editable=False)

    fonction = models.CharField(verbose_name=_('fonction'), max_length=50,
        blank=True, null=True)
    begin = models.IntegerField(verbose_name=_('start date'), blank=True,
        null=True)
    end = models.IntegerField(verbose_name=_('end date'), blank=True,
        null=True)

    def __unicode__(self):
        """club membership unicode"""
        return str(self.club) + " " + self.fonction

    class Meta:
        """club membership meta"""
        verbose_name = _('club membership')
        verbose_name_plural = _('club memberships')
        ordering = ['begin']

class UserActivity(models.Model):
    """user activity"""

    person = models.ForeignKey(Person, null=False)
    date = models.DateTimeField(verbose_name=_('start date'), null=False)
    client_host = models.CharField(max_length=256, blank=True, null=True)
    browser_info = models.TextField(null=True, blank=True)

    class Meta:
        """user activity meta"""
        verbose_name = _('user activity')
        verbose_name_plural = _('users activities')
        ordering = ['date']

