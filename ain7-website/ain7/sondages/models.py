# -*- coding: utf-8
#
# sondages/models.py
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

from django.db import models
from django.utils.translation import gettext_lazy as _

class Survey(models.Model):
    question = models.CharField(verbose_name=_('question'), maxlength=200)
    publication_date = models.DateTimeField(verbose_name=_('publication date'))
    is_online = models.BooleanField(verbose_name=_('online'), default=False)

    def __str__(self):
        return self.question

    class Admin:
        list_display = ('question', 'publication_date')
        ordering = ['-publication_date']

    class Meta:
        verbose_name = _('survey')

class Choice(models.Model):

    choice = models.CharField(verbose_name=_('choice'), maxlength=200, core=True)
    votes = models.IntegerField(verbose_name=_('votes'), default=0, editable=False)

    survey = models.ForeignKey(Survey, verbose_name=_('survey'), related_name='choices', edit_inline=models.TABULAR, num_in_admin=3)

    def __str__(self):
        return self.choice

    class Meta:
        verbose_name = _('choice')
        verbose_name_plural = _('choices')
