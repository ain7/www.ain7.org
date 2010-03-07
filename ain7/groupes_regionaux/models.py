# -*- coding: utf-8
"""
 ain7/groupes_regionaux/models.py
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
from ain7.utils import LoggedClass


class Group(LoggedClass):
    """Regional Group"""

    is_active = models.BooleanField(verbose_name=_('active'), default=True)
    shortname = models.CharField(verbose_name=_('name'), max_length=50,
        unique=True)
    name = models.CharField(verbose_name=_('name'), max_length=50)
    description = models.TextField(verbose_name=_('description'), blank=True,
        null=True)

    def __unicode__(self):
        """unicode string for a regional group"""
        return self.name

    def office_memberships(self):
        """board membership"""
        return self.roles.exclude(end_date__isnull=False, 
            end_date__lte=datetime.datetime.now())\
            .filter(start_date__lte=datetime.datetime.now())

    def active_events(self):
        """current events for a regional group"""
        return self.events.filter(publication_start__lte=\
            datetime.datetime.now(), publication_end__gte=\
            datetime.datetime.now())

    def has_for_member(self, person):
        """check membership for a regional group"""
        return self.memberships.filter(member=person)\
            .exclude(end_date__isnull=False, end_date__lte=\
            datetime.datetime.now())\
            .filter(start_date__lte=datetime.datetime.now())\
            .count() != 0

    def has_for_board_member(self, person):
        """check board member for a regional group"""
        has_role = False
        for role in self.roles.filter(member=person)\
            .filter(start_date__lte=datetime.datetime.now()):
            if not role.end_date or role.end_date > datetime.datetime.now():
                has_role = True
        return has_role

    def get_absolute_url(self):
        """absolute url for regional group"""
        return reverse('ain7.groupes_regionaux.views.details', args=[self.id])

    class Meta:
        """regional group meta"""
        verbose_name = _('regional group')
        verbose_name_plural = _('regional groups')

class GroupMembership(models.Model):
    """group membership"""

    start_date = models.DateField(verbose_name=_('start date'),
        default=datetime.datetime.now, blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)

    group = models.ForeignKey(Group, verbose_name=_('regional group'),
        related_name='memberships')
    member = models.ForeignKey(Person, verbose_name=_('member'),
        related_name='regional_group_memberships')

    class Meta:
        """group membership meta information"""
        ordering = ['start_date', 'end_date']
        verbose_name = _('regional group membership')
        verbose_name_plural = _('regional group memberships')

class GroupRole(models.Model):
    """Group role"""

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
    start_date = models.DateField(verbose_name=_('start date'),
        default=datetime.datetime.now, blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)

    group = models.ForeignKey(Group, verbose_name=_('regional group'),
        related_name='roles')
    member = models.ForeignKey(Person, verbose_name=_('member'),
        related_name='regional_group_roles')

    def __unicode__(self):
        """regional group role unicode"""
        typ = None
        for type, typename in self.ROLE_TYPE:
            if type == self.type:
                typ = typename
        return typ + ' : ' + str(self.member)

    class Meta:
        """regional group role meta"""
        ordering = ['type', 'start_date', 'end_date']
        verbose_name = _('regional group role')
        verbose_name_plural = _('regional group roles')

