# -*- coding: utf-8
#
# models.py
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

class Group(models.Model):

    name = models.CharField(verbose_name=_('name'), maxlength=100)
    contact = models.CharField(verbose_name=_('Contact'), maxlength=100, blank=True, null=True)
    description = models.CharField(verbose_name=_('description'), maxlength=200, blank=True, null=True)
    web_page = models.TextField(verbose_name=_('web page'), blank=True, null=True)
    parent = models.ForeignKey('Group', verbose_name=_('parent'), related_name='children', blank=True, null=True)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)
    modifier = models.IntegerField(editable=False)

    def __str__(self):
        return self.name

    def save(self):
        self.modification_date = datetime.datetime.today()
        self.modifier = 1
        return super(Group, self).save()

    class Admin:
        list_display = ('name', 'description')
        list_filter = ['name']
        search_fields = ['name']

    class Meta:
        verbose_name=_('group')

class Membership(models.Model):

    is_administrator = models.BooleanField(verbose_name=_('administrator'), default=False)

    group = models.ForeignKey(Group, verbose_name=_('group'), related_name='memberships', edit_inline=models.TABULAR, num_in_admin=1)
    member = models.ForeignKey(Person, verbose_name=_('member'), related_name='group_memberships', core=True)

    class Meta:
        verbose_name = _('membership')
