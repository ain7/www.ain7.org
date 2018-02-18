# -*- coding: utf-8
"""
 ain7/voyages/models.py
"""
#
#   Copyright © 2007-2018 AIn7 Devel Team
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
from ain7.utils import LoggedClass


class TravelType(models.Model):
    """Travel Type"""

    type = models.CharField(verbose_name=_('type'), max_length=50)

    def __unicode__(self):
        """travel type unicode"""
        return self.type

    class Meta:
        """travel type meta"""
        verbose_name = _('travel type')
        verbose_name_plural = _('travel types')

class Travel(LoggedClass):
    """Travel"""

    label = models.CharField(verbose_name=_('label'), max_length=50)
    start_date = models.DateField(verbose_name=_('start date'),
         blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'),
          blank=True, null=True)
    type = models.ForeignKey(TravelType, verbose_name=_('type'))
    description = models.TextField(verbose_name=_('description'),
           blank=True, null=True)
    price = models.IntegerField(verbose_name=_('price'), blank=True, null=True)
    thumbnail = models.ImageField(verbose_name=_('thumbnail'), upload_to='data',
           blank=True, null=True)
    report = models.TextField(verbose_name=_('report'), blank=True, null=True)

    def __unicode__(self):
        """travel unicode"""
        return self.label

    def is_past(self):
        """ Defines if a travel is past or not."""
        return self in Travel.objects.filter(
            start_date__lt=datetime.datetime.now())

    def nb_participants(self):
        """ Returns how many participants are registered for this travel."""
        value = Subscription.objects.filter(travel=self)\
                .values('subscriber_number')\
                .extra(select={'sum': 'sum(subscriber_number)'})
        if len(value) > 0:
            return value[0]['subscriber_number']
        else:
            return 0

    def get_absolute_url(self):
        """travel absolute url"""
        return reverse('travel-details', args=[self.id])

    class Meta:
        """travel meta"""
        verbose_name = _('travel')
        ordering = ['-start_date', '-end_date']
