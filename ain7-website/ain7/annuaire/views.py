# -*- coding: utf-8
#
# annuaire/views.py
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

import csv
import vobject
import time
import datetime

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django import newforms as forms
from django.db import models

from ain7.annuaire.models import *
from ain7.decorators import confirmation_required
from ain7.utils import ain7_render_to_response, ImgUploadForm, isAdmin, form_callback
from ain7.widgets import DateTimeWidget

# A few settings

# list of models for which attributes can be advanced search criteria
CRITERIA_MODELS = [Person, AIn7Member]

# we exclude some of them for non-admin users
EXCLUDE_FIELDS = [
    # in Person
    'user','creation_date', 'modification_date', 'modifier',
    # in AIn7Member
    'person', 'member_type', 'person_type', 'avatar' ]

# default filter operator
DEFAULT_OPERATOR = _('or')

# for each type of attribute, we define the comparators and the
# type of field to display in the form
dateWidget = DateTimeWidget()
dateWidget.dformat = '%d/%m/%Y'
FIELD_PARAMS = [
    ('CharField',
     [('EQ',_('equals'),    '__iexact',   False),
      ('NE',_('not equals'),'__iexact',   True ),
      ('CT',_('contains'),  '__icontains',False)],
     forms.CharField('value', label='')),
    ('DateField',
     [('EQ',_('equals'),'',     False),
      ('BF',_('before'),'__lte',False),
      ('AT',_('after'), '__gte',False),],
     forms.DateField('value', label='', widget=dateWidget)),
    # TODO : pour les autres types
    ]

# Some basic forms

class SearchPersonForm(forms.Form):
    last_name = forms.CharField(label=_('Last name'), max_length=50, required=False)
    first_name = forms.CharField(label=_('First name'), max_length=50, required=False)
    promo = forms.IntegerField(label=_('Promo'), required=False)
    track = forms.IntegerField(label=_('Track'), required=False, initial=-1, widget=forms.HiddenInput())

class SendmailForm(forms.Form):
    subject = forms.CharField(label=_('subject'),max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))
    body = forms.CharField(label=_('body'),max_length=500, required=False, widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':95}))
    send_test = forms.BooleanField(label=_('Send me a test'), required=False)

# Main functions

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
def search(request):

    form = SearchPersonForm()
    ain7members = False

    if request.method == 'POST':
        form = SearchPersonForm(request.POST)
        if form.is_valid():

            # criteres sur le nom et prenom
            criteria={'person__last_name__contains':form.clean_data['last_name'].encode('utf8'),\
                      'person__first_name__contains':form.clean_data['first_name'].encode('utf8')}
            # ici on commence par rechercher toutes les promos
            # qui concordent avec l'annee de promotion et la filiere
            # saisis par l'utilisateur.
            promoCriteria={}
            if form.clean_data['promo'] != None:
                promoCriteria['year']=form.clean_data['promo']
            if form.clean_data['track'] != -1:
                promoCriteria['track']=\
                    Track.objects.get(id=form.clean_data['track'].encode('utf8'))

            # on ajoute ces promos aux critères de recherche
            # si elle ne sont pas vides
            if len(promoCriteria)!=0:
                criteria['promos__in']=Promo.objects.filter(**promoCriteria)

            request.session['filter'] = criteria

            ain7members = AIn7Member.objects.filter(**criteria)

    return ain7_render_to_response(request, 'annuaire/search.html', 
                            {'form': form, 'ain7members': ain7members})

@login_required
def advanced_search(request):

    # default values of a filter
    filterOperator = DEFAULT_OPERATOR
    conditionsList = []
    try:
        filterOperator = request.session['filter_operator']
        conditionsList = request.session['criteria']
    except KeyError:
        pass
    request.session['filter_operator'] = filterOperator
    request.session['criteria'] = conditionsList
    ain7members = False
    if request.method == 'POST':
        ain7members = performSearch(request, None)
    return ain7_render_to_response(request, 'annuaire/adv_search.html', 
        {'ain7members': ain7members,
         'searchFilter': None,
         'conditionsList': conditionsList,
         'filterOperator': filterOperator,
         'userFilters': SearchFilter.objects.filter(
                            user=request.user.person)})

@login_required
def sessionFilter_register(request):

    FilterForm = forms.form_for_model(SearchFilter,
        formfield_callback=_form_callback)
    form = FilterForm()

    if request.method != 'POST':
        return ain7_render_to_response(request,
            'annuaire/edit_form.html', 
            {'form': form, 
             'action_title': _("Enter parameters of your filter")})
    else:
        form = FilterForm(request.POST)
        if form.is_valid():
            fName = form.clean_data['name'].encode('utf8')
            request.user.message_set.create(
                message=_("Modifications have been successfully saved.")
                )
            sessionCriteria = []
            sf = None
            try:
                # First we check that the user does not have
                # a filter with the same name
                sameName = SearchFilter.objects.filter(name=fName)\
                           .filter(user=request.user.person).count()
                if sameName>0:
                    request.user.message_set.create(
                        message=_("One of your filters already has this name."))
                    return HttpResponseRedirect('/annuaire/advanced_search/')
                # Build the SearchFilter
                sf = SearchFilter(
                    name     = fName,
                    operator = request.session['filter_operator'],
                    user     = request.user.person)
                sf.save()
                # Get the criteria in session
                sessionCriteria = request.session['criteria']
            except KeyError:
                raise NotImplementedError # TODO

            # Build SearchCriterions linked to this SearchFilter
            for (fn, cC, fvn, cvn, val, dVal, model) in sessionCriteria:
                sc = SearchCriterion(
                    searchFilter = sf,
                    fieldName = fn,
                    fieldVerboseName = unicode(fvn,'utf8'),
                    fieldClass = model,
                    comparatorName = cC,
                    comparatorVerboseName = unicode(cvn,'utf8'),
                    value = unicode(val,'utf8'))
                sc.save()
                # Reset session filter
                resetSessionFilter(request)
                # Redirect to filter page
                return HttpResponseRedirect(
                    '/annuaire/advanced_search/filter/%s/' % sf.id)
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))
        return HttpResponseRedirect('/annuaire/advanced_search/')

@login_required
def sessionCriterion_delete(request, criterion_id):

    try:
        conditionsList = request.session['criteria']
    except KeyError:
        pass
    conditionsList.pop(int(criterion_id))
    request.session['criteria'] = conditionsList
    return HttpResponseRedirect('/annuaire/advanced_search/')

@login_required
def sessionFilter_reset(request):

    resetSessionFilter(request)
    return HttpResponseRedirect('/annuaire/advanced_search/')

@login_required
def filter_details(request, filter_id):

    filtr = get_object_or_404(SearchFilter, pk=filter_id)
    ain7members = False
    if request.method == 'POST':
        ain7members = performSearch(request, filtr)
    return ain7_render_to_response(request,
        'annuaire/filter_details.html', 
        {'filtr': filtr,
         'criteria': filtr.criteria.all(),
         'ain7members': ain7members,
         'userFilters': SearchFilter.objects.filter(
                            user=request.user.person)})

@login_required
def filter_edit(request, filter_id):

    filtr = get_object_or_404(SearchFilter, pk=filter_id)
    FilterForm = forms.form_for_instance(
        filtr, formfield_callback=_form_callback)
    form = FilterForm()
 	     
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            form.clean_data['user'] = filtr.user
            form.clean_data['operator'] = filtr.operator
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
def filter_reset(request, filter_id):

    filtr = get_object_or_404(SearchFilter, pk=filter_id)
    for crit in filtr.criteria.all():
        crit.delete()
    return HttpResponseRedirect(
        '/annuaire/advanced_search/filter/%s/' % filter_id)

@login_required
def filter_delete(request, filter_id):

    filtr = get_object_or_404(SearchFilter, pk=filter_id)
    try:
        for crit in filtr.criteria.all():
            crit.delete()
        filtr.delete()
        request.user.message_set.create(
            message=_("Your filter has been successfully deleted."))
    except KeyError:
        request.user.message_set.create(
            message=_("Something went wrong. The filter has not been deleted."))    
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
def criterion_add(request, filter_id=None):
    """ Used to add a criterion, either in session
    or in a registered filter.
    It only deals with the first page (choice of the field)
    and then redirects to criterion_edit. """

    choiceList = []
    for field in criteriaList(isAdmin(request.user)):
        choiceList.append((field.name,field.verbose_name.capitalize()))
        
    class ChooseFieldForm(forms.Form):
        chosenField = forms.ChoiceField(
            label=_('Field'), required=True,
            choices = choiceList)
    form = ChooseFieldForm()

    if request.method == 'POST':
        form = ChooseFieldForm(request.POST)
        if form.is_valid():
            request.session['criterion_field'] = \
                form.clean_data['chosenField']
            if filter_id:
                return HttpResponseRedirect(
                    '/annuaire/advanced_search/filter/%s/criterion/edit/' % filter_id)
            else:
                return HttpResponseRedirect(
                    '/annuaire/advanced_search/sessionFilter/criterion/edit/')
    return ain7_render_to_response(request,
        'annuaire/criterion_add.html', 
        {'form': form,
         'action_title': _("Choose the criterion to add")})

@login_required
def criterion_edit(request, filter_id=None, criterion_id=None):
    """ Used to modify a criterion, either in session or
    in a registered filter.
    It can either be the second step during the creation of a criterion
    (see criterion_add) or the modification of an existing criterion."""
    
    fName = cCode = value = ""
    # if we're adding a new criterion
    if criterion_id == None:
        try:
            fName = request.session['criterion_field']
        except KeyError:
            pass
    # otherwise we're modifying an existing criterion    
    else:
        if filter_id:
            crit = get_object_or_404(SearchCriterion, pk=criterion_id)
            fName = crit.fieldName
            cCode = crit.comparatorName
            value = crit.value
        else:
            try:
                conditionsList = request.session['criteria']
                fName, cCode, fVName, compVName, value, dVal, model = \
                           conditionsList[int(criterion_id)]
            except KeyError:
                pass
    model,searchField = getFieldFromName(fName)
    comps,valueField = findComparatorsForField(searchField)

    # the form with 2 fields : comparator and value
    class CriterionValueForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super(CriterionValueForm, self).__init__(*args, **kwargs)
            self.fields = {
                'value': valueField,
                'comparator': forms.ChoiceField(
                                  label='', choices=comps,
                                  required=True),
                }
        # What's above is a trick to get the fields in the right order
        # when rendering the form.
        # It looks like a bug in Django. Try the code below to see
        # what happens:
        # comparator = forms.ChoiceField(
        #     label='', choices=comps, required=True)
        # value = valueField
    
    form = CriterionValueForm({'comparator':cCode, 'value':value})

    if request.method == 'POST':
        form = CriterionValueForm(request.POST)
        if form.is_valid():
            cCode = form.clean_data['comparator']
            val = form.clean_data['value']
            displayedVal = getDisplayedVal(val,fName)
            # if the filter is registered
            if filter_id:
                filtr = get_object_or_404(SearchFilter, pk=filter_id)
                fVName = unicode(str(searchField.verbose_name),'utf8')
                compVName = getCompVerboseName(searchField, cCode)
                # if we're adding a new criterion
                if criterion_id == None:
                    newCrit = SearchCriterion(
                        searchFilter = filtr,
                        fieldName = searchField.name,
                        fieldVerboseName = fVName,
                        fieldClass = model,
                        comparatorName = cCode,
                        comparatorVerboseName = compVName,
                        value = val)
                    newCrit.save()
                # otherwise we're modifying an existing criterion    
                else:
                    crit = get_object_or_404(
                        SearchCondition, pk=condition_id)
                    crit.searchFilter = filtr
                    crit.fieldName = searchField.name
                    crit.fieldVerboseName = fVName
                    crit.fieldClass = model
                    crit.comparatorName = cCode
                    crit.comparatorVerboseName = compVName
                    crit.value = val
                    crit.save()
                return HttpResponseRedirect(
                    '/annuaire/advanced_search/filter/%s/' % filter_id)
            # if the filter is in session
            else:
                # get the current list of criteria
                critList = []
                try:
                    critList = request.session['criteria']
                except KeyError:
                    pass
                # if we're adding a new criterion
                if criterion_id == None:
                    # I don't know why, but I have to use lower case
                    newCrit = (
                        searchField.name, cCode,
                        searchField.verbose_name.lower(),
                        getCompVerboseName(searchField, cCode),
                        val, displayedVal, model )
                    critList.append(newCrit)
                # otherwise we're modifying an existing criterion    
                else:
                    critList[int(criterion_id)] = \
                        ( searchField.name, cCode,
                          searchField.verbose_name.lower(),
                          getCompVerboseName(searchField, cCode),
                          val, displayedVal, model )
                request.session['criteria'] = critList
                return HttpResponseRedirect(
                    '/annuaire/advanced_search/')
    return ain7_render_to_response(request,
        'annuaire/criterion_edit.html', 
        {'form': form,
         'chosenField': searchField.verbose_name,
         'action_title': _("Edit the criterion")})

    return HttpResponseRedirect('/annuaire/advanced_search/')

@login_required
def criterion_delete(request, filter_id=None, criterion_id=None):
    crit = get_object_or_404(SearchCondition, pk=condition_id)
    try:
        crit.delete()
        request.user.message_set.create(message=_("Modifications have been successfully saved."))
    except KeyError:
        request.user.message_set.create(message=_("Something went wrong. No modification done."))
    return HttpResponseRedirect(
        '/annuaire/advanced_search/filter/%s/' % filter_id)

@login_required
def export_csv(request):

    criteria = request.session['filter']
    ain7members = AIn7Member.objects.filter(**criteria)

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
    ain7members = AIn7Member.objects.filter(**criteria)

    f= SendmailForm()

    if request.method == 'POST':
        f = SendmailForm(request.POST)
        if f.is_valid():
            if f.clean_data['send_test']:
                request.user.person.send_mail(f.clean_data['subject'].encode('utf8'),f.clean_data['body'].encode('utf8'))
            else:
                for member in ain7members:
                    member.person.send_mail(f.clean_data['subject'].encode('utf8'),f.clean_data['body'].encode('utf8'))

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

    if user_id is None:
        PersonForm = forms.form_for_model(Person,
            formfield_callback=_form_callback)
        form = PersonForm()

    else:
        person = Person.objects.get(user=user_id)
        PersonForm = forms.form_for_instance(person,
            formfield_callback=_form_callback)
        PersonForm.base_fields['sex'].widget=\
            forms.Select(choices=Person.SEX)
        form = PersonForm(auto_id=False)

        if request.method == 'POST':
             form = PersonForm(request.POST)
             if form.is_valid():
                 form.clean_data['user'] = person.user
                 form.save()
                 request.user.message_set.create(message=_("Modifications have been successfully saved."))
             else:
                 request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))
             return HttpResponseRedirect('/annuaire/%s/edit' % (person.user.id))
    return ain7_render_to_response(request, 'annuaire/edit_form.html',
                            {'form': form, 'person': person,
                             'action_title': _("Modification of personal data for")})

@login_required
def ain7member_edit(request, user_id=None):

    if user_id is None:
        PersonForm = forms.form_for_model(AIn7Member,
            formfield_callback=_form_callback)
        form = PersonForm()

    else:
        person = Person.objects.get(user=user_id)
        ain7member = get_object_or_404(AIn7Member, person=person)
        avatar = ain7member.avatar
        PersonForm = forms.form_for_instance(ain7member,
            formfield_callback=_form_callback)

        if request.method == 'POST':
             post = request.POST.copy()
             post.update(request.FILES)
             form = PersonForm(post)
             if form.is_valid():
                 form.clean_data['person'] = person
                 form.clean_data['avatar'] = avatar
                 form.save()
                 request.user.message_set.create(message=_("Modifications have been successfully saved."))
             else:
                 request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))
             return HttpResponseRedirect('/annuaire/%s/edit' % (person.user.id))
        form = PersonForm(auto_id=False)
    return ain7_render_to_response(request, 'annuaire/edit_form.html',
                            {'form': form, 'person': person,
                             'action_title':
                             _("Modification of personal data for")})

@login_required
def avatar_edit(request, user_id):

    person = Person.objects.get(user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    if request.method == 'GET':
        form = ImgUploadForm()
        filename = None
        if ain7member.avatar:
            filename = '/site_media/%s' % ain7member.avatar
        return ain7_render_to_response(request, 'pages/image.html',
            {'section': 'annuaire/base.html', 'name': _("avatar").capitalize(),
             'form': form, 'filename': filename})
    else:
        post = request.POST.copy()
        post.update(request.FILES)
        form = ImgUploadForm(post)
        if form.is_valid():
            ain7member.save_avatar_file(
                form.clean_data['img_file']['filename'],
                form.clean_data['img_file']['content'])
            request.user.message_set.create(message=_("The picture has been successfully changed."))
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))
        return HttpResponseRedirect('/annuaire/%s/edit/' % (person.user.id))

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

def _generic_edit(request, user_id, object_id, object_type,
                  person, ain7member, action_title, msg_done):

    obj = get_object_or_404(object_type, pk=object_id)

    # 1er passage : on propose un formulaire avec les donnees actuelles
    if request.method == 'GET':
        PosForm = forms.form_for_instance(obj,
            formfield_callback=_form_callback)
        f = PosForm()
        return ain7_render_to_response(request, 'annuaire/edit_form.html',
                                {'form': f, 'action_title': action_title, 'person': person})

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        PosForm = forms.form_for_instance(obj,
            formfield_callback=_form_callback)
        f = PosForm(request.POST.copy())
        if f.is_valid():
            if person is not None:
                f.clean_data['person'] = person
            if ain7member is not None:
                f.clean_data['member'] = ain7member
            f.save()
            request.user.message_set.create(message=msg_done)
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))
        return HttpResponseRedirect('/annuaire/%s/edit/' % user_id)

def _generic_delete(request, user_id, object_id, object_type, msg_done):

    obj = get_object_or_404(object_type, pk=object_id)
    obj.delete()

    request.user.message_set.create(message=msg_done)
    return HttpResponseRedirect('/annuaire/%s/edit/' % user_id)

def _generic_add(request, user_id, object_type, person, ain7member,
                action_title, msg_done):

    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        PosForm = forms.form_for_model(object_type,
            formfield_callback=_form_callback)
        f = PosForm()
        return ain7_render_to_response(request, 'annuaire/edit_form.html',
                                {'person': person, 'ain7member': ain7member,
                                 'form': f, 'action_title': action_title})

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        PosForm = forms.form_for_model(object_type,
            formfield_callback=_form_callback)
        f = PosForm(request.POST.copy())
        if f.is_valid():
            if person is not None:
                f.clean_data['person'] = person
            if ain7member is not None:
                f.clean_data['member'] = ain7member
            f.save()
            request.user.message_set.create(message=msg_done)
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
        return HttpResponseRedirect('/annuaire/%s/edit/' % user_id)

# Adresses
@login_required
def address_edit(request, user_id=None, address_id=None):

    return _generic_edit(request, user_id, address_id, Address,
                         get_object_or_404(Person, user=user_id), None,
                         _('Modification of an address for'),
                         _('Address informations updated successfully.'))

@confirmation_required(lambda user_id=None, address_id=None : str(get_object_or_404(Address, pk=address_id)), 'annuaire/base.html', _('Do you really want to delete your address'))
@login_required
def address_delete(request, user_id=None, address_id=None):

    return _generic_delete(request, user_id, address_id, Address,
                           _('Address successfully deleted.'))

@login_required
def address_add(request, user_id=None):

    return _generic_add(request, user_id, Address,
                        get_object_or_404(Person, user=user_id), None,
                        _('Creation of an address for'),
                        _('Address successfully added.'))

# Numeros de telephone
@login_required
def phone_edit(request, user_id=None, phone_id=None):

    return _generic_edit(request, user_id, phone_id, PhoneNumber,
                         get_object_or_404(Person, user=user_id), None,
                         _('Modification of a phone number for'),
                         _('Phone number informations updated successfully.'))

@confirmation_required(lambda user_id=None, phone_id=None : str(get_object_or_404(PhoneNumber, pk=phone_id)), 'annuaire/base.html', _('Do you really want to delete your phone number'))
@login_required
def phone_delete(request, user_id=None, phone_id=None):

    return _generic_delete(request, user_id, phone_id, PhoneNumber,
                           _('Phone number successfully deleted.'))

@login_required
def phone_add(request, user_id=None):

    return _generic_add(request, user_id, PhoneNumber,
                        get_object_or_404(Person, user=user_id), None,
                        _('Creation of a phone number for'),
                        _('Phone number successfully added.'))

# Adresses de courriel
@login_required
def email_edit(request, user_id=None, email_id=None):

    return _generic_edit(request, user_id, email_id, Email,
                         get_object_or_404(Person, user=user_id), None,
                         _('Modification of an email address for'),
                         _('Email informations updated successfully.'))

@confirmation_required(lambda user_id=None, email_id=None : str(get_object_or_404(Email, pk=email_id)), 'annuaire/base.html', _('Do you really want to delete your email address'))
@login_required
def email_delete(request, user_id=None, email_id=None):

    return _generic_delete(request, user_id, email_id, Email,
                           _('Email address successfully deleted.'))

@login_required
def email_add(request, user_id=None):

    return _generic_add(request, user_id, Email,
                        get_object_or_404(Person, user=user_id), None,
                        _('Creation of an email address for'),
                        _('Email address successfully added.'))

# Comptes de messagerie instantanee
@login_required
def im_edit(request, user_id=None, im_id=None):

    return _generic_edit(request, user_id, im_id, InstantMessaging,
                         get_object_or_404(Person, user=user_id), None,
                         _('Modification of an instant messaging account for'),
                         _('Instant messaging informations updated successfully.'))

@confirmation_required(lambda user_id=None, im_id=None : str(get_object_or_404(InstantMessaging, pk=im_id)), 'annuaire/base.html', _('Do you really want to delete your instant messaging account'))
@login_required
def im_delete(request, user_id=None, im_id=None):

    return _generic_delete(request, user_id, im_id, InstantMessaging,
                           _('Instant messaging account successfully deleted.'))

@login_required
def im_add(request, user_id=None):

    return _generic_add(request, user_id, InstantMessaging,
                        get_object_or_404(Person, user=user_id), None,
                        _('Creation of an instant messaging account for'),
                        _('Instant messaging account successfully added.'))

# Comptes IRC
@login_required
def irc_edit(request, user_id=None, irc_id=None):

    return _generic_edit(request, user_id, irc_id, IRC,
                         get_object_or_404(Person, user=user_id), None,
                         _('Modification of an IRC account for'),
                         _('IRC account informations updated successfully.'))

@confirmation_required(lambda user_id=None, irc_id=None : str(get_object_or_404(IRC, pk=irc_id)), 'annuaire/base.html', _('Do you really want to delete your IRC account'))
@login_required
def irc_delete(request, user_id=None, irc_id=None):

    return _generic_delete(request, user_id, irc_id, IRC,
                           _('IRC account successfully deleted.'))

@login_required
def irc_add(request, user_id=None):

    return _generic_add(request, user_id, IRC,
                        get_object_or_404(Person, user=user_id), None,
                        _('Creation of an IRC account for'),
                        _('IRC account successfully added.'))

# Sites Internet
@login_required
def website_edit(request, user_id=None, website_id=None):

    return _generic_edit(request, user_id, website_id, WebSite,
                         get_object_or_404(Person, user=user_id), None,
                         _('Modification of a website for'),
                         _('Website informations updated successfully.'))

@confirmation_required(lambda user_id=None, website_id=None : str(get_object_or_404(WebSite, pk=website_id)), 'annuaire/base.html', _('Do you really want to delete your website'))
@login_required
def website_delete(request, user_id=None, website_id=None):

    return _generic_delete(request, user_id, website_id, WebSite,
                           _('Website successfully deleted.'))

@login_required
def website_add(request, user_id=None):

    return _generic_add(request, user_id, WebSite,
                        get_object_or_404(Person, user=user_id), None,
                        _('Creation of a website for'),
                        _('Website successfully added.'))

# Vie associative a l'n7

@login_required
def club_membership_edit(request, user_id=None, club_membership_id=None):

    person = get_object_or_404(Person, user=user_id)
    return _generic_edit(request, user_id, club_membership_id, ClubMembership,
                         person, get_object_or_404(AIn7Member, person=person),
                         _('Modification of a club membership for'),
                         _('Club membership informations updated successfully.'))

@confirmation_required(lambda user_id=None, club_membership_id=None : str(get_object_or_404(ClubMembership, pk=club_membership_id)), 'annuaire/base.html', _('Do you really want to delete your club membership'))
@login_required
def club_membership_delete(request, user_id=None, club_membership_id=None):

    return _generic_delete(request, user_id, club_membership_id, ClubMembership,
                           _('Club membership successfully deleted.'))

@login_required
def club_membership_add(request, user_id=None):

    person = get_object_or_404(Person, user=user_id)
    return _generic_add(request, user_id, ClubMembership,
                        person, get_object_or_404(AIn7Member, person=person),
                        _('Creation of a club membership for'),
                        _('Club membership successfully added.'))

@login_required
def subscriptions(request, user_id):

    p = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)

    subscriptions_list = AIn7Subscription.objects.filter(member=ain7member).order_by('-date')

    return ain7_render_to_response(request, 'annuaire/subscriptions.html',
                            {'person': p, 'ain7member': ain7member, 'subscriptions_list': subscriptions_list})

@login_required
def subscription_edit(request, user_id=None, subscription_id=None):

    return _generic_edit(request, user_id, subscription_id, AIn7Subscription,
                         get_object_or_404(Person, user=user_id), None,
                         _('Modification of a subscription for'),
                         _('Subscription informations updated successfully.'))

@confirmation_required(lambda user_id=None, subscription_id=None : str(get_object_or_404(AIn7Subscription, pk=subscription_id)), 'annuaire/base.html', _('Do you really want to delete this subscription'))
@login_required
def subscription_delete(request, user_id=None, subscription_id=None):

    return _generic_delete(request, user_id, subscription_id, AIn7Subscription,
                           _('Subscription successfully deleted.'))

@login_required
def subscription_add(request, user_id=None):

    return _generic_add(request, user_id, AIn7Subscription,
                        get_object_or_404(Person, user=user_id), None,
                        _('Adding a subscription for'),
                        _('Subscription successfully added.'))

@login_required
def preferences(request, user_id):

    p = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)

    return ain7_render_to_response(request, 'annuaire/preferences.html',
                            {'person': p, 'ain7member': ain7member})

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
        vcard.add('adr').value = vobject.vcard.Address(street=address.street, city=address.city, region='', code=address.zip_code, country=address.country.name, box=address.number, extended='')
        vcard.add('adr').type_param = address.type.type
    for tel in PhoneNumber.objects.filter(person=p):
        vcard.add('tel').value = tel.number

    vcardstream = vcard.serialize()

    response = HttpResponse(vcardstream, mimetype='text/x-vcard')
    response['Filename'] = p.user.username+'.vcf'  # IE needs this
    response['Content-Disposition'] = 'attachment; filename='+p.user.username+'.vcf'

    return response

# une petite fonction pour exclure certains champs
# des formulaires crees avec form_for_model et form_for_instance
def _form_callback(f, **args):
  exclude_fields = ('person', 'user', 'member', 'avatar', 'operator')
  if f.name in exclude_fields:
    return None
  return form_callback(f, **args)

def complete_track(request):
    elements = []

    if request.method == 'POST':
        input = request.POST['input']
        tracks = Track.objects.filter(name__icontains=input)
        for track in tracks:
            elements.append({'id':track.id, 'value':track.name})

    return ain7_render_to_response(request, 'pages/complete.html', {'elements':elements})

def opDescription(operator):
    for (op,desc) in SearchFilter.OPERATORS:
        if op == operator:
            filterOp = desc
    return filterOp

def performSearch(request, filtr=None):
    """ Really perform search.
    If filtr is None, then we get criteria from the session. """
    #
    # Determine :
    # - operator : AND or OR ?
    # - criteria : build list of criteria for Qs:
    #              we don't use a dictionary because the same key
    #              could appear several times.
    operator = None
    criteria = []
    if filtr:
        operator = filtr.operator
        criteria = buildCriteriaFromFilter(request, filtr)
    else:
        operator = request.session['filter_operator']
        criteria = buildCriteriaFromSession(request)
    #
    # now use this list of criteria to filter
    #
    q = models.Q()
    for qCrit in criteria:
        if operator == _('and'):
            q = q & qCrit
        else:
            q = q | qCrit
    return AIn7Member.objects.filter(q)

def criteriaList(isAdmin):
    """ Returns the list of fields that are criteria for an advanced
    search.
    These fields are the attributes of models of CRITERIA_MODELS.
    If the user has an admin profile, he gets all these attributes.
    If not, we exclude the fields of EXCLUDE_FIELDS."""

    attrList = []
    def add_attr(field):
        if (not field.name in EXCLUDE_FIELDS) or isAdmin:
            attrList.append(field)

    # models for which attributes are criteria for advanced search
    for model in CRITERIA_MODELS:

        for basicField in model._meta.fields:
            add_attr(basicField)

        # _meta.fields does not contain ManyToManyFields, so we add them
        if model._meta.many_to_many:  
            for manyToManyField in model._meta.many_to_many:  
                add_attr(manyToManyField)  

        # TODO: add related_names ??? (it's also in _meta)

    # uncomment this if you want a sorted list of criteria
    #
    # def cmpFields(field1, field2):
    #     return cmp(field1.verbose_name.capitalize(),
    #                field2.verbose_name.capitalize())
    # attrList.sort(cmpFields)
    
    return attrList

def findParamsForField(field):
    for fieldName, comps, formField in FIELD_PARAMS:
        if str(type(field)).find(fieldName)!=-1:
            return (fieldName, comps, formField)
    return None

def findParamsForFieldName(fieldName):
    for fieldNam, comps, formField in FIELD_PARAMS:
        if fieldNam==fieldName:
            return (fieldName, comps, formField)
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
    return (choiceList,formField)

# TODO: il faut s'assurer que les champs de
# Person et AIn7Member sont disjoints !!!
def getFieldFromName(fieldName):
    """ Returns a field from its name."""
    field = fieldModel = None
    for model in CRITERIA_MODELS:
        for basicField in model._meta.fields:
            if fieldName == basicField.name:
                fieldModel = model
                field = basicField
        if model._meta.many_to_many:  
            for manyToManyField in model._meta.many_to_many:  
                if fieldName == manyToManyField.name:
                    fieldModel = model
                    field = manyToManyField    
    return (str(fieldModel._meta),field)

def getCompVerboseName(field, compCode):
    """ Returns the description of a comparator,
    given the field and the comparator's code."""
    compVerbName = None
    (fieldName, comps, formField) = findParamsForField(field)
    for code, name, qComp, qNeg in comps:
        if code == compCode:
            compVerbName = name
    return unicode(compVerbName,'utf8')

def buildCriteriaFromSession(request):
    criteria = []
    sessionCriteria = []
    try:
        sessionCriteria = request.session['criteria']
    except KeyError:
        pass
    for (fieldN, cCode, fVN, cVN, val, dVal, model) in sessionCriteria:
        criteria.append(
            buildQForCriterion(model, fieldN, cCode,val))
    return criteria

def buildCriteriaFromFilter(request, filtr):
    criteria = []
    for crit in filtr.criteria.all():
        criteria.append(
            buildQForCriterion(crit.fieldClass,
                               crit.fieldName.encode('utf8'),
                               crit.comparatorName,
                               unicode(crit.value, 'utf8')))
    return criteria

def buildQForCriterion(model,fieldN,compCode,value):
    qComp, qNeg = compInQ(fieldN,compCode)
    # TODO : c'est du spécifique...
    modelPrefix = ''
    if model == 'annuaire.person':
        modelPrefix = 'person__'
    crit = modelPrefix + fieldN + qComp
    mdl, field = getFieldFromName(fieldN)
    if str(type(field)).find('CharField')!=-1:
        value = value.encode('utf8')
    q = models.Q(**{crit: value})
    if qNeg:
        q = models.query.QNot(q)
    return q

def compInQ(fieldName,compCode):
    model, field = getFieldFromName(fieldName)
    fieldName, comps, formField = findParamsForField(field)
    if comps == None:
        raise NotImplementedError
    for compName, compVN, qComp, qNeg in comps:
        if compName == compCode:
            return (qComp,qNeg)
    return None


def resetSessionFilter(request):
    request.session['criteria'] = []
    request.session['filter_operator'] = DEFAULT_OPERATOR
    return

def getDisplayedVal(value, fieldName):
    """ Converts a value obtained from the form
    to a format displayed in the criteria list. """
    displayedVal = value
    mdl, field = getFieldFromName(fieldName)
    if str(type(field)).find('DateField')!=-1:
        dateVal = datetime.datetime(
            *time.strptime(str(value),'%Y-%m-%d')[0:5])
        displayedVal = dateVal.strftime('%d/%m/%Y')
    return displayedVal
