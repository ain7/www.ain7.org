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

from ain7.annuaire.models import Person

class Survey(models.Model):
    question = models.CharField(verbose_name=_('question'), maxlength=200)
    start_date = models.DateTimeField(verbose_name=_('start date'))
    end_date = models.DateTimeField(verbose_name=_('end date'))

    def __str__(self):
        return self.question

    def has_been_voted_by(self, voter):
        return Vote.objects.filter(survey=self, voter=voter).count() != 0

    def nb_vote(self):
        return Vote.objects.filter(survey=self).count()

    class Admin:
        list_display = ('question', 'start_date', 'end_date')
        ordering = ['-start_date', '-end_date']

    class Meta:
        verbose_name = _('survey')

class Choice(models.Model):
    choice = models.CharField(verbose_name=_('choice'), maxlength=200, core=True)

    survey = models.ForeignKey(Survey, verbose_name=_('survey'), related_name='choices', edit_inline=models.TABULAR, num_in_admin=3)

    def __str__(self):
        return self.choice

    def rate(self):
        total = self.survey.nb_vote()
        if total == 0:
            return 0
        else:
            return (self.votes.count() * 100.0) / total

    class Meta:
        verbose_name = _('choice')
        verbose_name_plural = _('choices')

class Vote(models.Model):
    voter = models.ForeignKey(Person, verbose_name=_('voter'), related_name='votes')
    choice = models.ForeignKey(Choice, verbose_name=_('choice'), related_name='votes')
    survey = models.ForeignKey(Survey, verbose_name=_('survey'), related_name='votes')

    class Meta:
        verbose_name = _('vote')