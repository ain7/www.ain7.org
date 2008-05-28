# -*- coding: utf-8
#
# annuaire/views.py
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

import csv
import vobject
import time
import datetime

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import ObjectPaginator, InvalidPage
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django import newforms as forms
from django.db import models
from django.utils.translation import ugettext as _

from ain7.annuaire.models import *
from ain7.annuaire.forms import *
from ain7.emploi.models import Company, Office
from ain7.decorators import confirmation_required
from ain7.utils import ain7_render_to_response, ain7_generic_edit, ain7_generic_delete
from ain7.search_engine.models import *
from ain7.search_engine.utils import *

# Some parameters for the search engine

parameters = Parameters()
parameters.criteria_models = [Person, AIn7Member]
parameters.custom_fields = [
    ('company',        Office , 'positions__office__company'                ),
    ('activity_field', Company, 'positions__office__company__activity_field'),
    ('city',           Address, 'person__addresses__city'                   ),
    ('country',        Address, 'person__addresses__country'                ),
    ]
parameters.baseClass = AIn7Member


# Main functions

def annuaire_search_engine():
    return get_object_or_404(SearchEngine, name="annuaire")

@login_required
def contributions(request, user_id):
    p = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)
    list_contributions = UserContribution.objects.filter(user=p).order_by('-date')
    return ain7_render_to_response(request, 'annuaire/contributions.html',
                            {'person': p, 'ain7member': ain7member, 'list_contributions': list_contributions})

@login_required
def details(request, user_id):
    p = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)
    return ain7_render_to_response(request, 'annuaire/details.html',
                            {'person': p, 'ain7member': ain7member})

@login_required
def details_frame(request, user_id):
    p = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)
    return ain7_render_to_response(request, 'annuaire/details_frame.html',
                            {'person': p, 'ain7member': ain7member})

@login_required
def search(request):

    form = SearchPersonForm()
    ain7members = False
    nb_results_by_page = 25
    paginator = ObjectPaginator(AIn7Member.objects.none(),nb_results_by_page)
    page = 1

    if request.method == 'POST':
        form = SearchPersonForm(request.POST)
        if form.is_valid():

            # perform search
            criteria = form.criteria()
            ain7members = form.search(criteria)

            # compute criteria to be displayed in the form
            promo_default = [ -1, ""]
            track_default = [ -1, ""]
            if form.cleaned_data['promo'] != -1:
                promo_default = \
                    [form.cleaned_data['promo'], form.cleaned_data['promo']]
            if form.cleaned_data['track'] != -1:
                track_default = \
                    [form.cleaned_data['track'],
                     get_object_or_404(Track,pk=form.cleaned_data['track'])]

            # put the criteria in session: they must be accessed when
            # performing a CSV export, sending a mail...
            request.session['filter'] = criteria

            paginator = ObjectPaginator(ain7members, nb_results_by_page)

            try:
                page = int(request.GET.get('page', '1'))
                ain7members = paginator.get_page(page - 1)
            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'annuaire/search.html',
        {'form': form, 'ain7members': ain7members,
         'userFilters': annuaire_search_engine().registered_filters(
                            request.user.person),
         'paginator': paginator, 'is_paginated': paginator.pages > 1,
         'has_next': paginator.has_next_page(page - 1),
         'has_previous': paginator.has_previous_page(page - 1),
         'current_page': page, 'pages': paginator.pages,
         'next_page': page + 1, 'previous_page': page - 1,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.hits),
         'hits' : paginator.hits,})


@login_required
def advanced_search(request):

    filtr = annuaire_search_engine().unregistered_filters(request.user.person)
    if filtr:
        return ain7_render_to_response(request, 'annuaire/adv_search.html',
            dict_for_filter(request, filtr.id))
    else:
        return ain7_render_to_response(request, 'annuaire/adv_search.html',
            dict_for_filter(request, None))
    

@login_required
def filter_details(request, filter_id):

    return ain7_render_to_response(request, 'annuaire/adv_search.html',
        dict_for_filter(request, filter_id))


@login_required
def dict_for_filter(request, filter_id):

    ain7members = False
    p = request.user.person
    nb_results_by_page = 25
    paginator = ObjectPaginator(AIn7Member.objects.none(),nb_results_by_page)
    page = 1
    sf = None
    if filter_id:
        sf = get_object_or_404(SearchFilter, pk=filter_id)
        

    if request.method == 'POST':

        ain7members = AIn7Member.objects.all()
        if filter_id:
            ain7members = sf.search(parameters)
        paginator = ObjectPaginator(ain7members, nb_results_by_page)

        try:
            page = int(request.GET.get('page', '1'))
            ain7members = paginator.get_page(page - 1)
        except InvalidPage:
            raise http.Http404

    return {'ain7members': ain7members,
         'filtr': sf,
         'userFilters': annuaire_search_engine().registered_filters(p),
         'paginator': paginator, 'is_paginated': paginator.pages > 1,
         'has_next': paginator.has_next_page(page - 1),
         'has_previous': paginator.has_previous_page(page - 1),
         'current_page': page,
         'next_page': page + 1, 'previous_page': page - 1,
         'pages': paginator.pages,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.hits),
         'hits' : paginator.hits,}


@login_required
def filter_register(request):

    sf = annuaire_search_engine().unregistered_filters(request.user.person)
    if not sf:
        return HttpResponseRedirect('/annuaire/advanced_search/')

    form = SearchFilterForm()

    if request.method != 'POST':
        return ain7_render_to_response(request,
            'annuaire/edit_form.html',
            {'form': form, 'back': request.META.get('HTTP_REFERER', '/'),
             'action_title': _("Enter parameters of your filter")})
    else:
        form = SearchFilterForm(request.POST)
        if form.is_valid():
            fName = form.cleaned_data['name']
            # First we check that the user does not have
            # a filter with the same name
            sameName = annuaire_search_engine().\
                registered_filters(request.user.person).\
                filter(name=fName).count()
            if sameName>0:
                request.user.message_set.create(
                    message=_("One of your filters already has this name."))
                return HttpResponseRedirect('/annuaire/advanced_search/')

            # Set the registered flag to True
            sf.registered = True
            sf.name = fName
            sf.save()

            # Redirect to filter page
            request.user.message_set.create(
                message=_("Modifications have been successfully saved."))
            return HttpResponseRedirect(
                '/annuaire/advanced_search/filter/%s/' % sf.id)
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))
        return HttpResponseRedirect('/annuaire/advanced_search/')


@login_required
def filter_edit(request, filter_id):

    filtr = get_object_or_404(SearchFilter, pk=filter_id)
    form = SearchFilterForm(instance=filtr)

    if request.method == 'POST':
        form = SearchFilterForm(request.POST, instance=filtr)
        if form.is_valid():
            form.cleaned_data['user'] = filtr.user
            form.cleaned_data['operator'] = filtr.operator
            form.save()
            request.user.message_set.create(message=_("Modifications have been successfully saved."))
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))
        return HttpResponseRedirect(
            '/annuaire/advanced_search/filter/%s/' % filter_id)
    return ain7_render_to_response(
        request, 'annuaire/edit_form.html',
        {'form': form, 'action_title': _("Modification of the filter")})


@login_required
def remove_criteria(request, filtr):
    for crit in filtr.criteriaField.all():  crit.delete()
    for crit in filtr.criteriaFilter.all(): crit.delete()
    # TODO non recursivite + supprimer filtres sans criteres
    return

@login_required
def filter_reset(request, filter_id):

    filtr = get_object_or_404(SearchFilter, pk=filter_id)
    remove_criteria(request, filtr)
    if filtr.registered:
        return HttpResponseRedirect(
            '/annuaire/advanced_search/filter/%s/' % filter_id)
    else:
        return HttpResponseRedirect('/annuaire/advanced_search/')

@login_required
def filter_delete(request, filter_id):

    filtr = get_object_or_404(SearchFilter, pk=filter_id)
    try:
        # remove criteria linked to this filter from database
        remove_criteria(request, filtr)
        # now remove the filter
        filtr.delete()
        request.user.message_set.create(
            message=_("Your filter has been successfully deleted."))
    except KeyError:
        request.user.message_set.create(
            message=_("Something went wrong. The filter has not been deleted."))    
    return HttpResponseRedirect('/annuaire/advanced_search/')

@login_required
def filter_new(request):

    filtr = annuaire_search_engine().unregistered_filters(request.user.person)
    if not filtr:
        return HttpResponseRedirect('/annuaire/advanced_search/')
    remove_criteria(request, filtr)
    if filtr.registered:
        return HttpResponseRedirect(
            '/annuaire/advanced_search/filter/%s/' % filter_id)
    else:
        return HttpResponseRedirect('/annuaire/advanced_search/')

@login_required
def filter_swapOp(request, filter_id=None):

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
              return HttpResponseRedirect(
                  '/annuaire/advanced_search/filter/%s/' % filter_id)

          else:
              request.session['filter_operator'] = _(op)
              return HttpResponseRedirect('/annuaire/advanced_search/')

@login_required
def criterion_add(request, filter_id=None, criterionType=None):
    """ Used to add a criterion.
    It only deals with the first page (choice of the field or filter)
    and then redirects to criterion_edit. """

    # build formFields: the form containing the list of fields to propose
    choiceList = []
    for field in criteriaList(request.user):
        choiceList.append((field.name,field.verbose_name.capitalize()))
    formFields = ChooseFieldForm()
    formFields.fields['chosenField'].choices = choiceList

    # build formFilters: the form containing the list of filters to propose
    qs = annuaire_search_engine().registered_filters(request.user.person)
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
        filtr = SearchFilter()
        filtr.name=""
        filtr.operator=_(SearchFilter.OPERATORS[0][0])
        filtr.user = request.user.person
        filtr.registered = False
        filtr.search_engine = annuaire_search_engine()
        filtr.save()
        filter_id = filtr.id

    # in the POST case, we redirect to the corresponding edit methods
    if request.method == 'POST' and criterionType == 'field':
        form = ChooseFieldForm(request.POST)
        form.fields['chosenField'].choices = choiceList
        if form.is_valid():
            request.session['criterion_field']= form.cleaned_data['chosenField']
            return HttpResponseRedirect(
                '/annuaire/advanced_search/filter/%s/criterion/edit/field/' %\
                filter_id)
        
    if request.method == 'POST' and criterionType == 'filter':
        form = ChooseFilterForm(request.POST)
        if form.is_valid():
            new_criterion = SearchCriterionFilter()
            new_criterion.searchFilter= SearchFilter.objects.get(id=filter_id)
            new_criterion.filterCriterion = form.cleaned_data['chosenFilter']
            new_criterion.is_in = form.cleaned_data['is_in']
            new_criterion.save()
        return HttpResponseRedirect('/annuaire/advanced_search/')

    return ain7_render_to_response(request,
        'annuaire/criterion_add.html',
        {'formFields': formFields, 'formFilters': formFilters,
         'zeroFilters': zeroFilters})

@login_required
def criterionField_edit(request, filter_id=None, criterion_id=None):
    """ Used to modify a criterion.
    It can either be the second step during the creation of a criterion
    (see criterion_add) or the modification of an existing criterion."""

    fName = cCode = value = msg = ""
    # if we're adding a new criterion
    if criterion_id == None:
        msg = _("Criterion to add")
        try:
            fName = request.session['criterion_field']
        except KeyError:
            pass
    # otherwise we're modifying an existing criterion
    else:
        msg = _("Edit the criterion")
        crit = get_object_or_404(SearchCriterionField, pk=criterion_id)
        fName = crit.fieldName
        cCode = crit.comparatorName
        value = crit.value
    model,searchField = getFieldFromName(fName, parameters)
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
            if isinstance(searchField,models.fields.related.ForeignKey)\
            or isinstance(searchField,models.fields.related.ManyToManyField):
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
            displayedVal = getDisplayedVal(val,fName)
            # if the value is an object, store its id
            if str(type(val)).find('class ')!=-1:
                displayedVal = str(val)
                val = str(val.id)
            filtr = get_object_or_404(SearchFilter, pk=filter_id)
            fVName = searchField.verbose_name
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
            crit.fieldClass = model
            crit.comparatorName = cCode
            crit.comparatorVerboseName = compVName
            crit.value = val
            crit.displayedValue = displayedVal
            crit.save()
            if filtr.registered:
                return HttpResponseRedirect(
                    '/annuaire/advanced_search/filter/%s/' % filter_id)
            else:
                return HttpResponseRedirect('/annuaire/advanced_search/')
    return ain7_render_to_response(request,
        'annuaire/criterion_edit.html',
        {'form': form, 'chosenField': searchField.verbose_name,
         'action_title': msg})

@login_required
def criterionFilter_edit(request, filter_id=None, criterion_id=None):
    """ Used to modify a filter criterion, either in session or
    in a registered filter."""

    critFilter = get_object_or_404(SearchCriterionFilter, pk=criterion_id)
    (crit, isin) = (critFilter.filterCriterion, critFilter.is_in)

    qs = annuaire_search_engine().registered_filters(request.user.person)
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
            return HttpResponseRedirect(
                '/annuaire/advanced_search/filter/%s/' % filter_id)
    return ain7_render_to_response(request,
        'annuaire/criterionFilter_edit.html', {'form': form})

@login_required
def criterion_delete(request, filtr_id=None, crit_id=None, crit_type=None):
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
        return HttpResponseRedirect(
            '/annuaire/advanced_search/filter/%s/' % filtr_id)
    else:
        return HttpResponseRedirect('/annuaire/advanced_search/')

@login_required
def export_csv(request):

    criteria = request.session['filter']
    ain7members = AIn7Member.objects.filter(**criteria).distinct()

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=export_ain7.csv'

    writer = csv.writer(response)
    writer.writerow(['First Name', 'Last Name'])
    for member in ain7members:
       writer.writerow([member.person.first_name, member.person.last_name])

    return response

@login_required
def sendmail(request):

    criteria = request.session['filter']
    ain7members = AIn7Member.objects.filter(**criteria).distinct()

    f= SendmailForm()

    if request.method == 'POST':
        f = SendmailForm(request.POST)
        if f.is_valid():
            if f.cleaned_data['send_test']:
                request.user.person.send_mail(f.cleaned_data['subject'].encode('utf8'),f.cleaned_data['body'].encode('utf8'))
            else:
                for member in ain7members:
                    member.person.send_mail(f.cleaned_data['subject'].encode('utf8'),f.cleaned_data['body'].encode('utf8'))

    return ain7_render_to_response(request, 'annuaire/sendmail.html',
                            {'form': f})

@login_required
def edit(request, user_id=None):

    p = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)
    return ain7_render_to_response(request, 'annuaire/edit.html',
                            {'person': p, 'ain7member': ain7member})

@login_required
def person_edit(request, user_id=None):

    person = None
    if user_id:
        person = Person.objects.get(user=user_id)
    return ain7_generic_edit(
        request, person, PersonForm, {'user': person.user},
        'annuaire/edit_form.html',
        {'action_title': _("Modification of personal data for"),
         'person': person, 'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/annuaire/%s/edit' % (person.user.id),
        _("Modifications have been successfully saved."))

@login_required
def ain7member_edit(request, user_id=None):

    person = None
    ain7member = None
    if user_id:
        person = get_object_or_404(Person, user=user_id)
        ain7member = get_object_or_404(AIn7Member, person=person)
    return ain7_generic_edit(
        request, ain7member, AIn7MemberForm, {'person': person},
        'annuaire/edit_form.html',
        {'action_title': _("Modification of personal data for"),
         'person': person, 'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/annuaire/%s/edit' % (person.user.id),
        _("Modifications have been successfully saved."))

@confirmation_required(lambda user_id=None, object_id=None : '', 'annuaire/base.html', _('Do you really want to delete your avatar'))
@login_required
def avatar_delete(request, user_id):

    person = Person.objects.get(user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    ain7member.avatar = None
    ain7member.save()

    request.user.message_set.create(message=
        _('Your avatar has been successfully deleted.'))
    return HttpResponseRedirect('/annuaire/%s/edit/' % user_id)

# Adresses
@login_required
def address_edit(request, user_id=None, address_id=None):

    person = get_object_or_404(Person, user=user_id)
    address = None
    title = _('Creation of an address for')
    msgDone = _('Address successfully added.')
    if address_id:
        address = get_object_or_404(Address, pk=address_id)
        title = _('Modification of an address for')
        msgDone = _('Address informations updated successfully.')
    return ain7_generic_edit(
        request, address, AddressForm, {'person': person},
        'annuaire/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/annuaire/%s/edit/#address' % user_id, msgDone)

@confirmation_required(lambda user_id=None, address_id=None : str(get_object_or_404(Address, pk=address_id)), 'annuaire/base.html', _('Do you really want to delete your address'))
@login_required
def address_delete(request, user_id=None, address_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(Address, pk=address_id),
        '/annuaire/%s/edit/#address' % user_id,
        _('Address successfully deleted.'))

# Numeros de telephone
@login_required
def phone_edit(request, user_id=None, phone_id=None):

    person = get_object_or_404(Person, user=user_id)
    phone = None
    title = _('Creation of a phone number for')
    msgDone = _('Phone number added successfully.')
    if phone_id:
        phone = get_object_or_404(PhoneNumber, pk=phone_id)
        title = _('Modification of a phone number for')
        msgDone = _('Phone number informations updated successfully.')
    return ain7_generic_edit(
        request, phone, PhoneNumberForm, {'person': person},
        'annuaire/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/annuaire/%s/edit/#phone' % user_id, msgDone)

@confirmation_required(lambda user_id=None, phone_id=None : str(get_object_or_404(PhoneNumber, pk=phone_id)), 'annuaire/base.html', _('Do you really want to delete your phone number'))
@login_required
def phone_delete(request, user_id=None, phone_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(PhoneNumber, pk=phone_id),
        '/annuaire/%s/edit/#phone' % user_id,
        _('Phone number successfully deleted.'))

# Adresses de courriel
@login_required
def email_edit(request, user_id=None, email_id=None):

    person = get_object_or_404(Person, user=user_id)
    email = None
    title = _('Creation of an email address for')
    msgDone = _('Email address successfully added.')
    if email_id:
        email = get_object_or_404(Email, pk=email_id)
        title = _('Modification of an email address for')
        msgDone = _('Email informations updated successfully.')
    return ain7_generic_edit(
        request, email, EmailForm, {'person': person},
        'annuaire/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/annuaire/%s/edit/#email' % user_id, msgDone)

@confirmation_required(lambda user_id=None, email_id=None : str(get_object_or_404(Email, pk=email_id)), 'annuaire/base.html', _('Do you really want to delete your email address'))
@login_required
def email_delete(request, user_id=None, email_id=None):

    return ain7_generic_delete(request, get_object_or_404(Email, pk=email_id),
                               '/annuaire/%s/edit/#email' % user_id,
                               _('Email address successfully deleted.'))

# Comptes de messagerie instantanee
@login_required
def im_edit(request, user_id=None, im_id=None):

    person = get_object_or_404(Person, user=user_id)
    im = None
    title = _('Creation of an instant messaging account for')
    msgDone = _('Instant messaging account successfully added.')
    if im_id:
        im = get_object_or_404(InstantMessaging, pk=im_id)
        title = _('Modification of an instant messaging account for')
        msgDone = _('Instant messaging informations updated successfully.')
    return ain7_generic_edit(
        request, im, InstantMessagingForm, {'person': person},
        'annuaire/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/annuaire/%s/edit/#im' % user_id, msgDone)

@confirmation_required(lambda user_id=None, im_id=None : str(get_object_or_404(InstantMessaging, pk=im_id)), 'annuaire/base.html', _('Do you really want to delete your instant messaging account'))
@login_required
def im_delete(request, user_id=None, im_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(InstantMessaging, pk=im_id),
        '/annuaire/%s/edit/#im' % user_id,
        _('Instant messaging account successfully deleted.'))

# Comptes IRC
@login_required
def irc_edit(request, user_id=None, irc_id=None):

    person = get_object_or_404(Person, user=user_id)
    irc = None
    title = _('Creation of an IRC account for')
    msgDone = _('IRC account successfully added.')
    if irc_id:
        irc = get_object_or_404(IRC, pk=irc_id)
        title = _('Modification of an IRC account for')
        msgDone = _('IRC account informations updated successfully.')
    return ain7_generic_edit(
        request, irc, IRCForm, {'person': person},
        'annuaire/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/annuaire/%s/edit/#irc' % user_id, msgDone)

@confirmation_required(lambda user_id=None, irc_id=None : str(get_object_or_404(IRC, pk=irc_id)), 'annuaire/base.html', _('Do you really want to delete your IRC account'))
@login_required
def irc_delete(request, user_id=None, irc_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(IRC, pk=irc_id),
        '/annuaire/%s/edit/#irc' % user_id,
        _('IRC account successfully deleted.'))

# Sites Internet
@login_required
def website_edit(request, user_id=None, website_id=None):

    person = get_object_or_404(Person, user=user_id)
    website = None
    title = _('Creation of a website for')
    msgDone = _('Website successfully added.')
    if website_id:
        website = get_object_or_404(WebSite, pk=website_id)
        title = _('Modification of a website for')
        msgDone = _('Website informations updated successfully.')
    return ain7_generic_edit(
        request, website, WebSiteForm, {'person': person},
        'annuaire/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/annuaire/%s/edit/#website' % user_id, msgDone)

@confirmation_required(lambda user_id=None, website_id=None : str(get_object_or_404(WebSite, pk=website_id)), 'annuaire/base.html', _('Do you really want to delete your website'))
@login_required
def website_delete(request, user_id=None, website_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(WebSite, pk=website_id),
        '/annuaire/%s/edit/#website' % user_id,
        _('Website successfully deleted.'))

# Vie associative a l'n7

@login_required
def club_membership_edit(request, user_id=None, club_membership_id=None):

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    club_membership = None
    title = _('Creation of a club membership for')
    msgDone = _('Club membership successfully added.')
    if club_membership_id:
        club_membership = get_object_or_404(ClubMembership,
                                            pk=club_membership_id)
        title = _('Modification of a club membership for')
        msgDone = _('Club membership informations updated successfully.')
    return ain7_generic_edit(
        request, club_membership, ClubMembershipForm,
        {'member': ain7member}, 'annuaire/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/annuaire/%s/edit/#assoc' % user_id, msgDone)

@confirmation_required(lambda user_id=None, club_membership_id=None : str(get_object_or_404(ClubMembership, pk=club_membership_id)), 'annuaire/base.html', _('Do you really want to delete your club membership'))
@login_required
def club_membership_delete(request, user_id=None, club_membership_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(ClubMembership, pk=club_membership_id),
        '/annuaire/%s/edit/#assoc' % user_id,
        _('Club membership successfully deleted.'))

@login_required
def subscriptions(request, user_id):

    p = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)

    subscriptions_list = AIn7Subscription.objects.filter(member=ain7member).order_by('-date')

    return ain7_render_to_response(request, 'annuaire/subscriptions.html',
                            {'person': p, 'ain7member': ain7member, 'subscriptions_list': subscriptions_list})

@login_required
def subscription_edit(request, user_id=None, subscription_id=None):

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    subscription = None
    title = _('Adding a subscription for')
    msgDone = _('Subscription successfully added.')
    if subscription_id:
        subscription = get_object_or_404(AIn7Subscription, pk=subscription_id)
        title = _('Modification of a subscription for')
        msgDone = _('Subscription informations updated successfully.')
    return ain7_generic_edit(
        request, subscription, AIn7SubscriptionForm,
        {'member': ain7member}, 'annuaire/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/annuaire/%s/subscriptions/' % user_id, msgDone)

@confirmation_required(lambda user_id=None, subscription_id=None : str(get_object_or_404(AIn7Subscription, pk=subscription_id)), 'annuaire/base.html', _('Do you really want to delete this subscription'))
@login_required
def subscription_delete(request, user_id=None, subscription_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(AIn7Subscription, pk=subscription_id),
        '/annuaire/%s/subscriptions/' % user_id,
        _('Subscription successfully deleted.'))

@login_required
def preferences(request, user_id):

    p = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)

    form = PreferencesForm()

    return ain7_render_to_response(request, 'annuaire/preferences.html',
                            {'form': form, 'person': p, 'ain7member': ain7member})

@login_required
def register(request, user_id=None):

    form = NewMemberForm()

    if request.method == 'POST':
        form = NewMemberForm(request.POST)
        if form.is_valid():
            new_person = form.save()
            request.user.message_set.create(message=_("New user successfully created"))
            return HttpResponseRedirect('/annuaire/%s/edit/' % (new_person.user.id))
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request,
        'annuaire/edit_form.html',
        {'action_title': _('Register new user'), 'back': back, 'form': form})

@login_required
def vcard(request, user_id):

    p = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)

    mail = None
    mail_list = Email.objects.filter(person=p,preferred_email=True,is_confidential=False)
    if mail_list:
       mail = mail_list[0].email

    vcard = vobject.vCard()
    vcard.add('n').value = vobject.vcard.Name( family=p.last_name, given=p.first_name )
    vcard.add('fn').value = p.first_name+' '+p.last_name
    if mail:
        vcard.add('mail').value = mail
        vcard.add('mail').type_param = 'INTERNET'
    for address in  Address.objects.filter(person=p):
        vcard.add('adr').value = vobject.vcard.Address(street=address.line1 + ' ' + address.line2, city=address.city, region='', code=address.zip_code, country=address.country.name, box=address.number, extended='')
        vcard.add('adr').type_param = address.type.type
    for tel in PhoneNumber.objects.filter(person=p):
        vcard.add('tel').value = tel.number

    vcardstream = vcard.serialize()

    response = HttpResponse(vcardstream, mimetype='text/x-vcard')
    response['Filename'] = p.user.username+'.vcf'  # IE needs this
    response['Content-Disposition'] = 'attachment; filename='+p.user.username+'.vcf'

    return response

def complete_track(request):
    elements = []

    if request.method == 'POST':
        input = request.POST['input']
        tracks = Track.objects.filter(name__icontains=input)
        for track in tracks:
            elements.append({'id':track.id, 'value':track.name})

    return ain7_render_to_response(request, 'pages/complete.html', {'elements':elements})

def criteriaList(user):
    """ Returns the list of fields that are criteria for an advanced
    search.
    These fields are the attributes of models of CRITERIA_MODELS.
    If the user has an admin profile, he gets all these attributes,
    except OneToOne and ImageField fields.
    If not, we also exclude the fields of EXCLUDE_FIELDS."""

    attrList = []

    # models for which attributes are criteria for advanced search
    for model in parameters.criteria_models:

        for field in model._meta.fields + model._meta.many_to_many:

            if field.name in model.objects.adv_search_fields(user)\
                and (str(type(field)).find('OneToOneField')==-1)\
                and not isinstance(field,models.fields.FileField):
                attrList.append(field)

    # now we deal with custom fields
    for (fName,fModel,query) in parameters.custom_fields:
        attrList.append(getModelField(fModel, fName))

    # uncomment this if you want a sorted list of criteria
    #
    # def cmpFields(field1, field2):
    #     return cmp(field1.verbose_name.capitalize(),
    #                field2.verbose_name.capitalize())
    # attrList.sort(cmpFields)

    return attrList

def findParamsForFieldName(fieldName):
    for fieldNam, comps, formField in FIELD_PARAMS:
        if fieldNam==fieldName:
            return (fieldName, comps, formField)
    raise NotImplementedError
    return None

def findComparatorsForField(field):
    """ Returns the set of comparators for a given field,
    depending on its type."""
    compList = None
    formField = None
    (fieldName, comps, formField) = findParamsForField(field)
    if comps == None:
        raise NotImplementedError
    choiceList = []
    for compName, compVN, qComp, qNeg in comps:
        choiceList.append((compName,compVN))
    # if there is a choice list in the model, use it (for instance Person.sex)
    if '_choices' in field.__dict__:
        formField = forms.ChoiceField(
            label='', choices=field.__dict__['_choices'])
    return (choiceList,formField)

def getCompVerboseName(field, compCode):
    """ Returns the description of a comparator,
    given the field and the comparator's code."""
    compVerbName = None
    (fieldName, comps, formField) = findParamsForField(field)
    for code, name, qComp, qNeg in comps:
        if code == compCode:
            compVerbName = name
    return compVerbName

def getDisplayedVal(value, fieldName):
    """ Converts a value obtained from the form
    to a format displayed in the criteria list. """
    displayedVal = value
    mdl, field = getFieldFromName(fieldName, parameters)
    if str(type(field)).find('DateField')!=-1:
        dateVal = datetime.datetime(
            *time.strptime(str(value),'%Y-%m-%d')[0:5])
        displayedVal = dateVal.strftime('%d/%m/%Y')
    if str(type(field)).find('DateTimeField')!=-1:
        dateVal = datetime.datetime(
            *time.strptime(str(value),'%Y-%m-%d %H:%M:%S')[0:5])
        displayedVal = dateVal.strftime('%d/%m/%Y %H:%M')
    if str(type(field)).find('BooleanField')!=-1:
        if value:
            displayedVal = _('checked')
        else:
            displayedVal = _('unchecked')
    if '_choices' in field.__dict__:
        # in this case we used a ChoiceField and stored a key, not a value
        for (k,v) in field.__dict__['_choices']:
            if k==value: displayedVal = v                
    return displayedVal

def filtersToExclude(filter_id=None):
    """ A recursive function that computes filters to exclude
    when proposing the user a list of filters as criteria for the
    filter given in parameter. This corresponds to the filter itself
    and to every filter having this filter as criterion."""
    if filter_id==None:
        return []
    else:
        filtr = get_object_or_404(SearchFilter, pk=filter_id)
        result = [ filter_id ]        
        for crit in filtr.used_as_criterion.all():
            result.extend(filtersToExclude(crit.searchFilter))
        return result

