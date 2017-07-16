# -*- coding: utf-8
"""
 ain7/annuaire/models.py
"""
#
#   Copyright © 2007-2017 AIn7 Devel Team
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
import os
import time
import uuid

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext as _

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

from ain7.utils import LoggedClass, get_root_url
from ain7.utils import CONFIDENTIALITY_LEVELS


class Country(models.Model):
    """ Country (used for adresses)"""

    name = models.CharField(verbose_name=_('name'), max_length=50)
    nationality = models.CharField(
        verbose_name=_('nationality'),
        max_length=50,
    )

    def __unicode__(self):
        """country unicode"""
        return self.name

    class Meta:
        """country meta"""
        verbose_name = _('country')
        verbose_name_plural = _('country')
        ordering = ['name']


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
        ordering = ['decoration']


class CeremonialDuty(models.Model):
    """Honorific functions occupied by some persons"""

    ceremonial_duty = models.CharField(
        verbose_name=_('ceremonial duty'),
        max_length=200,
    )

    def __unicode__(self):
        """ceremonial duty unicode"""
        return self.ceremonial_duty

    class Meta:
        """ceremonial duty meta"""
        verbose_name = _('ceremonial duty')
        verbose_name_plural = _('ceremonial duties')
        ordering = ['ceremonial_duty']


class School(models.Model):
    """school where users come from"""

    name = models.CharField(verbose_name=_('name'), max_length=500)
    initials = models.CharField(
        verbose_name=_('initials'), max_length=20, blank=True, null=True,
    )

    line1 = models.CharField(
        verbose_name=_('line1'), max_length=50, blank=True, null=True,
    )
    line2 = models.CharField(
        verbose_name=_('line2'), max_length=100, blank=True, null=True,
    )
    zip_code = models.CharField(
        verbose_name=_('zip code'), max_length=20, blank=True, null=True,
    )
    city = models.CharField(
        verbose_name=_('city'), max_length=50, blank=True, null=True,
    )
    country = models.ForeignKey(
        Country, verbose_name=_('country'), blank=True, null=True,
    )
    phone_number = models.CharField(
        verbose_name=_('phone number'), max_length=30, blank=True, null=True,
    )
    web_site = models.CharField(
        verbose_name=_('web site'), max_length=100, blank=True, null=True,
    )
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

    name = models.CharField(verbose_name=_('track'), max_length=100)
    initials = models.CharField(
        verbose_name=_('initials'), max_length=10, blank=True, null=True,
    )
    email = models.EmailField(verbose_name=_('email'), blank=True, null=True)

    active = models.BooleanField(verbose_name=_('active'), default=True)
    school = models.ForeignKey(
        School, verbose_name=_('school'), related_name='tracks',
    )

    def __unicode__(self):
        """track unicode"""
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

    year = models.ForeignKey(
        PromoYear, verbose_name=_('Promo Year'), related_name='promosyear',
    )
    track = models.ForeignKey(
        Track, verbose_name=_('Track'), related_name='promos',
        null=True, blank=True,
    )

    def __unicode__(self):
        """promo unicode"""
        return (("%s %s") % (unicode(self.track), self.year.year))

    class Meta:
        """promo meta"""
        verbose_name = _('Promo')
        ordering = ['year', 'track']


class Person(LoggedClass):
    """The main class for a person"""

    SEX = (
        ('M', _('Male')),
        ('F', _('Female')),
    )

    MARITAL_STATUS = (
        (1, _('Maried')),
        (2, _('Single')),
        (3, _('Divorced')),
        (4, _('Concubinage')),
        (5, _('Widower')),
        (6, _('Separated')),
        (7, _('PACS')),
    )

    PROMO_YEARS = [(year,year) for year in range(1907, timezone.now().year+1)]

    # User inheritance
    user = models.OneToOneField(User, verbose_name=_('user'))

    # from the old DB
    old_id = models.IntegerField(verbose_name='old id', blank=True, null=True)

    # Civility
    last_name = models.CharField(verbose_name=_('Last name'), max_length=50)
    first_name = models.CharField(verbose_name=_('First name'), max_length=50)
    complete_name = models.CharField(
        verbose_name=_('Complete name'), max_length=50,
    )
    maiden_name = models.CharField(
        verbose_name=_('maiden name'), max_length=100, blank=True, null=True,
    )
    birth_date = models.DateField(
        verbose_name=_('Birth date'), blank=True, null=True,
    )
    sex = models.CharField(verbose_name=_('sex'), max_length=1, choices=SEX)
    nationality = models.ForeignKey(
        Country, verbose_name=_('nationality'), blank=True, null=True,
        related_name='citizens',
    )

    validated = models.BooleanField(default=True)

    mail = models.EmailField(_('mail'), unique=True, blank=True)
    mail_confidential = models.BooleanField(_('mail confidential'), default=False)
    phone = models.CharField(_('phone number'), max_length=30, blank=True)
    phone_confidential = models.BooleanField(_('phone confidential'), default=False)
    address = models.CharField(_('address'), max_length=200, blank=True)
    address_confidential = models.BooleanField(_('confidential'), default=False)
    country = models.ForeignKey('Country', blank=True, null=True)
    current_company = models.CharField(_('current company'), max_length=100, blank=True, null=True)
    
    # person_type = models.ForeignKey(PersonType, verbose_name=_('type'))
    # member_type = models.ForeignKey(MemberType, verbose_name=_('member'))
    death_date = models.DateField(_('death date'), blank=True, null=True)
    is_dead = models.BooleanField(default=False)
    notes = models.TextField(verbose_name=_('Notes'), blank=True, null=True)
    is_subscriber = models.BooleanField(default=False)
    #
    # Family situation
    #marital_status = models.ForeignKey(
    #    MaritalStatus, verbose_name=_('marital status'), blank=True, null=True
    #)
    marital_status = models.IntegerField(_('marital status'), choices=MARITAL_STATUS, blank=True, null=True)
    children_count = models.IntegerField(_('children number'), blank=True, null=True)

    # Other
    nick_name = models.CharField(
        _('Nick name'), max_length=50, blank=True, null=True,
    )
    avatar = models.ImageField(
        _('avatar'), upload_to='data/avatar',
        blank=True, null=True,
    )

    # School situation
    #promos = models.ManyToManyField(
    #    Promo, verbose_name=_('Promos'), related_name='students', blank=True,
    #)
    year = models.IntegerField(choices=PROMO_YEARS, blank=True, null=True)
    track = models.ForeignKey('Track', blank=True, null=True)

    # Civil situation
    decorations = models.ManyToManyField(
        Decoration, verbose_name=_('decorations'), blank=True,
    )
    ceremonial_duties = models.ManyToManyField(
        CeremonialDuty, verbose_name=_('ceremonial duties'), blank=True,
    )

    # Curriculum Vitae and Job Service
    receive_job_offers = models.BooleanField(
        verbose_name=_('Receive job offers by email'), default=False,
    )


    def mobile(self):
        """return mobile phone of a person if exists"""
        try:
            return self.phone_numbers.filter(type=3)[0].number
        except IndexError:
            return ''

    def phone(self):
        """return fix phone of a person if exists"""
        try:
            return self.phone_numbers.filter(type=1)[0].number
        except IndexError:
            return ''

    def mail_favorite(self, email=None):
        """return favourite e-mail"""

        if email and Email.objects.filter(
            person=self, email=email
        ).count() == 1:
            return email
        try:
            return self.emails.filter(preferred_email=True)[0].email
        except IndexError:
            return ''

    def address(self, key=None):
        """return personal address"""

        addr_perm = AddressType.objects.get(id=7)
        addr_inconnue = AddressType.objects.get(id=1)
        addr_parents = AddressType.objects.get(id=4)

        try:
            addr = Address.objects.filter(person=self)[0]
            if Address.objects.filter(person=self).count() > 1:
                if Address.objects.filter(person=self, type=addr_perm):
                    addr = Address.objects.filter(
                        person=self, type=addr_perm)[0]
                else:
                    if Address.objects.filter(person=self, type=addr_inconnue):
                        addr = Address.objects.filter(
                            person=self, type=addr_inconnue)[0]
                    else:
                        if Address.objects.filter(
                            person=self, type=addr_parents
                        ):
                            addr = Address.objects.filter(
                                person=self, type=addr_parents)[0]

            if not key:
                addr_struct = {
                    'line1': addr.line1,
                    'line2': addr.line2,
                    'zip_code': addr.zip_code,
                    'city': addr.city,
                    'country': addr.country.name,
                    'type': addr.type,
                }
                return addr_struct
            else:
                return addr_struct[key]
        except (IndexError, KeyError):
            return {}

    def __unicode__(self):
        """person unicode"""
        return self.first_name + " " + self.last_name

    def mail_from(self, email=None):
        """Get a mail from field for message"""
        mail = self.mail_favorite(email)
        mail_modified = mail.replace('@', '=')
        return u'Association AIn7 <noreply+'+mail_modified+'@ain7.com>'

    def send_mail(self, subject, message, email=None):
        """person send a mail"""

        mail = self.mail_favorite(email)
        if mail:

            msg = EmailMessage(
                subject=subject,
                body=message,
                from_email=self.mail_from(email),
                to=[self.last_name+' <'+mail+'>'],
                headers={
                    'Date': time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
                    'Sender': 'bounces@ain7.com',
                    'Presence': 'Bulk',
                    'X-Mailer': 'Python',
                    'X-Generated-By': 'AIn7 Web Portal'
                    }
            )
            msg.send()

    def password_ask(self, email=None, request=None):
        """Ask for a password reset"""

        from ain7.pages.models import LostPassword

        lostpw = LostPassword()
        lostpw.key = User.objects.make_random_password(50)
        lostpw.person = self
        lostpw.save()

        root_url = get_root_url(request)

        url = '%s%s' % (root_url, lostpw.get_absolute_url())

        self.send_mail(
            _('Password reset of your AIn7 account'),
            _("""Hi %(firstname)s,

You have requested a new password for your AIn7 account.

Your user name is: %(login)s
To reset your password, please follow this link:
%(url)s

This link will be valid 24h.

If the new password request if not from you, you can ignore this message.
--
https://ain7.com""") % {'firstname': self.first_name, 'url': url, 'login': self.user.username}, email)

    def get_absolute_url(self):
        return reverse('member-details', args=[self.id])

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
    death_date = models.DateField(
        verbose_name=_('death date'), blank=True, null=True,
    )
    notes = models.TextField(verbose_name=_('Notes'), blank=True, null=True)

    def __unicode__(self):
        """AIn7 member unicode"""
        return unicode(self.person)

    class Meta:
        """Person Private Data"""
        verbose_name = _('Person Private Data')
        ordering = ['person']


@receiver(post_save, sender=PersonPrivate)
def paste_post_save(sender, instance, created, **kwargs):

    instance.person.death_date = instance.death_date
    instance.person.notes = instance.notes
    instance.person.save()


class AIn7MemberManager(models.Manager):
    """a Manager for the class AIn7Member"""

    def pending_subscriptions(self):
        return None

    def subscribers(self):
        pt = PersonType.objects.get(id=1)
        current_year = datetime.datetime.today().year
        return self.filter(
            ain7member__person__personprivate__death_date__isnull=True,
            ain7member__subscriptions__start_year=current_year,
            personprivate__person_type=pt
        )

    def almuni(self):
        pt = PersonType.objects.get(id=1)
        current_year = datetime.datetime.today().year
        return self.filter(
            ain7member__person__personprivate__death_date__isnull=True,
            personprivate__person_type=pt,
            ain7member__promos__year__year__lte=current_year-1
        )

    def students(self):
        current_year = datetime.datetime.today().year
        return self.filter(ain7member__promos__year__year__gt=current_year-1)


class AIn7Member(LoggedClass):
    """AIn7 member"""

    person = models.OneToOneField(Person, verbose_name=_('person'))

    # Family situation
    marital_status = models.ForeignKey(
        MaritalStatus, verbose_name=_('marital status'), blank=True, null=True
    )
    children_count = models.IntegerField(
        verbose_name=_('children number'), blank=True, null=True
    )

    # Other
    nick_name = models.CharField(
        verbose_name=_('Nick name'), max_length=50, blank=True, null=True,
    )
    avatar = models.ImageField(
        verbose_name=_('avatar'), upload_to='data/avatar',
        blank=True, null=True,
    )

    # School situation
    promos = models.ManyToManyField(
        Promo, verbose_name=_('Promos'), related_name='students', blank=True,
    )

    # Civil situation
    #decorations = models.ManyToManyField(
    #    Decoration, verbose_name=_('decorations'), blank=True,
    #)
    #ceremonial_duties = models.ManyToManyField(
    #    CeremonialDuty, verbose_name=_('ceremonial duties'), blank=True,
    #)

    # Curriculum Vitae and Job Service
    receive_job_offers = models.BooleanField(
        verbose_name=_('Receive job offers by email'), default=False,
    )

    # Internal
    objects = AIn7MemberManager()

    def is_subscriber(self):
        """
        /!\ local import to avoid recursive imports
        """
        import calendar
        from ain7.adhesions.models import Subscription

        result = False
        current_year = timezone.now().date().year

        if Subscription.objects.filter(member=self).filter(
            validated=True
        ).count() > 0:
            sub = Subscription.objects.filter(member=self).filter(
                validated=True
            ).reverse()[0]

            # FIXME: still need to adapt when subscription is done after
            # October 1st, and no more student
            # We shoudl fix that before the summer :)
            if self.promo() >= current_year:
                print self.promo
                print current_year
                return True

            if sub.date:
                today = timezone.now()
                delta = today - sub.date
                days_in_year = 365
                if calendar.isleap(current_year):
                    days_in_year = 366
                result = delta.days < days_in_year

        return result


    def current_subscription(self):
        """
        local import to avoid recursive imports
        """
        from ain7.adhesions.models import Subscription

        result = None
        if Subscription.objects.filter(
            member=self,
            validated=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now(),
        ).count() > 0:
            result = Subscription.objects.filter(
                member=self,
                validated=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now(),
            ).reverse()[0]

        return result

    def current_subscription_end_date(self):

        from ain7.adhesions.models import Subscription

        if self.current_subscription() is not None:
            return self.current_subscription().end_date

    def last_subscription(self):
        """
        local import to avoid recursive imports
        """
        from ain7.adhesions.models import Subscription

        result = None
        if Subscription.objects.filter(
            member=self,
            validated=True,
        ).count() > 0:
            result = Subscription.objects.filter(
                member=self,
                validated=True,
            ).order_by('end_date').reverse()[0]

        return result

    def last_subscription_end_date(self):

        from ain7.adhesions.models import Subscription

        if self.last_subscription() is not None:
            return self.last_subscription().end_date

    def previous_subscription(self, date=None):
        """
        local import to avoid recursive imports
        """
        from ain7.adhesions.models import Subscription

        year = timezone.now().year
        if date:
            year = date.year

        result = None
        if Subscription.objects.filter(member=self, validated=True
        ).exclude(start_year__icontains=year).count() > 0:
            result = Subscription.objects.filter(
                member=self,
                validated=True,
            ).exclude(start_year__icontains=year).reverse()[0]

        return result

    def previous_subscription_date(self, date=None):
        result = self.previous_subscription(date)
        if result is not None:
            return result.date
        else:
            return None

    def previous_subscription_amount(self, date=None):
        result = self.previous_subscription(date)
        if result is not None:
            return result.dues_amount
        else:
            return None

    def has_subscription_next(self):
        from ain7.adhesions.models import Subscription

        if (
             self.current_subscription() is not None and \
             self.current_subscription_end_date() > timezone.now().date() + \
             datetime.timedelta(days=60)
            ):
            return True

        next_subscriptions = []
        if self.current_subscription() is not None:
            next_subscriptions = Subscription.objects.filter(
                member=self, validated=True,
                start_date__gte=self.current_subscription_end_date(),
            )

        if self.current_subscription() is not None and next_subscriptions.count() > 0:
            return True
        else:
            return False

    def promo(self):
        if self.promos.all():
            return self.promos.all()[0].year.year
        else:
            return 0

    def track(self):
        if self.promos.all() and self.promos.all()[0].track:
            return self.promos.all()[0].track.name
        else:
            return ''

    def promo_full(self):
        return self.track()+' '+str(self.promo())

    def current_positions(self):
        if not self.person.personprivate.death_date:
            return self.positions.filter(end__isnull=True)
        else:
            return ''

    def current_positions_orga(self):
        """return current positions"""
        res = ''
        positions = self.current_positions()
        for pos in positions:
            res += str(pos.office.organization)
            res += ' '
        return res

    def notify_expiring_membership(self):

        from ain7.adhesions.models import SubscriptionKey

        today = timezone.now().date()
        is_today = False
        if self.current_subscription() is not None and self.current_subscription_end_date() == today:
            is_today = True

        is_future = False
        if self.current_subscription() is not None and self.current_subscription_end_date() > today:
            is_future = True

        is_past = False
        if self.current_subscription() is None:
            is_past = True

        subject = u'Votre adhésion à l\'AIn7 arrive à échéance'
        if is_today:
            subject += u' aujourd\'hui!'
        if is_future:
            subject += u' le '+self.current_subscription_end_date().strftime("%d %B %Y")
        if is_past:
            subject = u'Votre adhésion à l\'AIn7 est arrivée à échéance le '+self.previous_subscription().end_date.strftime("%d %B %Y")
        html_content = render_to_string(
            'emails/notification_subscription_ending.html', {
            'person': self.person, 'is_today': is_today, 'is_future': is_future,
            'is_past': is_past, 'settings': settings,
        })
        text_content = render_to_string(
            'emails/notification_subscription_ending.txt', {
            'person': self.person, 'is_today': is_today, 'is_future': is_future,
            'is_past': is_past, 'settings': settings,
        })
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [self.person.mail_favorite()],
        )

        msg.mixed_subtype = 'related'

        for img in ['logo_ain7.png', 'facebook.png', 'linkedin.png', 'twitter.png', 'googleplus.png']:
            fp = open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates/emails/img', img), 'rb')
            msg_img = MIMEImage(fp.read())
            fp.close()
            msg_img.add_header('Content-ID', '<{}>'.format(img))
            msg.attach(msg_img)

        msg.attach_alternative(html_content, "text/html")
        msg.send()

        sub_key = SubscriptionKey(person=self.person, expire_at=timezone.now()+datetime.timedelta(days=30))
        sub_key.save()


    def __unicode__(self):
        """AIn7 member unicode"""
        return unicode(self.person)+' ('+self.promo_full()+')'

    class Meta:
        """AIn7 member meta"""
        verbose_name = _('AIn7 member')
        ordering = ['person']


@receiver(post_save, sender=AIn7Member)
def paste_post_save(sender, instance, created, **kwargs):

    instance.person.marital_status = marital_status
    instance.person.children_count = instance.children_count
    instance.person.save()


class PhoneNumber(LoggedClass):
    """Phone number for a person"""

    PHONE_NUMBER_TYPE = (
        (1, _('Fix')),
        (2, _('Fax')),
        (3, _('Mobile')),
    )

    person = models.ForeignKey(
        Person, related_name='phone_numbers', editable=False,
    )

    number = models.CharField(
        verbose_name=_('number'), max_length=30
    )
    type = models.IntegerField(
        verbose_name=_('type'), choices=PHONE_NUMBER_TYPE, default=1,
    )
    confidentiality = models.IntegerField(
        verbose_name=_('confidentiality'),
        choices=CONFIDENTIALITY_LEVELS, default=0,
    )
    confidential = models.BooleanField(
        default=False, verbose_name=_('confidential')
    )

    def __unicode__(self):
        """phone number unicode"""
        return self.number

    class Meta:
        """phone number meta"""
        verbose_name = _('phone number')


@receiver(post_save, sender=PhoneNumber)
def paste_post_save(sender, instance, created, **kwargs):

    instance.person.phone = instance.number
    instance.person.save()


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

    person = models.ForeignKey(
        Person, related_name='addresses', editable=False,
    )

    line1 = models.CharField(verbose_name=_('address line1'), max_length=50)
    line2 = models.CharField(
        verbose_name=_('address line2'), max_length=100, blank=True, null=True,
    )
    zip_code = models.CharField(verbose_name=_('zip code'), max_length=20)
    city = models.CharField(verbose_name=_('city'), max_length=50)
    country = models.ForeignKey(Country, verbose_name=_('country'))
    type = models.ForeignKey(AddressType, verbose_name=_('type'))
    confidentiality = models.IntegerField(
        verbose_name=_('confidentiality'),
        choices=CONFIDENTIALITY_LEVELS, default=0,
    )
    confidential = models.BooleanField(
        default=False, verbose_name=_('confidential')
    )
    is_valid = models.BooleanField(verbose_name=_('is valid'), default=True)

    def __unicode__(self):
        """address unicode"""
        addr = self.line1
        if self.line2:
            addr += self.line2 + " - "
        else:
            addr += " - "
        addr += self.zip_code + " " + self.city + " - "
        addr += self.country.name
        return addr

    class Meta:
        """address meta"""
        verbose_name = _('Address')


class Email(models.Model):
    """e-mail address for a person"""

    person = models.ForeignKey(Person, related_name='emails', editable=False)

    email = models.EmailField(verbose_name=_('email'), unique=True)
    confidentiality = models.IntegerField(
        verbose_name=_('confidentiality'),
        choices=CONFIDENTIALITY_LEVELS, default=0,
    )
    confidential = models.BooleanField(
        default=False, verbose_name=_('confidential')
    )
    preferred_email = models.BooleanField(
        verbose_name=_('preferred'), default=False,
    )

    position = models.ForeignKey(
        'annuaire.Position', related_name='mail', blank=True,
        null=True, editable=False,
    )

    def __unicode__(self):
        """email unicode"""
        return self.email

    def save(self):
        """ if we set "preferred" to True, then other are moved to False"""
        if self.preferred_email:
            for email in Email.objects.filter(
                person=self.person, preferred_email=True
            ):
                if email is not self:
                    email.preferred_email = False
                    email.save()
        else:
            if Email.objects.filter(
                person=self.person, preferred_email=True
            ).count() == 0:
                self.preferred_email = True
        return super(Email, self).save()

    class Meta:
        """email meta"""
        verbose_name = _('email')


@receiver(post_save, sender=Email)
def paste_post_save(sender, instance, created, **kwargs):

    if instance.preferred_email:
        instance.person.mail = instance.email
        instance.person.save()


class InstantMessaging(models.Model):
    """instant messanger contact for a person"""

    INSTANT_MESSAGING_TYPE = (
        (1, 'ICQ'),
        (2, 'MSN'),
        (3, 'AIM'),
        (4, 'Yahoo'),
        (5, 'Jabber'),
        (6, 'Gadu-Gadu'),
        (7, 'Skype'),
    )

    person = models.ForeignKey(
        Person, related_name='instant_messagings', editable=False
    )

    type = models.IntegerField(
        verbose_name=_('type'), choices=INSTANT_MESSAGING_TYPE,
    )
    identifier = models.CharField(verbose_name=_('identifier'), max_length=40)
    confidentiality = models.IntegerField(
        verbose_name=_('confidentiality'),
        choices=CONFIDENTIALITY_LEVELS, default=0,
    )
    confidential = models.BooleanField(
        default=False, verbose_name=_('confidential')
    )

    def __unicode__(self):
        """instant messenger unicode"""
        return self.identifier

    class Meta:
        """instant messanger meta"""
        verbose_name = _('instant_messaging')


class WebSite(models.Model):
    """Website for a person"""

    WEBSITE_TYPE = (
        (0, 'link'),
        (1, 'blog'),
        (2, 'gallery'),
        (3, 'linkedin'),
        (4, 'viadeo'),
        (5, 'flickr'),
        (6, 'facebook'),
        (7, 'twitter'),
        (8, 'myspace'),
        (100, 'Other'),
    )

    person = models.ForeignKey(
        Person, related_name='web_sites', editable=False,
    )

    url = models.CharField(verbose_name=_('web site'), max_length=100)
    type = models.IntegerField(verbose_name=_('type'), choices=WEBSITE_TYPE)
    confidentiality = models.IntegerField(
        verbose_name=_('confidentiality'),
        choices=CONFIDENTIALITY_LEVELS, default=0,
    )
    confidential = models.BooleanField(
        default=False, verbose_name=_('confidential')
    )
    blog_is_agregated_on_planet = models.BooleanField(
        verbose_name=_('blog on planet'), default=False,
    )

    def __unicode__(self):
        """website unicode"""
        return self.url

    def save(self):
        """website save"""
        if (
            not self.url.startswith('http://')
            and not
            self.url.startswith('https://')
        ):
            self.url = 'http://'+self.url
        return super(WebSite, self).save()

    class Meta:
        """website meta"""
        verbose_name = _('web site')


class Club(LoggedClass):
    """N7 club"""

    name = models.CharField(verbose_name=('name'), max_length=20)
    description = models.CharField(
        verbose_name=_('description'), max_length=100,
    )
    web_site = models.URLField(
        verbose_name=_('web site'), max_length=50, blank=True, null=True,
    )
    email = models.EmailField(
        verbose_name=_('email'), max_length=50, blank=True, null=True,
    )
    school = models.ForeignKey(
        School, verbose_name=_('school'), related_name='clubs',
    )
    icon = models.ImageField(
        verbose_name=_('icon'), upload_to='data/', blank=True, null=True,
    )

    end_date = models.DateField(
        verbose_name=_('end date'), blank=True, null=True,
    )

    def __unicode__(self):
        """club unicode"""
        return self.name

    class Meta:
        """club meta"""
        verbose_name = _('club')


class ClubMembership(models.Model):
    """Club membership for a person"""

    club = models.ForeignKey(
        'annuaire.Club', verbose_name=_('club'), related_name='memberships',
    )
    member = models.ForeignKey(
        Person, verbose_name=_('member'),
        related_name='club_memberships', editable=False,
    )

    fonction = models.CharField(
        verbose_name=_('fonction'), max_length=50, blank=True, null=True,
    )
    begin = models.IntegerField(
        verbose_name=_('start date'), blank=True, null=True,
    )
    end = models.IntegerField(
        verbose_name=_('end date'), blank=True, null=True,
    )

    def __unicode__(self):
        """club membership unicode"""
        return str(self.club) + " " + self.fonction

    class Meta:
        """club membership meta"""
        verbose_name = _('club membership')
        verbose_name_plural = _('club memberships')
        ordering = ['begin']


class Position(LoggedClass):
    """
    A position occupied by a person.
    """

    ain7member = models.ForeignKey(
        'annuaire.Person', related_name='positions'
    )
    office = models.ForeignKey(
        'organizations.Office', verbose_name=_('office'),
        related_name='positions',
    )

    fonction = models.CharField(
        verbose_name=_('fonction'), max_length=80, blank=True, null=True
    )
    service = models.CharField(
        verbose_name=_('service'), max_length=80, blank=True, null=True
    )
    phone_number = models.CharField(
        verbose_name=_('phone'), max_length=20, blank=True, null=True
    )
    is_regie = models.BooleanField(
        verbose_name=_('regie outside'), default=False
    )
    begin = models.IntegerField(
        verbose_name=_('startyear'), blank=True, null=True
    )
    end = models.IntegerField(
        verbose_name=_('end year'), blank=True, null=True
    )

    description = models.TextField(
        verbose_name=_('description'), blank=True, null=True
    )

    def __unicode__(self):
        """position unicode"""
        description = ''
        if self.fonction:
            description += self.fonction
        description += " " + unicode(self.office)
        description += " (" + unicode(self.office.organization) + ")"
        return description

    class Meta:
        """position meta"""
        verbose_name = _('position')
        ordering = ['-begin']


class EducationItem(LoggedClass):
    """ An education item in the CV of a person."""

    ain7member = models.ForeignKey(
        'annuaire.Person', related_name='education',
    )
    school = models.CharField(
        verbose_name=_('school'), max_length=150, blank=True, null=True
    )
    diploma = models.CharField(
        verbose_name=_('diploma'), max_length=150, blank=True, null=True
    )
    details = models.TextField(
        verbose_name=_('description'), blank=True, null=True
    )
    begin = models.IntegerField(
        verbose_name=_('start year'), blank=True, null=True
    )
    end = models.IntegerField(
        verbose_name=_('end year'), blank=True, null=True
    )

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
    ain7member = models.ForeignKey(
        'annuaire.Person', related_name='leisure'
    )

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
    ain7member = models.ForeignKey(
        'annuaire.Person',  related_name='publication'
    )

    def __unicode__(self):
        """publication item unicode"""
        return self.title

    class Meta:
        """publication item meta"""
        verbose_name = _('Publication and patent')


class UserActivity(models.Model):
    """user activity"""

    person = models.ForeignKey('annuaire.Person', null=False)
    date = models.DateTimeField(verbose_name=_('start date'), null=False)
    client_host = models.CharField(max_length=256, blank=True, null=True)
    browser_info = models.TextField(null=True, blank=True)

    class Meta:
        """user activity meta"""
        verbose_name = _('user activity')
        verbose_name_plural = _('users activities')
        ordering = ['date']


class ProfileEditKey(models.Model):

    person = models.ForeignKey('annuaire.Person', null=False)
    key = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    expire_at = models.DateTimeField(editable=False)
