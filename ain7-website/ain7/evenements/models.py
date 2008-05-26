# -*- coding: utf-8
#
# evenements/models.py
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

from ain7.annuaire.models import Person
from ain7.groupes_regionaux.models import Group

# a Manager for the class Event
class EventManager(models.Manager):

    def next_events(self):
        """Returns all future events."""
        return self.filter(end__gte=datetime.datetime.now())

class Event(models.Model):

    EVENT_CATEGORY = (
              (0,_('conference')),
              (1,_('feistivity')),
              (2,_('Administration Council')),
              (3,_('General Assembly')),
              )

    EVENT_STATUS = (
              (0,_('tentative')),
              (0,_('confirmed')),
              (0,_('cancel')),
              )

    name = models.CharField(verbose_name=_('name'), max_length=20)
    start = models.DateTimeField(verbose_name=_('start'))
    end = models.DateTimeField(verbose_name=_('end'))
    description = models.TextField(verbose_name=_('description'), blank=True, null=True)
    location = models.CharField(verbose_name=_('place'), max_length=60)
    category = models.IntegerField(verbose_name=_('category'), choices=EVENT_CATEGORY, null=True, blank=True)
    status = models.IntegerField(verbose_name=_('status'), choices=EVENT_STATUS, null=True, blank=True)
    image = models.ImageField(verbose_name=_('image'), upload_to='data', null=True, blank=True)
    author = models.CharField(verbose_name=_('author'), max_length=20)
    contact_email = models.EmailField(verbose_name=_('contact email'), max_length=50)
    link = models.CharField(verbose_name=_('link'), max_length=60, blank=True, null=True)
    publication_start =  models.DateTimeField(verbose_name=_('publication start'))
    publication_end = models.DateTimeField(verbose_name=_('publication end'))

    organizer = models.ManyToManyField(Person, verbose_name=_('organizer'),related_name='events', blank=True, null=True, filter_interface=models.HORIZONTAL)
    regional_groups = models.ManyToManyField(Group, verbose_name=_('regional groups'), related_name='events', blank=True, null=True, filter_interface=models.HORIZONTAL)
    pictures_gallery = models.CharField(verbose_name=_('Pictures gallery'), max_length=100, blank=True, null=True)
    question = models.TextField(null=True, blank=True)
    objects = EventManager()

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)
    creator = models.ForeignKey(Person, related_name='created_events', editable=False, null=True)
    modifier = models.ForeignKey(Person, related_name='modified_events', editable=False, null=True)

    # Moderation
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(Person, related_name='events_approved', editable=False, null=True)

    def __unicode__(self):
        return self.name

    def save(self):
        #self.creator = 1
        self.modification_date = datetime.datetime.today()
        #self.modifier = 1
        if self.pictures_gallery:
            if not self.pictures_gallery.startswith('http://'):
                self.pictures_gallery = 'http://'+self.pictures_gallery
        return super(Event, self).save()

    # TODO: ca sert à quoi ?
    def get_absolute_url(self):
        return '/evenements/'+str(self.id)+'/'

    def nb_participants(self):
        """Renvoie le nombre de participants à l'événement."""
        nbpart = 0
        for sub in self.subscriptions.all(): nbpart += sub.subscriber_number
        return nbpart

    class Admin:
        pass

    class Meta:
        ordering = ['start', 'end', 'publication_start', 'publication_end']
        verbose_name = _('event')

class EventSubscription(models.Model):

    subscriber = models.ForeignKey(Person, verbose_name=_('subscriber'), related_name='event_subscriptions')
    event = models.ForeignKey(Event, verbose_name=_('event'), related_name='subscriptions', edit_inline=models.TABULAR, num_in_admin=1)
    subscriber_number = models.IntegerField(verbose_name=_('subscriber number'), core=True)
    note = models.TextField(null=True, blank=True)

    subscription_date = models.DateTimeField(default=datetime.datetime.now, editable=False)
    subscribed_by = models.ForeignKey(Person, related_name='subscriptions_done', editable=False, null=True)

    class Admin:
        pass

    class Meta:
        verbose_name = _('event subscription')
        verbose_name_plural = _('event subscriptions')

