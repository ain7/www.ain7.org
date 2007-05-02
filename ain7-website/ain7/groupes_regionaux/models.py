# -*- coding: utf-8
#
# groupes_regionaux/models.py
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

    name = models.CharField(verbose_name=_('name'), maxlength=50)

    def __str__(self):
        return self.name

    class Admin:
        pass

    class Meta:
        verbose_name = _('regional group')
        verbose_name_plural = _('regional groups')


class GroupMembership(models.Model):

    MEMBERSHIP_TYPE = (
                       (0, 'Administrator'),
                       (1, 'President'),
                       (2, 'Office member'),
                       (3, 'Member')
                       )

    type = models.IntegerField(verbose_name=_('type'), choices=MEMBERSHIP_TYPE, core=True)
    start_date = models.DateField(verbose_name=_('start date'), default=datetime.datetime.now, blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)

    group = models.ForeignKey(Group, verbose_name=_('regional group'), related_name='memberships', edit_inline=models.TABULAR, num_in_admin=2)
    member = models.ForeignKey(Person, verbose_name=_('member'), related_name='regional_group_memberships', core=True)

    class Meta:
        verbose_name = _('regional group membership')
        verbose_name_plural = _('regional group memberships')
