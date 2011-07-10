# -*- coding: utf-8 -*-
#
# search_engine/views.py
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

import csv

from django import forms
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _

from ain7.search_engine.models import getModelName, SearchCriterionFilter, SearchFilter,\
                                      getClassFromName, SearchCriterionField
from ain7.search_engine.forms import ChooseFieldForm, ChooseCSVFieldsForm
from ain7.search_engine.utils import criteriaList, filtersToExclude, splitFieldFullname,\
                                     getFieldFromName, getModelField, findComparatorsForField,\
                                     getDisplayedVal, getCompVerboseName, getValueFromField
from ain7.ajax.views import ajax_resolve


@login_required
def se_criterion_add(request, search_engine=None, filter_id=None,
    criterionType=None, editFieldRedirect=None, filterRedirect=None,
    criterionAddTemplate=None):
    """ Used to add a criterion to a search engine.
    It only deals with the first page (choice of the field or filter)
    and then redirects to criterion_edit. """

    # build formFields: the form containing the list of fields to propose
    choiceList = []
    for field,model,printprefix in criteriaList(search_engine, request.user):
        prefix = ""
        if printprefix:
            prefix = model._meta.verbose_name.capitalize() + ' : '
        choiceList.append((getModelName(model)+'.'+field.name,
                           prefix + field.verbose_name.capitalize()))
    formFields = ChooseFieldForm()
    formFields.fields['chosenField'].choices = choiceList

    # build formFilters: the form containing the list of filters to propose
    qs = search_engine.registered_filters(request.user.person)
    if filter_id != '':
        for filterToExclude in filtersToExclude(filter_id):
            qs = qs.exclude(id=filterToExclude)
    zeroFilters = (qs.count()==0)
    class ChooseFilterForm(forms.Form):
        is_in = forms.BooleanField(label=_('is in filter'), required=False)
        chosenFilter = forms.ModelChoiceField(label=' ',
            required=True, empty_label=None, queryset = qs)
    formFilters = ChooseFilterForm()

    # if the user has no unregistered filter, we create one
    if request.method == 'POST' and filter_id=='':
        unreg = search_engine.unregistered_filters(request.user.person)
        if unreg:
            filter_id = unreg.id
        else:
            filtr = SearchFilter()
            filtr.name=""
            filtr.operator=_(SearchFilter.OPERATORS[0][0])
            filtr.user = request.user
            filtr.registered = False
            filtr.search_engine = search_engine
            filtr.save()
            filter_id = filtr.id

    # in the POST case, we redirect to the corresponding edit methods
    if request.method == 'POST' and criterionType == 'field':
        form = ChooseFieldForm(request.POST)
        form.fields['chosenField'].choices = choiceList
        if form.is_valid():
            request.session['criterion_field']= form.cleaned_data['chosenField']
            return HttpResponseRedirect(
                reverse(editFieldRedirect, args=[ filter_id ]))

    if request.method == 'POST' and criterionType == 'filter':
        form = ChooseFilterForm(request.POST)
        if form.is_valid():
            new_criterion = SearchCriterionFilter()
            new_criterion.searchFilter= SearchFilter.objects.get(id=filter_id)
            new_criterion.filterCriterion = form.cleaned_data['chosenFilter']
            new_criterion.is_in = form.cleaned_data['is_in']
            new_criterion.save()
        return HttpResponseRedirect(filterRedirect)

    return render(request, criterionAddTemplate,
        {'formFields': formFields, 'formFilters': formFilters,
         'zeroFilters': zeroFilters})



@login_required
def se_criterion_field_edit(request, search_engine=None, filter_id=None,
    criterion_id=None, registeredRedirect=None, unregisteredRedirect=None,
    criterionEditTemplate=None):
    """ Used to modify a criterion.
    It can either be the second step during the creation of a criterion
    (see se_criterion_add) or the modification of an existing criterion."""

    fName = cCode = value = msg = ""
    # if we're adding a new criterion
    if criterion_id == None:
        msg = _("Criterion to add")
        try:
            fModelName, fName = splitFieldFullname(
                request.session['criterion_field'])
            fModel = getClassFromName(fModelName, search_engine)
        except KeyError:
            pass
    # otherwise we're modifying an existing criterion
    else:
        msg = _("Edit the criterion")
        crit = get_object_or_404(SearchCriterionField, pk=criterion_id)
        fName = crit.fieldName
        fModelName = crit.fieldClass
        fModel = getClassFromName(fModelName, search_engine)
        cCode = crit.comparatorName
        value = crit.value
    searchField = getFieldFromName(fModel, fName, search_engine)
    field_verbose_name = getModelField(fModel,fName).verbose_name
    comps,valueField = findComparatorsForField(searchField)

    # the form with 2 fields : comparator and value
    class CriterionValueForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super(CriterionValueForm, self).__init__(*args, **kwargs)
            fieldsDict = {'value': valueField}
            # If several comparators are listed, then they are proposed
            # in the formular. Otherwise, we take the only one.
            if len(comps)>1:
                fieldsDict['comparator'] = forms.ChoiceField(
                    label='', choices=comps, required=True)
            # for ForeignKey, we define the value field entirely.
            # It "should" be possible to only redefine the queryset here...
            if (isinstance(searchField,ForeignKey)\
            or  isinstance(searchField,ManyToManyField))\
            and not searchField.rel.to in ajax_resolve().keys():
                fieldsDict['value'] = forms.ModelChoiceField(
                    label='', empty_label=None,
                    queryset=searchField.rel.to.objects.all())
            self.fields = fieldsDict
        # What's above is a trick to get the fields in the right order
        # when rendering the form.
        # It looks like a bug in Django. Try the code below to see
        # what happens:
        # comparator = forms.ChoiceField(
        #     label='', choices=comps, required=True)
        # value = valueField

    initDict = {'value': value}
    if len(comps)>1:
        initDict['comparator'] = cCode
    else:
        initDict['comparator'] = comps[0][0]
    form = CriterionValueForm(initDict)

    if request.method == 'POST':
        form = CriterionValueForm(request.POST)
        if form.is_valid():
            cCode = comps[0][0]
            try:
                cCode = form.cleaned_data['comparator']
            except KeyError:
                pass
            val = form.cleaned_data['value']
            displayedVal = getDisplayedVal(val,fModel,fName,search_engine)
            # if the value is an object, store its id
            if str(type(val)).find('class ')!=-1:
                displayedVal = str(val)
                val = str(val.id)
            filtr = get_object_or_404(SearchFilter, pk=filter_id)
            fVName = field_verbose_name
            compVName = getCompVerboseName(searchField, cCode)
            crit = None
            # if we're adding a new criterion
            if criterion_id == None:
                crit = SearchCriterionField()
            # otherwise we're modifying an existing criterion
            else:
                crit = get_object_or_404(
                    SearchCriterionField, pk=criterion_id)
            crit.searchFilter = filtr
            crit.fieldName = searchField.name
            crit.fieldVerboseName = fVName
            crit.fieldClass = getModelName(fModel)
            crit.comparatorName = cCode
            crit.comparatorVerboseName = compVName
            crit.value = val
            crit.displayedValue = displayedVal
            crit.save()
            if filtr.registered:
                return HttpResponseRedirect(registeredRedirect)
            else:
                return HttpResponseRedirect(unregisteredRedirect)
    return render(request, criterionEditTemplate,
        {'form': form, 'chosenField': field_verbose_name,
         'action_title': msg})

@login_required
def se_criterion_filter_edit(request, search_engine,
    filter_id=None, criterion_id=None, redirectAfterEdit=None,
    criterionEditTemplate=None):
    """ Used to modify a filter criterion, either in session or
    in a registered filter."""

    critFilter = get_object_or_404(SearchCriterionFilter, pk=criterion_id)
    (crit, isin) = (critFilter.filterCriterion, critFilter.is_in)

    qs = search_engine.registered_filters(request.user.person)
    for filterToExclude in filtersToExclude(filter_id):
        qs = qs.exclude(id=filterToExclude)

    class ChooseFilterForm(forms.Form):
        is_in = forms.BooleanField(label=_('is in filter'),
            required=False)
        chosenFilter = forms.ModelChoiceField(label=' ',
            required=False, empty_label=None, queryset = qs)

    form = ChooseFilterForm({'chosenField':crit, 'is_in': isin})

    if request.method == 'POST':
        form = ChooseFilterForm(request.POST)
        if form.is_valid():
            crit = form.cleaned_data['chosenFilter']
            isin = form.cleaned_data['is_in']
            filtr  = get_object_or_404(SearchFilter, pk=filter_id)
            criter = get_object_or_404(SearchCriterionFilter, pk=criterion_id)
            criter.searchFilter    = filtr
            criter.filterCriterion = crit
            criter.is_in           = isin
            criter.save()
            return HttpResponseRedirect(redirectAfterEdit)
    return render(request,
                                   criterionEditTemplate, {'form': form})

@login_required
def se_criterion_delete(request, filtr_id=None, crit_id=None,
    crit_type=None, registeredRedirect=None, unregisteredRedirect=None):
    crit = None
    if (crit_type == "field"):
        crit = get_object_or_404(SearchCriterionField, pk=crit_id)
    else:
        crit = get_object_or_404(SearchCriterionFilter, pk=crit_id)
    try:
        crit.delete()
        request.user.message_set.create(message=_("Modifications have been successfully saved."))
    except KeyError:
        request.user.message_set.create(message=_("Something went wrong. No modification done."))
    filtr = get_object_or_404(SearchFilter, pk=filtr_id)
    if filtr.registered:
        return HttpResponseRedirect(registeredRedirect)
    else:
        return HttpResponseRedirect(unregisteredRedirect)


@login_required
def se_filter_swap_op(request, filter_id=None,
    registeredRedirect=None, unregisteredRedirect=None):

    operator = None
    if filter_id:
        filtr = get_object_or_404(SearchFilter, pk=filter_id)
        operator = filtr.operator
    else:
        operator = request.session['filter_operator']
    for (op,desc) in SearchFilter.OPERATORS:
        if _(op) != operator:
            if filter_id:
                filtr.operator = _(op)
                filtr.save()
                return HttpResponseRedirect(registeredRedirect)
            else:
                request.session['filter_operator'] = _(op)
                return HttpResponseRedirect(unregisteredRedirect)


@login_required
def se_export_csv(request, objects_to_export=None, search_engine=None,
    editTemplate=None):
    """Export advanced search results to a CSV file.
    Fields to be exported are slected by the user."""

    choiceList = []
    for field,model,printprefix in criteriaList(search_engine, request.user):
        choiceList.append((getModelName(model)+'.'+field.name,
                           model._meta.verbose_name.capitalize() + ' : ' +
                           field.verbose_name.capitalize()))
    form = ChooseCSVFieldsForm()
    form.fields['chosenFields'].choices = choiceList

    if request.method != 'POST':
        return render(request, editTemplate,
            {'form': form, 'back': request.META.get('HTTP_REFERER', '/'),
             'action_title': _("Choose fields to export")})
    else:
        form = ChooseCSVFieldsForm(request.POST)
        form.fields['chosenFields'].choices = choiceList
        if form.is_valid():
            response = HttpResponse(mimetype='text/csv')
            response['Content-Disposition'] = \
                'attachment; filename=export_ain7.csv'
            writer = csv.writer(response)
            # in the first row we write fields names
            fields = []
            for fullname in form.cleaned_data['chosenFields']:
                classname, fieldname = splitFieldFullname(fullname)
                clas  = getClassFromName(classname, search_engine)
                field = getFieldFromName(clas, fieldname, search_engine)
                fields.append((field,clas))
            writer.writerow(
                [ f.verbose_name.capitalize().encode('utf8')
                  for f,c in fields ])
            # then we fill the following lines with search results
            for found_obj in objects_to_export:
                writer.writerow(
                    [ getValueFromField(f, found_obj, search_engine)
                      for f,c in fields ])
            return response
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            return render(request,
                {'form': form, 'back': request.META.get('HTTP_REFERER', '/'),
                'action_title': _("Choose fields to export")})

