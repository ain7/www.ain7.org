# -*- coding: utf-8
#
# voyages/models.py
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

class TravelType(models.Model):
    
    type = models.CharField(verbose_name=_('type'), maxlength=50)

    def __str__(self):
        return self.type

    class Admin:
        pass

    class Meta:
        verbose_name = _('travel type')
        verbose_name_plural = _('travel types')

class Travel(models.Model):

    label = models.CharField(verbose_name=_('label'), maxlength=20)
    start_date = models.DateField(verbose_name=_('start date'), blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)
    date = models.CharField(verbose_name=_('date'), maxlength=30)
    term = models.IntegerField(verbose_name=_('term'), default=0, blank=True, null=True)
    type = models.ForeignKey(TravelType, verbose_name=_('type'))
    visited_places = models.CharField(verbose_name=_('visited places'), maxlength=100)
    description = models.TextField(verbose_name=_('description'), blank=True, null=True)
    price = models.IntegerField(verbose_name=_('price'), blank=True, null=True)
    thumbnail = models.ImageField(verbose_name=_('thumbnail'), upload_to='data',blank=True,null=True)
    report = models.TextField(verbose_name=_('report'), blank=True, null=True)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)

    def __str__(self):
        return self.label

    def save(self):
        self.modification_date = datetime.datetime.today()
        return super(Travel, self).save()

    class Admin:
        pass
    
    class Meta:
        verbose_name = _('travel')
        ordering = ['start_date', 'end_date']

class Subscription(models.Model):

    subscriber_number = models.IntegerField(verbose_name=_('subscriber number'), default=1, core=True)
    comment = models.TextField(verbose_name=_('comment'), blank=True, null=True)

    subscription_date = models.DateTimeField(default=datetime.datetime.now, editable=False)

    subscriber = models.ForeignKey(Person, verbose_name=_('subscriber'), related_name='travel_subscriptions')
    travel = models.ForeignKey(Travel, verbose_name=_('event'), related_name='subscriptions', edit_inline=models.TABULAR, num_in_admin=1)

    class Meta:
        verbose_name = _('travel subscription')
        verbose_name_plural = _('travel subscriptions')

# indicates who is responsible for a travel
class TravelResponsible(models.Model):
    
    travel = models.ForeignKey(Travel, verbose_name=_('travel'), related_name='travel_responsibles')
    responsible = models.ForeignKey(Person, verbose_name=_('responsible'), related_name='travel_responsibilities')

    class Meta:
        verbose_name = _('travel responsible')
        verbose_name_plural = _('travel responsibles')


