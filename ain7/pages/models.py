# -*- coding: utf-8
"""
 ain7/pages/models.py
"""
#
#   Copyright © 2007-2017 AIn7 Devel Team
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
from django.db.models import permalink
from django.utils import timezone
from django.utils.translation import ugettext as _

from ain7.utils import LoggedClass


class TextBlock(LoggedClass):
    """Text Block"""
    shortname = models.CharField(verbose_name=_('shortname'), max_length=50)
    url = models.CharField(
        verbose_name=_('url'), max_length=100, blank=True, null=True,
    )

    def get_absolute_url(self):
        """text block url"""
        if self.url:
            return self.url
        else:
            return None

    def __unicode__(self):
        """unicode string for test blocks"""
        return self.shortname


class Text(LoggedClass):
    """Text"""

    textblock = models.ForeignKey(TextBlock)
    lang = models.CharField(
        verbose_name=_('lang'), default='fr', max_length=10,
    )
    title = models.CharField(verbose_name=_('title'), max_length=150)
    body = models.TextField(verbose_name=_('body'), blank=True, null=True)

    def get_absolute_url(self):
        """ return the URL of the page"""
        return self.textblock.url


class LostPassword(models.Model):
    """store lost password information"""
    person = models.ForeignKey('annuaire.Person')
    key = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'Lost password for %s dated of %s' % \
            (self.person, self.created.date())

    @permalink
    def get_absolute_url(self):
        """ return the URL used to change the password """
        return ('resetpassword', (self.key,))

    def is_expired(self):
        """
            Return True is lostpassword is expired (ie have more than 24 hour)
        """
        return (timezone.now() - self.created) > datetime.timedelta(hours=24)
