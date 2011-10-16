# -*- coding: utf-8 -*-
#
# search_engine/models.py
#
#   Copyright © 2007-2011 AIn7 Devel Team
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

from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from ain7 import search_engine
from ain7.annuaire.models import AIn7Member, Person, Address
from ain7.emploi.models import Position, EducationItem
from ain7.organizations.models import Office, Organization


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
        return self.name

    def registered_filters(self, person):
        return self.filters.filter(registered=True).filter(user=person)
   
    def unregistered_filters(self, person):
        unregs = self.filters.filter(registered=False).filter(user=person)
        if unregs:
            assert(unregs.count()<2)
            return unregs[0]
        return None

def params(search_engine):
    """This is the place where we define parameters of search engine,
    as it cannot be stored in the base."""
    assert(search_engine)

    ase = get_object_or_404(SearchEngine, name="annuaire")
    aseParams = Parameters()
    aseParams.criteria_models = {AIn7Member:'', Person: 'person__'}
    def get_city(ain7member):
        return display_list(
            [ addr.city for addr in ain7member.person.addresses.all() ])
    def get_country(ain7member):
        return display_list(
            [ addr.country for addr in ain7member.person.addresses.all() ])
    def get_org(ain7member):
        return display_list(
            [ p.office.organization for p in ain7member.positions.all() ])
    def get_office(ain7member):
        return display_list(
            [ p.office for p in ain7member.positions.all() ])
    def get_activity(ain7member):
        return display_list([ p.office.organization.activity_field
                         for p in ain7member.positions.all() ])
    def get_diploma(ain7member):
        return display_list(
            [ e.diploma for e in ain7member.education.all() ])
    # custom_fields is made of the following components:
    # 1. the name of the field in the model
    # 2. the model from which we're considering a field
    # 3. the query really used when querying the database
    # 4. the query, given as a function
    # 5. a Boolean indicating if we want to print the model in the
    #    list of criteria proposed to the user
    aseParams.custom_fields = [
    ('city',         Address, 'person__addresses__city',        get_city, True ),
    ('country',      Address, 'person__addresses__country',     get_country, True ),
    ('organization', Office,  'positions__office__organization',get_org, False ),
    ('office', Position, 'positions__office', get_office, False ),
    ('activity_field', Organization,
     'positions__office__organization__activity_field', get_activity, False),
    ('diploma', EducationItem, 'education__diploma', get_diploma, False ),
    ]
    aseParams.baseClass = AIn7Member

    ose = get_object_or_404(SearchEngine, name="organization")
    oseParams = Parameters()
    oseParams.criteria_models = {Office:'', Organization: 'organization__'}
    oseParams.custom_fields = []
    oseParams.baseClass = Office

    params = { ase: aseParams , ose: oseParams, }
    if not search_engine in params.keys():
        raise AssertionError, \
              "No parameters found for search engine: " + str(search_engine)
    return params[search_engine]

def display_list(seq):
    """Converts a list of objects to a string."""
    if len(seq)==0: return ''
    seq = dict.fromkeys(seq).keys()  # remove duplicates
    ret = unicode(seq.pop())
    for s in seq: ret+=';'+unicode(seq.pop()).encode('utf-8') 
    return ret

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

    def search(self):
        return params(self.search_engine).baseClass.objects.filter(
            self.buildQ()).distinct()

    def buildQ(self):
        q = models.Q()
        for crit in self.criteriaField.all():
            if self.operator == _('and'): q = q & crit.buildQ()
            else: q = q | crit.buildQ()
        
        for crit in self.criteriaFilter.all():
            qCrit = crit.filterCriterion.buildQ()
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

    def buildQ(self):
        se = self.searchFilter.search_engine
        clas = getClassFromName(self.fieldClass, se)
        qComp, qNeg = search_engine.utils.compInQ(
            clas, self.fieldName.encode('utf8'), self.comparatorName, se)
        if clas in params(se).criteria_models.keys():
            modelPrefix = params(se).criteria_models[clas]
            crit = modelPrefix + self.fieldName.encode('utf8') + qComp
        
        # if the criterion comes from a custom field we use the specified query
        for (fName,fModel,query,solver, p) in params(se).custom_fields:
            if self.fieldClass == str(fModel._meta) and self.fieldName==fName:
                crit = query + qComp
        q = models.Q(**{crit: self.value})
        if qNeg: q = ~q
        return q

class SearchCriterionFilter(models.Model):
    searchFilter = models.ForeignKey(SearchFilter,
        related_name='criteriaFilter')
    filterCriterion = models.ForeignKey(SearchFilter,
        related_name='used_as_criterion')
    is_in = models.BooleanField(default=True)

    def __unicode__(self):
        return str(self.filterCriterion)

def getClassFromName(className, search_engine):
    """Example: 'annuaire.person' -> Person
    This is the invert function of getModelName."""
    model = None
    for modl in params(search_engine).criteria_models:
        if getModelName(modl) == className: model = modl
    for fName, fModel, comps, solver, p in params(search_engine).custom_fields:
        if getModelName(fModel) == className: model = fModel
    return model

def getModelName(model):
    """A unique way to stringify model names.
    This is the invert function of getClassFromName.
    Example : Person -> 'annuaire.person'"""
    return str(model._meta)

