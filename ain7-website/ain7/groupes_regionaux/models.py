# -*- coding: utf-8
#
# groupes_regionaux/models.py
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

    is_active = models.BooleanField(verbose_name=_('active'), default=True)
    name = models.CharField(verbose_name=_('name'), max_length=50)
    description = models.TextField(verbose_name=_('description'), blank=True, null=True)

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

    def office_memberships(self):
        return self.roles.exclude(end_date__isnull=False, end_date__lte=datetime.datetime.now())\
                                .filter(start_date__lte=datetime.datetime.now())

    def active_events(self):
        return self.events.filter(publication_start__lte=datetime.datetime.now(), publication_end__gte=datetime.datetime.now())

    def has_for_member(self, person):
        return self.memberships.filter(member=person)\
            .exclude(end_date__isnull=False, end_date__lte=datetime.datetime.now())\
            .filter(start_date__lte=datetime.datetime.now())\
            .count() != 0

    def has_for_office_member(self, person):
        has_role = False
        for role in self.roles.filter(member=person)\
            .filter(start_date__lte=datetime.datetime.now()):
            if not role.end_date or role.end_date > datetime.datetime.now():
                has_role = True
        return has_role

    class Meta:
        verbose_name = _('regional group')
        verbose_name_plural = _('regional groups')

class GroupMembership(models.Model):

    start_date = models.DateField(verbose_name=_('start date'), default=datetime.datetime.now, blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)

    group = models.ForeignKey(Group, verbose_name=_('regional group'), related_name='memberships')
    member = models.ForeignKey(Person, verbose_name=_('member'), related_name='regional_group_memberships')

    class Meta:
        ordering = ['start_date', 'end_date']
        verbose_name = _('regional group membership')
        verbose_name_plural = _('regional group memberships')

class GroupRole(models.Model):

    ROLE_TYPE = (
                       (0, _('President')),
                       (1, _('Vice president')),
                       (2, _('Secretary')),
                       (3, _('Treasurer')),
                       (4, _('Under treasurer')),
                       (5, _('Emploi manager')),
                       (6, _('Office member')),
                       )

    type = models.IntegerField(verbose_name=_('type'), choices=ROLE_TYPE)
    start_date = models.DateField(verbose_name=_('start date'), default=datetime.datetime.now, blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)

    group = models.ForeignKey(Group, verbose_name=_('regional group'), related_name='roles')
    member = models.ForeignKey(Person, verbose_name=_('member'), related_name='regional_group_roles')

    def __unicode__(self):
        typ = None
        for type, typename in self.ROLE_TYPE:
            if type==self.type: typ = typename
        return typ + ' : ' + str(self.member)

    class Meta:
        ordering = ['type', 'start_date', 'end_date']
        verbose_name = _('regional group role')
        verbose_name_plural = _('regional group roles')
