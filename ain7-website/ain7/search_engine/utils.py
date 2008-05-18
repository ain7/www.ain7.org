# -*- coding: utf-8 -*-
#
# search_engine/utils.py
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

import time
import datetime

from django import newforms as forms
from django.utils.translation import ugettext as _

from ain7.widgets import DateTimeWidget

# for each type of attribute, we define the comparators and the
# type of field to display in the form
dateWidget = DateTimeWidget()
dateWidget.dformat = '%d/%m/%Y'
dateTimeWidget = DateTimeWidget()
dateTimeWidget.dformat = '%d/%m/%Y %H:%M'
FIELD_PARAMS = [
    ('CharField',
     [('EQ',_('equals'),    '__iexact',   False),
      ('NE',_('not equals'),'__iexact',   True ),
      ('CT',_('contains'),  '__icontains',False)],
     forms.CharField(label='')),
    ('TextField',
     [('EQ',_('equals'),    '__iexact',   False),
      ('NE',_('not equals'),'__iexact',   True ),
      ('CT',_('contains'),  '__icontains',False)],
     forms.CharField(label='')),
    ('DateField',
     [('EQ',_('equals'),'',     False),
      ('BF',_('before'),'__lte',False),
      ('AT',_('after'), '__gte',False),],
     forms.DateField(label='', widget=dateWidget)),
    ('DateTimeField',
     [('EQ',_('equals'),'',     False),
      ('BF',_('before'),'__lte',False),
      ('AT',_('after'), '__gte',False),],
     forms.DateTimeField(label='', widget=dateTimeWidget)),
    ('IntegerField',
     [('EQ',_('equals'),    '__exact', False),
      ('NE',_('not equals'),'__exact', True ),
      ('LT',_('lower'),     '__lt',    False),
      ('GT',_('greater'),   '__gt',    False),],
     forms.IntegerField(label='')),
    ('BooleanField',
     [('IS',_('is'),'',False)],
     forms.BooleanField(label='', required=False, initial=True)),
    # for ForeignKey, the field is defined later
    ('ForeignKey',
     [('EQ',_('equals'),    '__exact', False),
      ('NE',_('not equals'),'__exact', True )],
     None),
    # for ManyToManyField, the field is defined later
    ('ManyToManyField',
     [('EQ',_('equals'),    '__exact', False),
      ('NE',_('not equals'),'__exact', True )],
     None),

    # Not implemented: RelatedField
    
    # Not implemented because not used in our model
    # or meaningless for a search engine:
    # AutoField, DecimalField, EmailField(CharField), FileField,
    # FilePathField, FloatField, ImageField(FileField), IPAddressField,
    # NullBooleanField, PhoneNumberField(IntegerField),
    # PositiveIntegerField(IntegerField),
    # PositiveSmallIntegerField(IntegerField), SlugField(CharField),
    # SmallIntegerField(IntegerField), TimeField, URLField(CharField),
    # USStateField(Field), XMLField(TextField),
    # OrderingField(IntegerField)
    ]

# TODO: il faut s'assurer que les champs de
# Person et AIn7Member sont disjoints !!!
def getFieldFromName(fieldName, parameters):
    """ Returns a field from its name."""
    field = fieldModel = None
    # first we look into models for which all fields are criteria
    for model in parameters.criteria_models:
        for basicField in model._meta.fields:
            if fieldName == basicField.name:
                fieldModel = model
                field = basicField
        if model._meta.many_to_many:
            for manyToManyField in model._meta.many_to_many:
                if fieldName == manyToManyField.name:
                    fieldModel = model
                    field = manyToManyField
    # then we look for fields manually managed
    for (fName, fModel, comps) in parameters.custom_fields:
        if fieldName == fName:
            fieldModel = fModel
            field = getModelField(fModel, fName)
    return (str(fieldModel._meta),field)

def getModelField(fModel, fName):
    """ Given a model and the name of one of its fields, returns this field."""
    field = None
    for f in fModel._meta.fields:
        if f.name == fName:
            field = f
    return field

def compInQ(fieldName,compCode, parameters):
    model, field = getFieldFromName(fieldName, parameters)
    fieldName, comps, formField = findParamsForField(field)
    if comps == None:
        raise NotImplementedError
    for compName, compVN, qComp, qNeg in comps:
        if compName == compCode:
            return (qComp,qNeg)
    return None

def findParamsForField(field):
    for fieldName, comps, formField in FIELD_PARAMS:
        if str(type(field)).find(fieldName)!=-1:
            return (fieldName, comps, formField)
    raise NotImplementedError
    return None

