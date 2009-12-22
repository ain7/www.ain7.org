# -*- coding: utf-8
"""
 ain7/sondages/models.py
"""
#
#   Copyright © 2007-2009 AIn7
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


class Survey(models.Model):
    """survey"""
    question = models.CharField(verbose_name=_('question'), max_length=200)
    start_date = models.DateField(verbose_name=_('start date'))
    end_date = models.DateField(verbose_name=_('end date'))

    def __unicode__(self):
        """survey unicode"""
        return self.question

    def has_been_voted_by(self, voter):
        """survey has been voted by someone"""
        return Vote.objects.filter(survey=self, voter=voter).count() != 0

    def nb_vote(self):
        """number of votes"""
        return Vote.objects.filter(survey=self).count()

    def delete(self):
        """delete survey"""
        for choice in self.choices.all():
            choice.delete()
        for vote in self.votes.all():
            vote.delete()
        return super(Survey, self).delete()
        
    def is_valid(self):
        """Test for survey that have to be displayed on index"""
        return (self.start_date == None or
                self.start_date <= datetime.date.today()) and \
               (self.end_date == None or
                self.end_date >= datetime.date.today()) and \
               (self.choices.count() > 0)

    class Meta:
        """survey meta"""
        verbose_name = _('survey')

class Choice(models.Model):
    """survey choice"""
    choice = models.CharField(verbose_name=_('choice'), max_length=200)

    survey = models.ForeignKey(Survey, verbose_name=_('survey'),
        related_name='choices')

    def __unicode__(self):
        """survey choice unicode method"""
        return self.choice

    def rate(self):
        """survey choice rate method"""
        total = self.survey.nb_vote()
        if total == 0:
            return 0
        else:
            return (self.votes.count() * 100.0) / total

    class Meta:
        """survey choice meta"""
        verbose_name = _('choice')
        verbose_name_plural = _('choices')

class Vote(models.Model):
    """survey vote"""
    voter = models.ForeignKey(Person, verbose_name=_('voter'),
        related_name='votes')
    choice = models.ForeignKey(Choice, verbose_name=_('choice'),
        related_name='votes')
    survey = models.ForeignKey(Survey, verbose_name=_('survey'),
        related_name='votes')

    class Meta:
        """vote meta"""
        verbose_name = _('vote')

