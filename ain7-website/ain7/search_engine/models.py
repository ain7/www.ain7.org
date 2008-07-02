# -*- coding: utf-8 -*-
#
# search_engine/models.py
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
from django.contrib.auth.models import User
from ain7 import search_engine

# classes

class Parameters:
    # we are looking for objects from this class:
    baseClass = None
    # dictionary of {models, prefix}: list of models for which we want to
    # propose fields as criteria. They has to be subclasses of the baseClass.
    # Prefixes indicate how to reach this subclass from the baseClass.
    criteria_models = {}
    # some fields that we manage manually
    custom_fields = []
 
class SearchEngine(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __unicode__(self):
        return name

    def registered_filters(self, person):
        return self.filters.filter(registered=True).filter(user=person)
   
    def unregistered_filters(self, person):
        unregs = self.filters.filter(registered=False).filter(user=person)
        if unregs:
            # mise en commentaire de cet assert qui provoque un plantage de la recherche
            # avancee dans le profile dans certains cas restant à déterminer :(
            #assert(unregs.count()<2)
            return unregs[0]
        return None

class SearchFilter(models.Model):
    OPERATORS = [ ('and', _('and')),
                  ('or', _('or')) ]
    name = models.CharField(verbose_name=_('name'), max_length=20)
    search_engine = models.ForeignKey(SearchEngine,
            verbose_name=_('search engine'), related_name='filters')
    operator = models.CharField(verbose_name=_('operator'),
                                max_length=3, choices=OPERATORS)
    registered = models.BooleanField(default=True)
    user = models.ForeignKey(User, verbose_name=_('user'),
                             related_name='filters')

    def __unicode__(self):
        if self.registered:
            return self.name
        else:
            return _('unregistered filter')

    def search(self, parameters):
        return parameters.baseClass.objects.filter(
            self.buildQ(parameters)).distinct()

    def buildQ(self, parameters):
        q = models.Q()
        for crit in self.criteriaField.all():
            if self.operator == _('and'): q = q & crit.buildQ(parameters)
            else: q = q | crit.buildQ(parameters)
        
        for crit in self.criteriaFilter.all():
            qCrit = crit.filterCriterion.buildQ(parameters)
            if not crit.is_in: qCrit = ~qCrit
            if self.operator == _('and'): q = q & qCrit
            else: q = q | qCrit
        return q
    
    class Meta:
        verbose_name = _('filter')
        verbose_name_plural = _('filters')

class SearchCriterionField(models.Model):
    searchFilter = models.ForeignKey(SearchFilter,
                                     related_name='criteriaField')
    fieldName = models.CharField(max_length=30)
    fieldVerboseName = models.CharField(max_length=50)
    fieldClass = models.CharField(max_length=30)
    comparatorName = models.CharField(max_length=2)
    comparatorVerboseName = models.CharField(max_length=20)
    value = models.CharField(max_length=50)
    displayedValue = models.CharField(max_length=50)
    # Example: for a criterion 'prénom égale Toto'
    #     fieldName = 'last_name'
    #     fieldVerboseName = 'prénom'
    #     fieldClass = 'Person'
    #     comparatorName = 'EQ'
    #     comparatorVerboseName = 'égale'
    #     value = 'Toto'
    #     displayedValue = 'Toto'

    def __unicode__(self):
        return self.fieldVerboseName + " " \
               + self.comparatorVerboseName + " " \
               + self.displayedValue

    def buildQ(self, parameters):
        qComp, qNeg = search_engine.utils.compInQ(
            self.fieldName.encode('utf8'), self.comparatorName, parameters)
        # TODO : c'est du spécifique...
        # utiliser le dictionnaire criteria_models pour récupérer le préfixe
        modelPrefix = ''
        if self.fieldClass == 'annuaire.person':
            modelPrefix = 'person__'
        crit = modelPrefix + self.fieldName.encode('utf8') + qComp
        # if the criterion comes from a custom field, we use the specified query
        for (fName,fModel,query) in parameters.custom_fields:
            if self.fieldClass == str(fModel._meta):
                crit = query
        mdl, field = search_engine.utils.getFieldFromName(
            self.fieldName.encode('utf8'), parameters)
        q = models.Q(**{crit: self.value})
        if qNeg: q = ~q
        return q

class SearchCriterionFilter(models.Model):
    searchFilter = models.ForeignKey(SearchFilter,
        related_name='criteriaFilter', core=True)
    filterCriterion = models.ForeignKey(SearchFilter,
        related_name='used_as_criterion')
    is_in = models.BooleanField(default=True)

    def __unicode__(self):
        return str(filterCriterion)

