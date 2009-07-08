# -*- coding: utf-8
#
# voyages/views.py
#
#   Copyright (C) 2007-2009 AIn7
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

from datetime import datetime

from django import forms
from django.db import models
from django.forms import widgets
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person
from ain7.decorators import confirmation_required
from ain7.pages.models import Text
from ain7.utils import ain7_render_to_response, ain7_generic_edit, ain7_generic_delete, check_access
from ain7.voyages.models import Travel, Subscription, TravelResponsible
from ain7.voyages.forms import *


def index(request):
    next_travels = Travel.objects.filter(
        start_date__gte=datetime.now()).order_by('-start_date')
    prev_travels = Travel.objects.filter(
        start_date__lt=datetime.now()).order_by('-start_date')[:5]
    text = Text.objects.get(textblock__shortname='voyages')
    return ain7_render_to_response(request, 'voyages/index.html',
        {'next_travels': next_travels, 'previous_travels': prev_travels, 'text': text})

@login_required
def add(request):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    return ain7_generic_edit(
        request, None, TravelForm, {}, 'voyages/edit.html',
        {'action': 'add', 'back': request.META.get('HTTP_REFERER', '/')},
        {}, '/voyages/', _('The travel has been successfully created.'))

@confirmation_required(
    lambda user_id=None,
    travel_id=None: str(get_object_or_404(Travel, pk=travel_id)),
    'voyages/base.html',
    _('Do you REALLY want to delete this travel'))
@login_required
def delete(request, travel_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    return ain7_generic_delete(request,
        get_object_or_404(Travel, pk=travel_id),
        '/voyages/', _('Travel successfully deleted.'))

def details(request,travel_id):
    t = get_object_or_404(Travel, pk=travel_id)
    return ain7_render_to_response(request, 'voyages/details.html',
        {'travel': t})

def list(request):
    return ain7_render_to_response(request, 'voyages/list.html',
                            {'travels': Travel.objects.all()})

def search(request):

    form = SearchTravelForm()
    nb_results_by_page = 25
    travels = False
    paginator = Paginator(Travel.objects.none(),nb_results_by_page)
    page = 1

    if request.method == 'POST':
        form = SearchTravelForm(request.POST)
        if form.is_valid():
            travels = form.search()
            paginator = Paginator(travels, nb_results_by_page)
            try:
                page =  int(request.GET.get('page', '1'))
                travels = paginator.page(page).object_list
            except InvalidPage:
                raise http.Http404
    return ain7_render_to_response(request, 'voyages/search.html',
        {'travels': travels, 'form': form, 'request': request,
         'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page,
         'next_page': page + 1, 'previous_page': page - 1,
         'pages': paginator.num_pages,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits' : paginator.count})

@login_required
def edit(request, travel_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    travel = Travel.objects.get(pk=travel_id)
    back = request.META.get('HTTP_REFERER', '/')
    return ain7_generic_edit(
        request, travel, TravelForm, {}, 'voyages/edit.html',
        {'action': 'edit', 'travel': travel, 'back': back}, {},
        '/voyages/%s/' % (travel.id),
        _("Modifications have been successfully saved."))

@confirmation_required(lambda travel_id=None, object_id=None : '', 'voyages/base.html', _('Do you really want to delete the thumbnail of this travel'))
@login_required
def thumbnail_delete(request, travel_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    travel = get_object_or_404(Travel, pk=travel_id)
    travel.thumbnail = None
    travel.logged_save(request.user.person)

    request.user.message_set.create(message=
        _('The thumbnail of this travel has been successfully deleted.'))
    return HttpResponseRedirect('/voyages/%s/edit/' % travel_id)

@login_required
def join(request, travel_id):

    r = check_access(request, request.user, ['ain7-member'])
    if r:
        return r

    travel = get_object_or_404(Travel, pk=travel_id)
    person = request.user.person

    if request.method == 'GET':
        # on vérifie que la personne n'est pas déjà inscrite
        already_subscribed = False
        for subscription in person.travel_subscriptions.all():
            if subscription.travel == travel:
                already_subscribed = True
        if already_subscribed:
            request.user.message_set.create(message=_('You have already subscribed to this travel.'))
            return HttpResponseRedirect('/voyages/%s/' % (travel.id))
        f = JoinTravelForm()
        back = request.META.get('HTTP_REFERER', '/')
        return ain7_render_to_response(request, "voyages/join.html",
            {'form': f, 'travel': travel, 'back': back})

    if request.method == 'POST':
        f = JoinTravelForm(request.POST.copy())
        if f.is_valid():
            f.cleaned_data['subscriber'] = person
            f.cleaned_data['travel'] = travel
            f.save()
            request.user.message_set.create(message=_('You have been successfully subscribed to this travel.'))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.')+str(f.errors))
        return HttpResponseRedirect('/voyages/%s/' % (travel.id))


@login_required
def subscribe(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    if request.method == 'GET':
        f = SubscribeTravelForm()
        # TODO : AJAX pour sélectionner une personne plutôt qu'une liste
        return ain7_render_to_response(request, "voyages/join.html",
            {'form': f, 'travel': travel,
             'back': request.META.get('HTTP_REFERER', '/')})

    if request.method == 'POST':
        f = SubscribeTravelForm(request.POST.copy())
        persons = Person.objects.filter(pk=request.POST['subscriber'])
        if not persons:
            return ain7_render_to_response(request, "voyages/join.html",
                {'form': f, 'travel': travel,
                 'back': request.META.get('HTTP_REFERER', '/')})
        person = persons[0]
        # on vérifie que la personne n'est pas déjà inscrite
        already_subscribed = False
        for subscription in person.travel_subscriptions.all():
            if subscription.travel == travel:
                already_subscribed = True
        if already_subscribed:
            request.user.message_set.create(message=_('This person is already subscribed to this travel.'))
            return ain7_render_to_response(request,
                'voyages/participants.html', {'travel': travel})
        else:
            if f.is_valid():
                f.cleaned_data['travel'] = travel
                f.cleaned_data['subscriber'] = person
                f.save()
                request.user.message_set.create(message=_('You have successfully subscribed someone to this travel.'))
            else:
                request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            return ain7_render_to_response(request,
                'voyages/participants.html', {'travel': travel})
    return HttpResponseRedirect('/voyages/%s/' % (travel.id))

@confirmation_required(
    lambda user_id=None, travel_id=None, participant_id=None:
    str(get_object_or_404(Person, pk=participant_id)),
    'voyages/base.html',
    _('Do you really want to unsubscribe this participant'))

@login_required
def unsubscribe(request, travel_id, participant_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    travel = get_object_or_404(Travel, pk=travel_id)
    participant = get_object_or_404(Person, pk=participant_id)
    subscription = get_object_or_404(Subscription, travel=travel, subscriber=participant_id)
    subscription.delete()
    return ain7_render_to_response(request, 'voyages/participants.html',
                            {'travel': travel})

@login_required
def participants(request, travel_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    travel = get_object_or_404(Travel, pk=travel_id)
    return ain7_render_to_response(request, 'voyages/participants.html',
        {'travel': travel})

@login_required
def responsibles(request, travel_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    travel = get_object_or_404(Travel, pk=travel_id)
    return ain7_render_to_response(request, 'voyages/responsibles.html',
        {'travel': travel})

@login_required
def responsibles_add(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    if request.method == 'GET':
        f = TravelResponsibleForm()
        back = request.META.get('HTTP_REFERER', '/')
        return ain7_render_to_response(request, "voyages/join.html",
                                {'form': f, 'travel': travel, 'back': back})

    if request.method == 'POST':
        f = TravelResponsibleForm(request.POST.copy())
        person = Person.objects.get(pk=request.POST['responsible'])
        # on vérifie que la personne n'est pas déjà inscrite
        already_responsible = False
        for responsibility in person.travel_responsibilities.all():
            if responsibility.travel == travel:
                already_responsible = True
        if already_responsible:
            request.user.message_set.create(message=_('This person is already responsible of this travel.'))
            return ain7_render_to_response(request,
                'voyages/responsibles.html', {'travel': travel})
        else:
            if f.is_valid():
                tr = TravelResponsible(travel=travel, responsible=person)
                tr.save()
                request.user.message_set.create(message=_('You have successfully added someone to responsibles of this travel.'))
            else:
                request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.')+str(f.errors))
            return ain7_render_to_response(request,
                'voyages/responsibles.html', {'travel': travel})
    return HttpResponseRedirect('/voyages/%s/' % (travel.id))

@confirmation_required(
    lambda user_id=None, travel_id=None, responsible_id=None:
    str(get_object_or_404(Person, pk=responsible_id)),
    'voyages/base.html',
    _('Do you really want this person not to be responsible of this travel'))
@login_required
def responsibles_delete(request, travel_id, responsible_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    travel = get_object_or_404(Travel, pk=travel_id)
    responsible = get_object_or_404(Person, pk=responsible_id)
    travelResponsible = get_object_or_404(TravelResponsible,
        responsible=responsible, travel=travel)
    travelResponsible.delete()
    return ain7_render_to_response(request, 'voyages/responsibles.html',
                            {'travel': travel})

