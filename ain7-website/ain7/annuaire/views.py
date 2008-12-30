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

import vobject
import time
import datetime

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.db import models
from django.utils.translation import ugettext as _
from django.http import Http404

from ain7.annuaire.models import *
from ain7.annuaire.forms import *
from ain7.emploi.models import Organization, Office
from ain7.decorators import confirmation_required
from ain7.utils import ain7_render_to_response, ain7_generic_edit, ain7_generic_delete, check_access
from ain7.search_engine.models import *
from ain7.search_engine.utils import *
from ain7.search_engine.views import *


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
    is_subscriber = AIn7Subscription.objects.filter(member=ain7member,year=datetime.datetime.now().year)
    return ain7_render_to_response(request, 'annuaire/details.html',
                            {'person': p, 'is_subscriber': is_subscriber, 'ain7member': ain7member})

@login_required
def details_frame(request, user_id):
    p = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)
    return ain7_render_to_response(request, 'annuaire/details_frame.html',
                            {'person': p, 'ain7member': ain7member})

@login_required
def search(request):

    form = SearchPersonForm()
    dosearch = False
    ain7members = False
    nb_results_by_page = 25
    paginator = Paginator(AIn7Member.objects.none(),nb_results_by_page)
    page = 1

    if request.GET.has_key('first_name') or request.GET.has_key('last_name') or \
       request.GET.has_key('organization') or request.GET.has_key('promo') or request.GET.has_key('track'):
        form = SearchPersonForm(request.GET)
        if form.is_valid():

            dosearch = True

            # perform search
            criteria = form.criteria()
            ain7members = form.search(criteria)

            # put the criteria in session: they must be accessed when
            # performing a CSV export, sending a mail...
            request.session['filter'] = criteria
            paginator = Paginator(ain7members, nb_results_by_page)

            try:
                page = int(request.GET.get('page', '1'))
                ain7members = paginator.page(page).object_list
            except InvalidPage:
                raise Http404

    return ain7_render_to_response(request, 'annuaire/search.html',
        {'form': form, 'ain7members': ain7members, 'request': request,
         'userFilters': annuaire_search_engine().registered_filters(
                            request.user.person),
         'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page, 'pages': paginator.num_pages,
         'next_page': page + 1, 'previous_page': page - 1,
         'first_result': (page-1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits' : paginator.count, 'dosearch': dosearch})


@login_required
def advanced_search(request):

    r = check_access(request, request.user, ['ain7-member','ain7-secretariat'])
    if r:
        return r

    filter = annuaire_search_engine().unregistered_filters(request.user.person)
    if filter:
        return ain7_render_to_response(request, 'annuaire/adv_search.html',
            dict_for_filter(request, filter.id))
    else:
        return ain7_render_to_response(request, 'annuaire/adv_search.html',
            dict_for_filter(request, None))
    

@login_required
def filter_details(request, filter_id):

    r = check_access(request, request.user, ['ain7-member','ain7-secretariat'])
    if r:
        return r

    return ain7_render_to_response(request, 'annuaire/adv_search.html',
        dict_for_filter(request, filter_id))


@login_required
def dict_for_filter(request, filter_id):

    r = check_access(request, request.user, ['ain7-member','ain7-secretariat'])
    if r:
        return r

    ain7members = False
    p = request.user.person
    nb_results_by_page = 25
    paginator = Paginator(AIn7Member.objects.none(),nb_results_by_page)
    page = 1
    sf = None
    if filter_id:
        sf = get_object_or_404(SearchFilter, pk=filter_id)
        

    if request.method == 'POST':

        ain7members = AIn7Member.objects.all()
        if filter_id:
            ain7members = sf.search()
        paginator = Paginator(ain7members, nb_results_by_page)

        try:
            page = int(request.GET.get('page', '1'))
            ain7members = paginator.page(page).object_list
        except InvalidPage:
            raise http.Http404

    return {'ain7members': ain7members,
         'filtr': sf,
         'userFilters': annuaire_search_engine().registered_filters(p),
         'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page,
         'next_page': page + 1, 'previous_page': page - 1,
         'pages': paginator.num_pages,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits' : paginator.count}


@login_required
def filter_register(request):

    r = check_access(request, request.user, ['ain7-member','ain7-secretariat'])
    if r:
        return r

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
                request.user.message_set.create(message=_("One of your filters already has this name."))
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

    r = check_access(request, request.user, ['ain7-member','ain7-secretariat'])
    if r:
        return r

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

    r = check_access(request, request.user, ['ain7-member','ain7-secretariat'])
    if r:
        return r

    filtr = get_object_or_404(SearchFilter, pk=filter_id)
    remove_criteria(request, filtr)
    if filtr.registered:
        return HttpResponseRedirect(
            '/annuaire/advanced_search/filter/%s/' % filter_id)
    else:
        return HttpResponseRedirect('/annuaire/advanced_search/')

@login_required
def filter_delete(request, filter_id):

    r = check_access(request, request.user, ['ain7-member','ain7-secretariat'])
    if r:
        return r

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

    r = check_access(request, request.user, ['ain7-member','ain7-secretariat'])
    if r:
        return r

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
    return se_filter_swapOp(request, filter_id,
                            reverse(filter_details, args =[ filter_id ]),
                            reverse(advanced_search))

@login_required
def criterion_add(request, filter_id=None, criterionType=None):
    redirect = reverse(advanced_search)
    if filter_id: redirect = reverse(filter_details, args=[ filter_id ])
    return se_criterion_add(request, annuaire_search_engine(),
        filter_id, criterionType, criterionField_edit,
        redirect, 'annuaire/criterion_add.html')

@login_required
def criterionField_edit(request, filter_id=None, criterion_id=None):
    return se_criterionField_edit(request, annuaire_search_engine(),
        filter_id, criterion_id, reverse(filter_details, args=[filter_id]),
        reverse(advanced_search), 'annuaire/criterion_edit.html')

@login_required
def criterionFilter_edit(request, filter_id=None, criterion_id=None):
    return se_criterionFilter_edit(request, annuaire_search_engine(),
        filter_id, criterion_id, reverse(filter_details, args=[filter_id]),
        'annuaire/criterionFilter_edit.html')

@login_required
def criterion_delete(request, filtr_id=None, crit_id=None, crit_type=None):
    return se_criterion_delete(request, filtr_id, crit_id, crit_type,
        reverse(filter_details, args=[filtr_id]), reverse(advanced_search))

@login_required
def export_csv(request):

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    if not request.session.has_key('filter'):
        request.user.message_set.create(message=_("You have to make a search before using csv export."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    criteria = request.session['filter']
    ain7members = AIn7Member.objects.filter(**criteria).distinct()

    return se_export_csv(request, ain7members, annuaire_search_engine(),
        'annuaire/edit_form.html')

@login_required
def adv_export_csv(request, filter_id=None):

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    se = annuaire_search_engine()
    if not filter_id and not se.unregistered_filters(request.user.person):
        request.user.message_set.create(message=
            _("You have to make a search before using csv export."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    if filter_id:
        sf = get_object_or_404(SearchFilter, id=filter_id)
    else:
        sf = se.unregistered_filters(request.user.person)
    return se_export_csv(request, sf.search(), se, 'annuaire/edit_form.html')

@login_required
def sendmail(request):

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    if not request.session.has_key('filter'):
        request.user.message_set.create(message=_("You have to make a search before using sendmail."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

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

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    p = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)
    return ain7_render_to_response(request, 'annuaire/edit.html',
                            {'person': p, 'ain7member': ain7member})

@login_required
def person_edit(request, user_id=None):

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

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

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

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

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

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

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

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

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    return ain7_generic_delete(request,
        get_object_or_404(Address, pk=address_id),
        '/annuaire/%s/edit/#address' % user_id,
        _('Address successfully deleted.'))

# Numeros de telephone
@login_required
def phone_edit(request, user_id=None, phone_id=None):

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

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

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    return ain7_generic_delete(request,
        get_object_or_404(PhoneNumber, pk=phone_id),
        '/annuaire/%s/edit/#phone' % user_id,
        _('Phone number successfully deleted.'))

# Adresses de courriel
@login_required
def email_edit(request, user_id=None, email_id=None):

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

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

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    return ain7_generic_delete(request, get_object_or_404(Email, pk=email_id),
                               '/annuaire/%s/edit/#email' % user_id,
                               _('Email address successfully deleted.'))

# Comptes de messagerie instantanee
@login_required
def im_edit(request, user_id=None, im_id=None):

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

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

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    return ain7_generic_delete(request,
        get_object_or_404(InstantMessaging, pk=im_id),
        '/annuaire/%s/edit/#im' % user_id,
        _('Instant messaging account successfully deleted.'))

# Comptes IRC
@login_required
def irc_edit(request, user_id=None, irc_id=None):

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

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

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    return ain7_generic_delete(request,
        get_object_or_404(IRC, pk=irc_id),
        '/annuaire/%s/edit/#irc' % user_id,
        _('IRC account successfully deleted.'))

# Sites Internet
@login_required
def website_edit(request, user_id=None, website_id=None):

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

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

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    return ain7_generic_delete(request,
        get_object_or_404(WebSite, pk=website_id),
        '/annuaire/%s/edit/#website' % user_id,
        _('Website successfully deleted.'))

# Vie associative a l'n7

@login_required
def club_membership_edit(request, user_id=None, club_membership_id=None):

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

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

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    return ain7_generic_delete(request,
        get_object_or_404(ClubMembership, pk=club_membership_id),
        '/annuaire/%s/edit/#assoc' % user_id,
        _('Club membership successfully deleted.'))

@login_required
def subscriptions(request, user_id):

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    p = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)

    subscriptions_list = AIn7Subscription.objects.filter(member=ain7member).order_by('-date')

    return ain7_render_to_response(request, 'annuaire/subscriptions.html',
                            {'person': p, 'ain7member': ain7member, 'subscriptions_list': subscriptions_list})

@login_required
def subscription_edit(request, user_id=None, subscription_id=None):

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r

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

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r

    return ain7_generic_delete(request,
        get_object_or_404(AIn7Subscription, pk=subscription_id),
        '/annuaire/%s/subscriptions/' % user_id,
        _('Subscription successfully deleted.'))

@login_required
def register(request, user_id=None):

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

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

    r = check_access(request, request.user, ('ain7-secretariat','ain7-member'))
    if r:
        return r

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
        street = ''
        if address.line1:
            street = street + address.line1
        if address.line2:
            street = street + address.line2
        vcard.add('adr').value = vobject.vcard.Address(street=street, city=address.city, region='', code=address.zip_code, country=address.country.name, box='', extended='')
        vcard.add('adr').type_param = address.type.type
    for tel in PhoneNumber.objects.filter(person=p):
        vcard.add('tel').value = tel.number

    vcardstream = vcard.serialize()

    response = HttpResponse(vcardstream, mimetype='text/x-vcard')
    response['Filename'] = p.user.username+'.vcf'  # IE needs this
    response['Content-Disposition'] = 'attachment; filename='+p.user.username+'.vcf'

    return response

def findParamsForFieldName(fieldName):
    for fieldNam, comps, formField in FIELD_PARAMS:
        if fieldNam==fieldName:
            return (fieldName, comps, formField)
    raise NotImplementedError
    return None

