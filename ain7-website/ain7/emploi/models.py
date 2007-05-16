# -*- coding: utf-8
#
# emploi/models.py
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

import datetime

from django.db import models

from ain7.annuaire.models import Person

# An education item in the CV of a person.
class EducationItem(models.Model):

    school = models.CharField(verbose_name=_('school'), maxlength=150, core=True)
    diploma = models.CharField(verbose_name=_('diploma'), maxlength=150, blank=True, null=True)
    details = models.TextField(verbose_name=_('description'), blank=True, null=True)
    start_date = models.DateField(verbose_name=_('start date'), core=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True, null=True)
    person = models.ForeignKey(Person, related_name='education', edit_inline=models.STACKED, num_in_admin=1)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)

    def save(self):
        self.modification_date = datetime.datetime.today()
        return super(EducationItem, self).save()

    class Meta:
        verbose_name = _('Education item')
        ordering = ['-start_date']

# A leisure item in the CV of a person.
# For instance: title="Culture" detail="Japanim"
#               title="Sport" detail="Judo, Pastis, Pétanque"
class LeisureItem(models.Model):

    title = models.CharField(verbose_name=_('Title'), maxlength=50, core=True)
    detail = models.TextField(verbose_name=_('Detail'), blank=True, null=True)
    person = models.ForeignKey(Person, related_name='leisure', edit_inline=models.STACKED, num_in_admin=1)

    # Internal
    creation_date =  models.DateTimeField(default=datetime.datetime.now, editable=False)
    modification_date = models.DateTimeField(editable=False)

    def save(self):
        self.modification_date = datetime.datetime.today()
        return super(LeisureItem, self).save()

    class Meta:
        verbose_name = _('Leisure item')
        ordering = ['title']

