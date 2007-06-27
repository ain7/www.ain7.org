# -*- coding: utf-8
#
# voyages/views.py
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

from django.shortcuts import get_object_or_404, render_to_response
from django import newforms as forms
from django.template import RequestContext
from django.newforms import widgets
from django.http import HttpResponseRedirect
from datetime import datetime
from django.contrib.auth.decorators import login_required
from ain7.decorators import confirmation_required

from ain7.voyages.models import Travel, Subscription
from ain7.annuaire.models import Person

def index(request):
    next_travels = Travel.objects.filter(start_date__gte=datetime.now())[:5]
    prev_travels = Travel.objects.filter(start_date__lt=datetime.now())[:5]
    return _render_response(request, 'voyages/index.html',
                            {'next_travels': next_travels,
                             'previous_travels': prev_travels})

@login_required
def add(request):
    # TODO
    return HttpResponseRedirect('/voyages/')

@confirmation_required(lambda user_id=None, travel_id=None: str(get_object_or_404(Travel, pk=travel_id)), 'voyages/base.html', _('Do you REALLY want to delete this travel'))
@login_required
def delete(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)
    travel.delete()
    return HttpResponseRedirect('/voyages/')

def detail(request,travel_id):
    t = get_object_or_404(Travel, pk=travel_id)
    past = t in Travel.objects.filter(start_date__lt=datetime.now())
    return _render_response(request, 'voyages/details.html',
                            {'travel': t, 'past': past})

def list(request):
    # TODO
    return HttpResponseRedirect('/voyages/')

@login_required
def edit(request, travel_id=None):
    if travel_id is None:
        TravelForm = forms.models.form_for_model(Travel)
        TravelForm.base_fields['description'].widget = \
            forms.widgets.Textarea(attrs={'rows':10, 'cols':90})
        TravelForm.base_fields['report'].widget = \
            forms.widgets.Textarea(attrs={'rows':15, 'cols':90})
        form = TravelForm()
    else:
        travel = Travel.objects.get(pk=travel_id)
        TravelForm = forms.models.form_for_instance(travel)
        TravelForm.base_fields['description'].widget = \
            forms.widgets.Textarea(attrs={'rows':15, 'cols':90})
        TravelForm.base_fields['report'].widget = \
            forms.widgets.Textarea(attrs={'rows':15, 'cols':90})
        form = TravelForm()
        if request.method == 'POST':
             form = TravelForm(request.POST)
             if form.is_valid():
                 form.save()
                 request.user.message_set.create(
                     message=_("Modifications have been successfully saved."))
                 return HttpResponseRedirect('/voyages/%s/' % (travel.id))
    return _render_response(request, 'voyages/edit.html', {'form': form})

@login_required
def join(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)

    if request.method == 'GET':
        person = request.user.person
        # on vérifie que la personne n'est pas déjà inscrite
        already_subscribed = False 
        for subscription in person.travel_subscriptions.all():
            if subscription.travel == travel:
                already_subscribed = True
        if already_subscribed:
            request.user.message_set.create(message=_('You have already subscribed to this travel.'))
            return HttpResponseRedirect('/voyages/%s/' % (travel.id))
        JoinTravelForm = forms.models.form_for_model(Subscription,
            formfield_callback=_join_callback)
        f = JoinTravelForm()
        return _render_response(request, "voyages/join.html",
                                {'form': f, 'travel': travel})
    
    if request.method == 'POST':
        JoinTravelForm = forms.models.form_for_model(Subscription,
            formfield_callback=_join_callback)
        f = JoinTravelForm(request.POST.copy())
        if f.is_valid():
            f.clean_data['subscriber'] = person
            f.clean_data['travel'] = travel
            f.save()
            request.user.message_set.create(message=_('You have been successfully subscribed to this travel.'))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
        return HttpResponseRedirect('/voyages/%s/' % (travel.id))


@login_required
def subscribe(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)

    if request.method == 'GET':
        SubscribeTravelForm = forms.models.form_for_model(Subscription,
            formfield_callback=_subscribe_callback)
        f = SubscribeTravelForm()
        # TODO : AJAX pour sélectionner une personne plutôt qu'une liste
        return _render_response(request, "voyages/join.html",
                                {'form': f, 'travel': travel})
    
    if request.method == 'POST':
        SubscribeTravelForm = forms.models.form_for_model(Subscription,
            formfield_callback=_subscribe_callback)
        f = SubscribeTravelForm(request.POST.copy())
        person = Person.objects.filter(pk=request.POST['subscriber'])[0]
        # on vérifie que la personne n'est pas déjà inscrite
        already_subscribed = False 
        for subscription in person.travel_subscriptions.all():
            if subscription.travel == travel:
                already_subscribed = True
        if already_subscribed:
            request.user.message_set.create(message=_('This person is already subscribed to this travel.'))
            return HttpResponseRedirect('/voyages/%s/' % (travel.id))
        else:
            if f.is_valid():
                f.clean_data['travel'] = travel
                f.save()
                request.user.message_set.create(message=_('You have successfully subscribed someone to this travel.'))
            else:
                request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            return _render_response(request, 'voyages/participants.html',
                                    {'travel': travel})
    return HttpResponseRedirect('/voyages/%s/' % (travel.id))

@confirmation_required(lambda user_id=None, travel_id=None, participant_id=None: str(get_object_or_404(Person, pk=participant_id)), 'voyages/base.html', _('Do you really want to unsubscribe this participant'))
@login_required
def unsubscribe(request, travel_id, participant_id):
    travel = get_object_or_404(Travel, pk=travel_id)
    participant = get_object_or_404(Person, pk=participant_id)
    subscription = get_object_or_404(Subscription, travel=travel, subscriber=participant_id)
    subscription.delete()
    return _render_response(request, 'voyages/participants.html',
                            {'travel': travel})

@login_required
def participants(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)
    return _render_response(request, 'voyages/participants.html',
                            {'travel': travel})

@login_required
def responsibles(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)
    return _render_response(request, 'voyages/responsibles.html',
                            {'travel': travel})

@login_required
def responsibles_add(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)
    # TODO
    return _render_response(request, 'voyages/responsibles.html',
                            {'travel': travel})

@login_required
def responsibles_delete(request, travel_id, responsible_id):
    travel = get_object_or_404(Travel, pk=travel_id)
    # TODO
    return _render_response(request, 'voyages/responsibles.html',
                            {'travel': travel})

# pour alléger les appels à render_to_response
# http://www.djangosnippets.org/snippets/3/
def _render_response(req, *args, **kwargs):
    kwargs['context_instance'] = RequestContext(req)
    return render_to_response(*args, **kwargs)

# une petite fonction pour exclure les champs
# subscriber travel
# des formulaires créés avec form_for_model et form_for_instance
def _join_callback(f, **args):
    exclude_fields = ('subscriber', 'travel')
    if f.name in exclude_fields:
        return None
    return f.formfield(**args)

def _subscribe_callback(f, **args):
    exclude_fields = ('travel')
    if f.name in exclude_fields:
        return None
    return f.formfield(**args)

