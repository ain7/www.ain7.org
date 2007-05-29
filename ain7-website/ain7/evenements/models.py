# -*- coding: utf-8
#
# evenements/models.py
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
from django.utils.translation import gettext_lazy as _

from ain7.annuaire.models import Person
from ain7.groupes_regionaux.models import Group

class Event(models.Model):

    name = models.CharField(verbose_name=_('name'), maxlength=20)
    start_date = models.DateField(verbose_name=_('start date'))
    end_date = models.DateField(verbose_name=_('end date'))
    description = models.TextField(verbose_name=_('description'), blank=True, null=True)
    author = models.CharField(verbose_name=_('author'), maxlength=20)
    contact_email = models.EmailField(verbose_name=_('contact email'), maxlength=50)
    link = models.CharField(verbose_name=_('link'), maxlength=60, blank=True, null=True)
    place = models.CharField(verbose_name=_('place'), maxlength=60)
    publication_start =  models.DateTimeField(verbose_name=_('publication start'))
    publication_end = models.DateTimeField(verbose_name=_('publication end'))

    regional_groups = models.ManyToManyField(Group, verbose_name=_('regional groups'), related_name='events', blank=True, null=True, filter_interface=models.HORIZONTAL)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)
    #creator = models.ForeignKey(Person, related_name='created_events', editable=False)
    #modifier = models.ForeignKey(Person, related_name='modified_events', editable=False)

    def __str__(self):
        return self.name

    def save(self):
        #self.creator = 1
        self.modification_date = datetime.datetime.today()
        #self.modifier = 1
        return super(Event, self).save()

    def get_absolute_url(self):
        return '/evenements/'+str(self.id)+'/'

    class Admin:
        pass

    class Meta:
        ordering = ['start_date', 'end_date', 'publication_start', 'publication_end']
        verbose_name = _('event')

class EventSubscription(models.Model):

    subscriber_number = models.IntegerField(verbose_name=_('subscriber number'), core=True)

    subscription_date = models.DateTimeField(default=datetime.datetime.now, editable=False)

    subscriber = models.ForeignKey(Person, verbose_name=_('subscriber'), related_name='event_subscriptions')
    event = models.ForeignKey(Event, verbose_name=_('event'), related_name='subscriptions', edit_inline=models.TABULAR, num_in_admin=1)

    class Meta:
        verbose_name = _('event subscription')
        verbose_name_plural = _('event subscriptions')
