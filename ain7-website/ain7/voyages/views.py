# -*- coding: utf-8
#
# voyages/views.py
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

from datetime import datetime

from django.shortcuts import get_object_or_404
from django import newforms as forms
from django.newforms import widgets
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import ObjectPaginator, InvalidPage
from django.db import models
from django.utils.translation import ugettext as _

from ain7.decorators import confirmation_required
from ain7.utils import ain7_render_to_response, ImgUploadForm
from ain7.voyages.models import Travel, Subscription, TravelResponsible
from ain7.voyages.forms import *
from ain7.annuaire.models import Person


def index(request):
    next_travels = Travel.objects.filter(start_date__gte=datetime.now())
    prev_travels = Travel.objects.filter(start_date__lt=datetime.now())[:5]
    return ain7_render_to_response(request, 'voyages/index.html',
                            {'next_travels': next_travels,
                             'previous_travels': prev_travels})

@login_required
def add(request):
    form = TravelForm()
    if request.method == 'POST':
        form = TravelForm(request.POST)
        if form.is_valid():
            form.cleaned_data['thumbnail'] = None
            form.save()
            request.user.message_set.create(
                message=_('The travel has been successfully created.'))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.')+str(form.errors))
        return HttpResponseRedirect('/voyages/')

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 'voyages/edit.html',
        {'form': form, 'action': 'add', 'back': back})

@confirmation_required(
    lambda user_id=None,
    travel_id=None: str(get_object_or_404(Travel, pk=travel_id)),
    'voyages/base.html',
    _('Do you REALLY want to delete this travel'))
@login_required
def delete(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)
    travel.delete()
    return HttpResponseRedirect('/voyages/')

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
    paginator = ObjectPaginator(Travel.objects.none(),nb_results_by_page)
    page = 1

    if request.method == 'POST':
        form = SearchTravelForm(request.POST)
        if form.is_valid():

            travels = form.search()
            paginator = ObjectPaginator(travels, nb_results_by_page)

            try:
                page =  int(request.GET.get('page', '1'))
                travels = paginator.get_page(page - 1)

            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'voyages/search.html',
                                    {'travels': travels, 'form': form, 'request': request,
                    'paginator': paginator, 'is_paginated': paginator.pages > 1,
                    'has_next': paginator.has_next_page(page - 1),
                    'has_previous': paginator.has_previous_page(page - 1),
                    'current_page': page,
                    'next_page': page + 1,
                    'previous_page': page - 1,
                    'pages': paginator.pages,
                    'first_result': (page - 1) * nb_results_by_page +1,
                    'last_result': min((page) * nb_results_by_page, paginator.hits),
                    'hits' : paginator.hits,})

@login_required
def edit(request, travel_id=None):
    travel = Travel.objects.get(pk=travel_id)
    thumbnail = travel.thumbnail
    form = TravelForm(instance=travel)
    if request.method == 'POST':
        form = TravelForm(request.POST, instance=travel)
        if form.is_valid():
            form.cleaned_data['thumbnail'] = thumbnail
            form.save()
            request.user.message_set.create(
                message=_("Modifications have been successfully saved."))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.')+str(form.errors))
        return HttpResponseRedirect('/voyages/%s/' % (travel.id))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 'voyages/edit.html',
        {'form': form, 'action': 'edit', 'travel': travel, 'back': back})

@login_required
def thumbnail_edit(request, travel_id):

    travel = get_object_or_404(Travel, pk=travel_id)

    if request.method == 'GET':
        form = ImgUploadForm()
        filename = None
        if travel.thumbnail:
            filename = '/site_media/%s' % travel.thumbnail
        return ain7_render_to_response(request, 'pages/image.html',
            {'section': 'voyages/base.html',
             'name': _("thumbnail").capitalize(), 'form': form,
             'filename': filename})
    else:
        post = request.POST.copy()
        post.update(request.FILES)
        form = ImgUploadForm(post)
        if form.is_valid():
            travel.save_thumbnail_file(
                form.cleaned_data['img_file']['filename'],
                form.cleaned_data['img_file']['content'])
            request.user.message_set.create(message=_("The picture has been successfully changed."))
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done.")+str(form.errors))
        return HttpResponseRedirect('/voyages/%s/edit/' % travel_id)

@confirmation_required(lambda travel_id=None, object_id=None : '', 'voyages/base.html', _('Do you really want to delete the thumbnail of this travel'))
@login_required
def thumbnail_delete(request, travel_id):

    travel = get_object_or_404(Travel, pk=travel_id)
    travel.thumbnail = None
    travel.save()

    request.user.message_set.create(message=
        _('The thumbnail of this travel has been successfully deleted.'))
    return HttpResponseRedirect('/voyages/%s/edit/' % travel_id)

@login_required
def join(request, travel_id):
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

    if request.method == 'GET':
        f = SubscribeTravelForm()
        # TODO : AJAX pour sélectionner une personne plutôt qu'une liste
        return ain7_render_to_response(request, "voyages/join.html",
                                {'form': f, 'travel': travel})

    if request.method == 'POST':
        f = SubscribeTravelForm(request.POST.copy())
        person = Person.objects.filter(pk=request.POST['subscriber'])[0]
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
                f.save()
                request.user.message_set.create(message=_('You have successfully subscribed someone to this travel.'))
            else:
                request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.')+str(f.errors))
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
    travel = get_object_or_404(Travel, pk=travel_id)
    participant = get_object_or_404(Person, pk=participant_id)
    subscription = get_object_or_404(Subscription, travel=travel, subscriber=participant_id)
    subscription.delete()
    return ain7_render_to_response(request, 'voyages/participants.html',
                            {'travel': travel})

@login_required
def participants(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)
    return ain7_render_to_response(request, 'voyages/participants.html',
        {'travel': travel})

@login_required
def responsibles(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)
    return ain7_render_to_response(request, 'voyages/responsibles.html',
        {'travel': travel})

@login_required
def responsibles_add(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)

    if request.method == 'GET':
        f = TravelResponsibleForm()
        # TODO : AJAX pour sélectionner une personne plutôt qu'une liste
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
                f.cleaned_data['travel'] = travel
                f.save()
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
    travel = get_object_or_404(Travel, pk=travel_id)
    responsible = get_object_or_404(Person, pk=responsible_id)
    travelResponsible = get_object_or_404(TravelResponsible,
        responsible=responsible, travel=travel)
    travelResponsible.delete()
    return ain7_render_to_response(request, 'voyages/responsibles.html',
                            {'travel': travel})

