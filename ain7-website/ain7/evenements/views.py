# -*- coding: utf-8
#
# evenements/views.py
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
from django.contrib.auth.decorators import login_required
from django import newforms as forms
from django.template import RequestContext
from django.newforms import widgets
from django.http import HttpResponseRedirect

from ain7.annuaire.models import Person
from ain7.evenements.models import Event, EventSubscription

class JoinEventForm(forms.Form):
    subscriber_number = forms.IntegerField(label=_('Number of persons'))

class SubscribeEventForm(forms.Form):
    subscriber = forms.IntegerField(label=_('Person to subscribe'))
    subscriber_number = forms.IntegerField(label=_('Number of persons'))

class SearchEventForm(forms.Form):
    name = forms.CharField(label=_('Event name'), max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))
    place = forms.CharField(label=_('Place'), max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))

def index(request):
    events = Event.objects.all()[:5]
    return render_to_response('evenements/index.html', 
                             {'events': events, 'user': request.user},
                             context_instance=RequestContext(request))


def details(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render_to_response('evenements/details.html', 
                             {'event': event, 'user': request.user},
                             context_instance=RequestContext(request))

@login_required
def edit(request, event_id):

    event = get_object_or_404(Event, pk=event_id)

    EventForm = forms.models.form_for_instance(event)

    if request.method == 'POST':
        f = EventForm(request.POST.copy())
        if f.is_valid():
            f.save()

        request.user.message_set.create(message=_('Event successfully updated.'))

        return HttpResponseRedirect('/evenements/%s/' % (event.id))

    f = EventForm()

    return render_to_response('evenements/edit.html', 
                             {'form': f, 'event': event, 'user': request.user},
                             context_instance=RequestContext(request))

@login_required
def join(request, event_id):

    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        f = JoinEventForm(request.POST)
        if f.is_valid():
            subscription = EventSubscription()
            subscription.subscriber_number = request.POST['subscriber_number']
            subscription.subscriber = request.user.person
            subscription.event = event
            subscription.save()

        request.user.message_set.create(message=_('You have been successfully subscribed to this event.'))
        return HttpResponseRedirect('/evenements/%s/' % (event.id))

    f =  JoinEventForm()

    return render_to_response('evenements/join.html', 
                             {'event': event, 'form': f, 'user': request.user},
                             context_instance=RequestContext(request))

@login_required
def participants(request, event_id):

    event = get_object_or_404(Event, pk=event_id)

    return render_to_response('evenements/participants.html', 
                             {'event': event, 'user': request.user},
                             context_instance=RequestContext(request))

@login_required
def register(request):

    EventForm = forms.models.form_for_model(Event)

    if request.method == 'POST':
        f = EventForm(request.POST.copy())
        if f.is_valid():
            f.save()

        request.user.message_set.create(message=_('Event successfully added.'))

        #return HttpResponseRedirect('/evenements/%s/' % (f.id))
        return HttpResponseRedirect('/evenements/')

    f = EventForm()

    return render_to_response('evenements/register.html', 
                             {'form': f, 'user': request.user},
                             context_instance=RequestContext(request))

def search(request):

    if request.method == 'POST':
        form = SearchEventForm(request.POST)
        if form.is_valid():
                    list_events = Event.objects.filter(name__icontains=form.clean_data['name'],
                                                       place__icontains=form.clean_data['place'])

        return render_to_response('evenements/search.html', 
                                 {'form': form, 
                                  'list_events': list_events, 
                                  'request': request, 
                                  'user': request.user},
                                   context_instance=RequestContext(request))

    else:
        f = SearchEventForm()
        return render_to_response('evenements/search.html', 
                                 {'form': f , 'user': request.user}, 
                                 context_instance=RequestContext(request))

@login_required
def subscribe(request, event_id):

    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        f = SubscribeEventForm(request.POST)
        if f.is_valid():
            subscription = EventSubscription()
            subscription.subscriber_number = request.POST['subscriber_number']
            subscription.subscriber = Person.objects.filter(pk=request.POST['subscriber'])[0]
            subscription.event = event
            subscription.save()

        p = subscription.subscriber

        request.user.message_set.create(message=_('You have successfully subscribed '+p.first_name+' '+p.last_name+' to this event.'))
        return HttpResponseRedirect('/evenements/%s/' % (event.id))

    f =  SubscribeEventForm()

    return render_to_response('evenements/subscribe.html', 
                             {'event': event, 'form': f, 'user': request.user},
                             context_instance=RequestContext(request))

def validate(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render_to_response('evenements/validate.html', 
                             {'event': event, 'user': request.user},
                             context_instance=RequestContext(request))

