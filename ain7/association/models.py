# -*- coding: utf-8
"""
 ain7/association/models.py
"""
#
#   Copyright © 2007-2009 AIn7 Devel Team
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


class CouncilRole(models.Model):
    """Council Role"""

    COUNCIL_ROLE = (
                       (0, _('President')),
                       (1, _('Vice president')),
                       (2, _('Secretary')),
                       (3, _('Treasurer')),
                       (4, _('Secretary Assistant')),
                       (5, _('Treasurer Assistant')),
                       (10, _('Council Member')),
                       (15, _('Regional Group Representative')),
                    )

    role = models.IntegerField(verbose_name=_('type'), choices=COUNCIL_ROLE)
    member = models.ForeignKey(Person, verbose_name=_('member'),
        related_name='council_roles')
    start_date = models.DateField(verbose_name=_('start date'),
        default=datetime.datetime.now, blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'),
        blank=True, null=True)
    board_member = models.BooleanField()

    def __unicode__(self):
        """council role unicode"""
        return [ nam for role, nam in self.COUNCIL_ROLE if role == self.role ][0]

    def current(self):
        """is role a current role"""
        return self.start_date <= datetime.datetime.now().date() and \
            not(self.end_date and \
                self.end_date <= datetime.datetime.now().date())

    class Meta:
        """council meta"""
        verbose_name = _('council role')
        verbose_name_plural = _('council roles')
        ordering = ['role', 'member']

