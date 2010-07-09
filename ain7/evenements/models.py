# -*- coding: utf-8
"""
 ain7/evenements/models.py
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

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person
from ain7.groupes_regionaux.models import Group
from ain7.groupes_professionnels.models import GroupPro
from ain7.utils import LoggedClass


# a Manager for the class Event
class EventManager(models.Manager):
    """event manager"""

    def next_events(self):
        """Returns all future events."""
        return self.filter(date__gte=datetime.datetime.now())

class Event(LoggedClass):
    """event"""

    EVENT_STATUS = (
              (0,_('project')),
              (1,_('confirmed')),
              (2,_('cancel')),
              )

    # general fields
    slug = models.SlugField(max_length=100, blank=True, null=True)
    title = models.CharField(verbose_name=_('title'), max_length=100)
    body = models.TextField(verbose_name=_('body'),
        blank=True, null=True)
    shorttext = models.CharField(verbose_name=_('short text'), max_length=500,
        blank=True, null=True)
    image = models.ImageField(verbose_name=_('image'), upload_to='data',
        blank=True, null=True)

    # to which group we should link this news
    regional_groups = models.ManyToManyField(Group,
         verbose_name=_('regional groups'), related_name='events',
         blank=True, null=True)
    professional_groups = models.ManyToManyField(GroupPro,
         verbose_name=_('professional groups'), related_name='events',
         blank=True, null=True)

    # those fields are only present for an event
    date = models.DateTimeField(verbose_name=_('date'))
    location = models.CharField(verbose_name=_('location'), max_length=60)
    status = models.IntegerField(verbose_name=_('status'), choices=EVENT_STATUS,
        blank=True, null=True)
    contact_email = models.EmailField(verbose_name=_('contact email'),
        max_length=50)

    link = models.CharField(verbose_name=_('external link'), max_length=60, blank=True,
        null=True)

    organizers = models.ManyToManyField(Person, verbose_name=_('organizers'), 
         related_name='events', blank=True, null=True, through='EventOrganizer')
    pictures_gallery = models.CharField(verbose_name=_('Pictures gallery'),
         max_length=100, blank=True, null=True)
    objects = EventManager()

    def __unicode__(self):
        """event unicode"""
        return self.name

    def save(self):
        """save event"""
        if self.pictures_gallery:
            if not self.pictures_gallery.startswith('http://'):
                self.pictures_gallery = 'http://'+self.pictures_gallery
        return super(Event, self).save()

    def get_absolute_url(self):
        """event url"""
        return reverse('ain7.evenements.views.details', args=[self.id])

    def nb_participants(self):
        """Renvoie le nombre de participants à l'événement."""
        nbpart = 0
        for sub in self.subscriptions.all():
            nbpart += sub.subscriber_number
        return nbpart

    class Meta:
        """event meta"""
        ordering = ['date']
        verbose_name = _('event')

class EventSubscription(models.Model):
    """Event Subscription"""

    subscriber = models.ForeignKey(Person, verbose_name=_('subscriber'),
        related_name='event_subscriptions')
    event = models.ForeignKey(Event, verbose_name=_('event'),
        related_name='subscriptions')
    subscriber_number = models.IntegerField(verbose_name=_('subscriber number'))
    note = models.TextField(null=True, blank=True)

    subscription_date = models.DateTimeField(default=datetime.datetime.now,
        editable=False)
    subscribed_by = models.ForeignKey(Person, related_name='subscriptions_done',
        editable=False, null=True)

    class Meta:
        """event subscription meta"""
        verbose_name = _('event subscription')
        verbose_name_plural = _('event subscriptions')

    def save(self):
        """event subscription save"""
        evt_sub = super(EventSubscription, self).save()
        # if some organizers want to get informed by email, do it
        msg  = _('subscriber').capitalize()+' : '+unicode(self.subscriber) \
               + ' (' + unicode(self.subscriber_number) + ' ' \
               + _('subscribers in total') + ')\n\n' \
               + _('notes').capitalize() + '\n' \
               + self.note + '\n\n' \
               + _('subscribed by') + ' ' + unicode(self.subscribed_by) + ' ' \
               + _('the') + ' ' \
               + self.subscription_date.strftime('%d/%m/%Y') + ' ' \
               + _('at') + ' ' \
               + self.subscription_date.strftime('%H:%M')
        for event_organizer in self.event.event_organizers.all():
            if event_organizer.send_email_for_new_subscriptions:
                event_organizer.organizer.send_mail(
                    subject=_('New subscription for')+' : '+unicode(self.event),
                    message=msg)
        return evt_sub

class EventOrganizer(models.Model):
    """event organizer"""

    event = models.ForeignKey(Event, verbose_name=_('event'),
        related_name='event_organizers')
    organizer = models.ForeignKey(Person, verbose_name=_('organizer'),
        related_name='organized_events')
    send_email_for_new_subscriptions = models.BooleanField(default=False,
            verbose_name=_('send email for new subscription'))

