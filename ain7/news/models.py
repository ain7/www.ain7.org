# -*- coding: utf-8
"""
 ain7/news/models.py
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
from django.template import defaultfilters
from django.utils.translation import ugettext as _

from ain7.utils import LoggedClass


class NewsItem(LoggedClass):
    """news item"""

    title = models.CharField(verbose_name=_('title'), max_length=100)
    body = models.TextField(verbose_name=_('body'))
    slug = models.SlugField(max_length=100)
    image = models.ImageField(verbose_name=_('image'), upload_to='data',
        null=True, blank=True)
    creation_date = models.DateTimeField(verbose_name=_('date'), 
        default=datetime.datetime.today, editable=False)

    def __unicode__(self):
        """news item unicode method"""
        return self.title

    def get_absolute_url(self):
        """news item url"""
        return reverse('ain7.news.views.details', args=[self.slug])

    def short_body(self):
        """news item short body"""
        if len(self.body) > 100:
            # we avoid to cut a word because this could produce non-valid html
            # example: t&eamp;nu -> t&ea
            wordlist = self.body[:100].split(" ")
            return " ".join(wordlist[:-1]) + " ..."
        else:
            return self.body

    def save(self):
        """news item save method"""
        self.slug = defaultfilters.slugify(self.title)
        super(NewsItem, self).save()

    class Meta:
        """news item meta information"""
        verbose_name = _('news item')

