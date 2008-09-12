# -*- coding: utf-8
#
# groupes_professionnels/models.py
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
from ain7.utils import LoggedClass

class GroupPro(LoggedClass):

    name = models.CharField(verbose_name=_('name'), max_length=30, unique=True, blank=False)
    description = models.CharField(verbose_name=_('description'), max_length=200, blank=True, null=True)
    contact = models.EmailField(verbose_name=_('Contact email'), max_length=100, blank=True, null=True)
    web_page = models.TextField(verbose_name=_('web page'), blank=True, null=True)
    link = models.CharField(verbose_name=_('link'), max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def has_for_member(self, person):
        return self.memberships.filter(member=person)\
            .exclude(end_date__isnull=False, end_date__lte=datetime.datetime.now())\
            .filter(start_date__lte=datetime.datetime.now())\
            .count() != 0

    def current_memberships(self):
        return [ ms for ms in self.memberships.all() if ms.current() ]

    def current_roles(self):
        return [ rol for rol in self.roles.all() if rol.current() ]

    class Meta:
        verbose_name=_('group')

class Membership(models.Model):

    group = models.ForeignKey(GroupPro, verbose_name=_('group'), related_name='memberships')
    member = models.ForeignKey(Person, verbose_name=_('member'), related_name='group_memberships')

    start_date = models.DateField(verbose_name=_('start date'), default=datetime.datetime.now, blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)

    def current(self):
        return self.start_date <= datetime.datetime.now().date() and \
            not(self.end_date and \
                self.end_date <= datetime.datetime.now().date())

    class Meta:
        verbose_name = _('membership')


class GroupProRole(models.Model):

    ROLE_TYPE = (
                       (0, _('Responsible')),
                       (1, _('Animator')),
                       )

    type = models.IntegerField(verbose_name=_('type'), choices=ROLE_TYPE)
    start_date = models.DateField(verbose_name=_('start date'), default=datetime.datetime.now, blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)

    group = models.ForeignKey(GroupPro, verbose_name=_('professional group'), related_name='roles')
    member = models.ForeignKey(Person, verbose_name=_('member'), related_name='professional_group_roles')

    def __unicode__(self):
        typ = None
        for type, typename in self.ROLE_TYPE:
            if type==self.type: typ = typename
        return typ

    def current(self):
        return self.start_date <= datetime.datetime.now().date() and \
            not(self.end_date and \
                self.end_date <= datetime.datetime.now().date())

    class Meta:
        ordering = ['type', 'start_date', 'end_date']
        verbose_name = _('professional group role')
        verbose_name_plural = _('professional group roles')

