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

class NewsItem(models.Model):

    title = models.CharField(verbose_name=_('title'), max_length=100)
    description = models.TextField(verbose_name=_('description'))
    image = models.ImageField(verbose_name=_('image'), upload_to='data', null=True, blank=True)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)
    modifier = models.IntegerField(editable=False)

    def __unicode__(self):
        return self.title

    def short_description(self):
        if len(self.description) > 100:
            return self.description[:100] + " ..."
        else:
            return self.description

    def save(self):
        self.modification_date = datetime.datetime.today()
        self.modifier = 1
        return super(NewsItem, self).save()

    class Admin:
        list_display = ('title', 'description')

    class Meta:
        verbose_name = _('news item')
