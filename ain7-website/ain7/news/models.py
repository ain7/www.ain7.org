# -*- coding: utf-8
#
# news/models.py
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

from ain7.utils import LoggedClass

class NewsItem(LoggedClass):

    title = models.CharField(verbose_name=_('title'), max_length=100)
    description = models.TextField(verbose_name=_('description'))
    image = models.ImageField(verbose_name=_('image'), upload_to='data', null=True, blank=True)
    creation_date = models.DateTimeField(verbose_name=_('date'), default=datetime.datetime.today, editable=False)

    def __unicode__(self):
        return self.title

    def short_description(self):
        if len(self.description) > 100:
            # we avoid to cut a word because this could produce non-valid html
            # example: t&eamp;nu -> t&ea
            wordlist = self.description[:100].split(" ")
            return " ".join(wordlist[:-1]) + " ..."
        else:
            return self.description
        
    class Meta:
        verbose_name = _('news item')
