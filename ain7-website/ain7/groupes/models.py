# -*- coding: utf-8
#
# groupes/models.py
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

class Group(models.Model):

    name = models.CharField(verbose_name=_('name'), max_length=100)
    contact = models.EmailField(verbose_name=_('Contact email'), max_length=100, blank=True, null=True)
    description = models.CharField(verbose_name=_('description'), max_length=200, blank=True, null=True)
    web_page = models.TextField(verbose_name=_('web page'), blank=True, null=True)
    parent = models.ForeignKey('Group', verbose_name=_('parent'), related_name='children', blank=True, null=True)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)
    modifier = models.IntegerField(editable=False)

    def __unicode__(self):
        return self.name

    def save(self):
        self.modification_date = datetime.datetime.today()
        self.modifier = 1
        return super(Group, self).save()

    class Meta:
        verbose_name=_('group')

class Membership(models.Model):

    is_coordinator = models.BooleanField(verbose_name=_('coordinator'), default=False)

    group = models.ForeignKey(Group, verbose_name=_('group'), related_name='memberships')
    member = models.ForeignKey(Person, verbose_name=_('member'), related_name='group_memberships')

    start_date = models.DateField(verbose_name=_('start date'), default=datetime.datetime.now, blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)

    class Meta:
        verbose_name = _('membership')
