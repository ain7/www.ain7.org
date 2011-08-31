# -*- coding: utf-8
"""
 ain7/voyages/views.py
"""
#
#   Copyright © 2007-2011 AIn7
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

from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person
from ain7.decorators import access_required, confirmation_required
from ain7.pages.models import Text
from ain7.utils import ain7_generic_delete
from ain7.voyages.models import Travel, Subscription, TravelResponsible
from ain7.voyages.forms import SearchTravelForm, TravelForm, JoinTravelForm,\
                               SubscribeTravelForm, TravelResponsibleForm


def index(request):
    """index"""
    next_travels = Travel.objects.filter(
        start_date__gte=datetime.now()).order_by('-start_date')
    prev_travels = Travel.objects.filter(
        start_date__lt=datetime.now()).order_by('-start_date')[:5]
    text = Text.objects.get(textblock__shortname='voyages')
    return render(request, 'voyages/index.html',
        {'next_travels': next_travels, 'previous_travels': prev_travels,
         'text': text})

@confirmation_required(
    lambda user_id = None,
    travel_id = None: str(get_object_or_404(Travel, pk=travel_id)),
    'voyages/base.html',
    _('Do you REALLY want to delete this travel'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def delete(request, travel_id):
    """delete travel"""

    return ain7_generic_delete(request,
        get_object_or_404(Travel, pk=travel_id),
        '/voyages/', _('Travel successfully deleted.'))

def details(request, travel_id):
    """travel details"""
    travel = get_object_or_404(Travel, pk=travel_id)
    return render(request, 'voyages/details.html',
        {'travel': travel})

def list(request):
    """upcoming travels list"""
    return render(request, 'voyages/list.html',
        {'travels': Travel.objects.exclude(end_date__lte=datetime.now())})

def search(request):
    """search travels form"""

    form = SearchTravelForm()
    nb_results_by_page = 25
    travels = False
    paginator = Paginator(Travel.objects.none(), nb_results_by_page)
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
                raise Http404
    return render(request, 'voyages/search.html',
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

@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def edit(request, travel_id=None):
    """edit travel"""

    form = TravelForm()
    travel = None

    if travel_id:
        travel = Travel.objects.get(pk=travel_id)
        form = TravelForm(instance=travel)

    if request.method == 'POST':
        if travel_id:
            form = TravelForm(request.POST, request.FILES, instance=travel)
        else:
            form = TravelForm(request.POST, request.FILES)

        if form.is_valid():
            trav = form.save()
            request.user.message_set.create(message=_('Modifications have been\
 successfully saved.'))

            return HttpResponseRedirect(reverse(details, args=[trav.id]))

    return render(
        request, 'voyages/edit.html',
        {'form': form, 'action_title': _("Modification of personal data for"),
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda travel_id=None, object_id=None : '',
    'voyages/base.html', 
     _('Do you really want to delete the thumbnail of this travel'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def thumbnail_delete(request, travel_id):
    """remove travel thumbnail"""

    travel = get_object_or_404(Travel, pk=travel_id)
    travel.thumbnail = None
    travel.logged_save(request.user.person)

    request.user.message_set.create(message=
        _('The thumbnail of this travel has been successfully deleted.'))
    return HttpResponseRedirect('/voyages/%s/edit/' % travel_id)

@access_required(groups=['ain7-membre'])
def join(request, travel_id):
    """join travel"""

    travel = get_object_or_404(Travel, pk=travel_id)
    person = request.user.person

    if request.method == 'GET':
        # on vérifie que la personne n'est pas déjà inscrite
        already_subscribed = False
        for subscription in person.travel_subscriptions.all():
            if subscription.travel == travel:
                already_subscribed = True
        if already_subscribed:
            request.user.message_set.create(
                message=_('You have already subscribed to this travel.'))
            return HttpResponseRedirect('/voyages/%s/' % (travel.id))
        form = JoinTravelForm()
        back = request.META.get('HTTP_REFERER', '/')
        return render(request, "voyages/join.html",
            {'form': form, 'travel': travel, 'back': back})

    if request.method == 'POST':
        form = JoinTravelForm(request.POST.copy())
        if form.is_valid():
            form.cleaned_data['subscriber'] = person
            form.cleaned_data['travel'] = travel
            form.save()
            request.user.message_set.create(message=
                _('You have been successfully subscribed to this travel.'))
        else:
            request.user.message_set.create(message=
                _('Something was wrong in the form you filled. No modification\
 done.') + str(form.errors))
        return HttpResponseRedirect('/voyages/%s/' % (travel.id))


@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def subscribe(request, travel_id):
    """subscribe someone to a travel"""

    travel = get_object_or_404(Travel, pk=travel_id)

    if request.method == 'GET':
        form = SubscribeTravelForm()
        # TODO : AJAX pour sélectionner une personne plutôt qu'une liste
        return render(request, "voyages/join.html",
            {'form': form, 'travel': travel,
             'back': request.META.get('HTTP_REFERER', '/')})

    if request.method == 'POST':
        form = SubscribeTravelForm(request.POST.copy())
        persons = Person.objects.filter(pk=request.POST['subscriber'])
        if not persons:
            return render(request, "voyages/join.html",
                {'form': form, 'travel': travel,
                 'back': request.META.get('HTTP_REFERER', '/')})
        person = persons[0]
        # on vérifie que la personne n'est pas déjà inscrite
        already_subscribed = False
        for subscription in person.travel_subscriptions.all():
            if subscription.travel == travel:
                already_subscribed = True
        if already_subscribed:
            request.user.message_set.create(message=
                _('This person is already subscribed to this travel.'))
            return render(request,
                'voyages/participants.html', {'travel': travel})
        else:
            if form.is_valid():
                form.cleaned_data['travel'] = travel
                form.cleaned_data['subscriber'] = person
                form.save()
                request.user.message_set.create(message=_('You have\
 successfully subscribed someone to this travel.'))
            else:
                request.user.message_set.create(message=_('Something was\
 wrong in the form you filled. No modification done.'))
            return render(request,
                'voyages/participants.html', {'travel': travel})
    return HttpResponseRedirect('/voyages/%s/' % (travel.id))

@confirmation_required(
    lambda user_id=None, travel_id=None, participant_id=None:
    str(get_object_or_404(Person, pk=participant_id)),
    'voyages/base.html',
    _('Do you really want to unsubscribe this participant'))

@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def unsubscribe(request, travel_id, participant_id):
    """unsubscribe someone from a travel"""

    travel = get_object_or_404(Travel, pk=travel_id)
    participant = get_object_or_404(Person, pk=participant_id)
    subscription = get_object_or_404(Subscription, travel=travel,
        subscriber=participant.id)
    subscription.delete()
    return render(request, 'voyages/participants.html',
                            {'travel': travel})

@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def participants(request, travel_id):
    """travel participants list"""

    travel = get_object_or_404(Travel, pk=travel_id)
    return render(request, 'voyages/participants.html',
        {'travel': travel})

@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def responsibles(request, travel_id):
    """travels responsibles"""

    travel = get_object_or_404(Travel, pk=travel_id)
    return render(request, 'voyages/responsibles.html',
        {'travel': travel})

@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def responsibles_add(request, travel_id):
    """travel responsible add"""

    travel = get_object_or_404(Travel, pk=travel_id)

    if request.method == 'GET':
        form = TravelResponsibleForm()
        back = request.META.get('HTTP_REFERER', '/')
        return render(request, "voyages/join.html",
            {'form': form, 'travel': travel, 'back': back})

    if request.method == 'POST':
        form = TravelResponsibleForm(request.POST.copy())
        person = Person.objects.get(pk=request.POST['responsible'])
        # on vérifie que la personne n'est pas déjà inscrite
        already_responsible = False
        for responsibility in person.travel_responsibilities.all():
            if responsibility.travel == travel:
                already_responsible = True
        if already_responsible:
            request.user.message_set.create(message=
                _('This person is already responsible of this travel.'))
            return render(request,
                'voyages/responsibles.html', {'travel': travel})
        else:
            if form.is_valid():
                travel_responsible = TravelResponsible(travel=travel,
                    responsible=person)
                travel_responsible.save()
                request.user.message_set.create(message=_('You have\
 successfully added someone to responsibles of this travel.'))
            else:
                request.user.message_set.create(message=_('Something was wrong\
 in the form you filled. No modification done.') + str(form.errors))
            return render(request,
                'voyages/responsibles.html', {'travel': travel})
    return HttpResponseRedirect('/voyages/%s/' % (travel.id))

@confirmation_required(
    lambda user_id=None, travel_id=None, responsible_id=None:
    str(get_object_or_404(Person, pk=responsible_id)),
    'voyages/base.html',
    _('Do you really want this person not to be responsible of this travel'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def responsibles_delete(request, travel_id, responsible_id):
    """travel responsible delete"""

    travel = get_object_or_404(Travel, pk=travel_id)
    responsible = get_object_or_404(Person, pk=responsible_id)
    travel_responsible = get_object_or_404(TravelResponsible,
        responsible=responsible, travel=travel)
    travel_responsible.delete()
    return render(request, 'voyages/responsibles.html',
                            {'travel': travel})

