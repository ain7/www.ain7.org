# -*- coding: utf-8
#
# adhesions/models.py
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

from django.db import models
from django.utils.translation import ugettext as _

from ain7.utils import LoggedClass
from ain7.annuaire.models import AIn7Member

class Subscription(LoggedClass):

    MODE = (
            ('CASH', _('Cash')),
            ('CHEQUE', _('Cheque')),
            #('CARD', _('Card')),
            )

    dues_amount = models.IntegerField(verbose_name=_('Dues amount'))
    newspaper_amount = models.IntegerField(verbose_name=_('Newspaper amount'), null=True, blank=True)
    validated = models.BooleanField(verbose_name=_('validated'), default=False)

    year = models.IntegerField(verbose_name=_('year'))

    member = models.ForeignKey(AIn7Member, verbose_name=_('member'), related_name='subscriptions')

    def __unicode__(self):
        return u'%s %s' % (self.member, self.year)
