# -*- coding: utf-8
#
# evenements/views.py
#
#   Copyright © 2007-2009 AIn7 Devel Team
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

import datetime

from django import forms
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage
from django.core.mail import send_mail
from django.db import models
from django.forms import widgets
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person, Email
from ain7.decorators import confirmation_required
from ain7.evenements.models import Event, EventSubscription
from ain7.evenements.forms import *
from ain7.utils import ain7_render_to_response, ain7_generic_edit, ain7_generic_delete, check_access



def index(request):
    events = Event.objects.filter(date__gte=datetime.datetime.now())[:5]
    return ain7_render_to_response(request, 'evenements/index.html',
        {'events': events, 'event_list': Event.objects.all(),
         'next_events': Event.objects.next_events()})


def details(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return ain7_render_to_response(request, 'evenements/details.html',
        {'event': event, 'event_list': Event.objects.all(),'nbparticipants': event.nb_participants(),
         'next_events': Event.objects.next_events()})

@login_required
def edit(request, event_id):

    r = check_access(request, request.user, ['ain7-ca','ain7-secretariat','ain7-contributeur'])
    if r:
        return r

    event = get_object_or_404(Event, pk=event_id)
    return ain7_generic_edit(
        request, event, EventForm, {},
        'evenements/edit.html',
        {'event': event, 'back': request.META.get('HTTP_REFERER', '/'),
         'event_list': Event.objects.all(),
         'next_events': Event.objects.next_events()},
        {'contributor': request.user.person},
        '/evenements/%s/' % (event.id), _('Event successfully updated.'))

@confirmation_required(lambda event_id=None, object_id=None : '', 'evenements/base.html', _('Do you really want to delete the image of this event'))
@login_required
def image_delete(request, event_id):

    r = check_access(request, request.user, ['ain7-ca','ain7-secretariat','ain7-contributeur'])
    if r:
        return r

    event = get_object_or_404(Event, pk=event_id)
    event.image = None
    event.logged_save(request.user.person)

    request.user.message_set.create(message=
        _('The image of this event has been successfully deleted.'))
    return HttpResponseRedirect('/evenements/%s/edit/' % event_id)

@login_required
def join(request, event_id):

    event = get_object_or_404(Event, pk=event_id)

    r = check_access(request, request.user, ['ain7-membre','ain7-ca','ain7-secretariat','ain7-contributeur'])
    if r:
        return r

    if request.method == 'GET':
        # on vérifie que la personne n'est pas déjà inscrite
        person = request.user.person
        already_subscribed = False
        for subscription in person.event_subscriptions.all():
            if subscription.event == event:
                already_subscribed = True
        if already_subscribed:
            request.user.message_set.create(message=_('You have already subscribed to this event.'))
            return HttpResponseRedirect('/evenements/%s/' % event.id)
        
        return ain7_render_to_response(request, 'evenements/join.html',
            {'event': event, 'form': JoinEventForm(),
             'back': request.META.get('HTTP_REFERER', '/'),
             'event_list': Event.objects.all(),
             'next_events': Event.objects.next_events()})

    if request.method == 'POST':
        f = JoinEventForm(request.POST)
        if f.is_valid():
            f.save(subscriber=request.user.person, event=event)
            request.user.message_set.create(message=_('You have been successfully subscribed to this event.'))            
            return HttpResponseRedirect('/evenements/%s/' % (event.id))
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))
            return ain7_render_to_response(request, 'evenements/join.html',
                {'event': event, 'form': f,
                 'back': request.META.get('HTTP_REFERER', '/'),
                 'event_list': Event.objects.all(),
                 'next_events': Event.objects.next_events()})
            

@login_required
def participants(request, event_id):

    r = check_access(request, request.user, ['ain7-ca','ain7-secretariat','ain7-contributeur'])
    if r:
        return r

    event = get_object_or_404(Event, pk=event_id)
    return ain7_render_to_response(request, 'evenements/participants.html',
        {'event': event, 'nbparticipants': event.nb_participants()})

@login_required
def add(request):

    r = check_access(request, request.user, ['ain7-ca','ain7-secretariat','ain7-contributeur'])
    if r:
        return r

    return ain7_generic_edit(
        request, None, EventForm, {}, 'evenements/edit.html',
        {'back': request.META.get('HTTP_REFERER', '/'),
         'event_list': Event.objects.all(),
         'next_events': Event.objects.next_events()},
        {'contributor': request.user.person},
        '/evenements/$objid/edit/', _('Event successfully added. You can now add organizers.'))

def search(request):

    form = SearchEventForm()
    nb_results_by_page = 25
    list_events = False
    paginator = Paginator(Event.objects.none(),nb_results_by_page)
    page = 1

    if request.method == 'POST':
        form = SearchEventForm(request.POST)
        if form.is_valid():
            list_events = form.search()
            paginator = Paginator(list_events, nb_results_by_page)
            try:
                page = int(request.GET.get('page', '1'))
                list_events = paginator.page(page).object_list
            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'evenements/search.html',
        {'form': form, 'list_events': list_events, 'request': request,
         'event_list': Event.objects.all(),
         'next_events': Event.objects.next_events(),
         'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page,
         'next_page': page + 1, 'previous_page': page - 1,
         'pages': paginator.num_pages,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits' : paginator.count })

@login_required
def subscribe(request, event_id):

    r = check_access(request, request.user, ['ain7-ca','ain7-secretariat','ain7-contributeur'])
    if r:
        return r

    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'GET':
        return ain7_render_to_response(request, 'evenements/subscribe.html',
            {'event': event, 'form': SubscribeEventForm(),
             'back': request.META.get('HTTP_REFERER', '/'),
             'event_list': Event.objects.all(),
             'next_events': Event.objects.next_events()})

    if request.method == 'POST':
        f = SubscribeEventForm(request.POST)
        if f.is_valid():
            person = Person.objects.get(id=request.POST['subscriber'])
            # on vérifie que la personne n'est pas déjà inscrite
            already_subscribed = False
            for subscription in person.event_subscriptions.all():
                if subscription.event == event:
                    already_subscribed = True
            if already_subscribed:
                request.user.message_set.create(message=_('This person is already subscribed to this event.'))
                return ain7_render_to_response(request,
                    'evenements/subscribe.html',
                    {'event': event, 'form': SubscribeEventForm(),
                     'back': request.META.get('HTTP_REFERER', '/'),
                     'event_list': Event.objects.all(),
                     'next_events': Event.objects.next_events()})
            subscription = f.save(event=event,
                                  subscribed_by=request.user.person)
            p = subscription.subscriber
            request.user.message_set.create(
                message=_('You have successfully subscribed')+
                ' '+p.last_name+' '+p.first_name+' '+_('to this event.'))
            return HttpResponseRedirect('/evenements/%s/' % (event.id))
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))
            return ain7_render_to_response(request,
                'evenements/subscribe.html',
                {'event': event, 'form': f,
                 'back': request.META.get('HTTP_REFERER', '/'),
                 'event_list': Event.objects.all(),
                 'next_events': Event.objects.next_events()})

@login_required
def contact(request, event_id):

    event = get_object_or_404(Event, pk=event_id)

    r = check_access(request, request.user, ['ain7-membre','ain7-ca','ain7-secretariat','ain7-contributeur'])
    if r:
        return r

    if request.method == 'GET':
        p = request.user.person    
        try:
            email = Email.objects.get(person=p, preferred_email=True)
        except Email.DoesNotExist:
            f = ContactEventForm()
        else:
            f = ContactEventForm(initial={'sender': email})
        return ain7_render_to_response(request, 'evenements/contact.html',
            {'event': event, 'form': f,
             'back': request.META.get('HTTP_REFERER', '/'),
             'event_list': Event.objects.all(),
             'next_events': Event.objects.next_events()})

    if request.method == 'POST':
        f = ContactEventForm(request.POST)
        if f.is_valid():
            # Préparer le message et envoi au contact
            subject = '[ain7_event] ' + event.name
            sender = f.cleaned_data['sender']
            message = f.cleaned_data['message']
            send_mail(subject, message, sender, [event.contact_email], fail_silently=False)
                
            request.user.message_set.create(
                message=_('Your message has been sent to the event responsible.'))
            return HttpResponseRedirect('/evenements/%s/' % (event.id))
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No message sent."))
            return ain7_render_to_response(request,
                'evenements/contact.html',
                {'event': event, 'form': f,
                 'back': request.META.get('HTTP_REFERER', '/'),
                 'event_list': Event.objects.all(),
                 'next_events': Event.objects.next_events()})

def ical(request):

    list_events = Event.objects.filter(date__gte=datetime.datetime.now())

    cal = vobject.iCalendar()
    cal.add('method').value = 'PUBLISH'  # IE/Outlook needs this

    utc = vobject.icalendar.utc

    for event in list_events:
        ev = cal.add('vevent')
        ev.add('summary').value = event.name
        if event.location:
            ev.add('location').value = event.location
        if event.date:
            ev.add('dtstart').value = event.date
        #ev.add('dtend').value = event.end
        if event.description:
            ev.add('description').value = event.description
        if event.status:
            ev.add('status').value = event.get_status_display()
        if event.category:
            ev.add('category').value = event.description
        ev.add('dtstamp').value = event.last_change_at

    icalstream = cal.serialize()
    response = HttpResponse(icalstream, mimetype='text/calendar')
    response['Filename'] = 'ain7.ics'  # IE needs this
    response['Content-Disposition'] = 'attachment; filename=ain7.ics'

    return response

@login_required
def organizer_add(request, event_id):

    r = check_access(request, request.user, ['ain7-ca','ain7-secretariat','ain7-contributeur'])
    if r:
        return r

    event = get_object_or_404(Event, pk=event_id)
    return ain7_generic_edit(
        request, None, EventOrganizerForm, {},
        'evenements/organizer_add.html',
        {'back': request.META.get('HTTP_REFERER', '/'),
         'event_list': Event.objects.all(),
         'next_events': Event.objects.next_events()},
        {'contributor': request.user.person, 'event': event},
        '/evenements/%s/edit/' % event.id, _('Organizer successfully added.'))

@confirmation_required(lambda event_id=None, organizer_id=None : str(get_object_or_404(Person, pk=organizer_id)), 'evenements/base.html', _('Do you really want to remove this organizer'))
@login_required
def organizer_delete(request, event_id, organizer_id):

    r = check_access(request, request.user, ['ain7-ca','ain7-secretariat','ain7-contributeur'])
    if r:
        return r

    event = get_object_or_404(Event, pk=event_id)
    organizer = get_object_or_404(Person, pk=organizer_id)
    eventorg = event.event_organizers.get(organizer=organizer)
    if eventorg:
        eventorg.delete()
        request.user.message_set.create(
            message=_('Organizer successfully removed'))
    return HttpResponseRedirect('/evenements/%s/edit/' % event_id)

@login_required
def swap_email_notif(request, event_id, organizer_id):

    r = check_access(request, request.user, ['ain7-ca','ain7-secretariat','ain7-contributeur'])
    if r:
        return r

    event = get_object_or_404(Event, pk=event_id)
    organizer = get_object_or_404(Person, pk=organizer_id)
    eventorg = event.event_organizers.get(organizer=organizer)
    if eventorg:
        eventorg.send_email_for_new_subscriptions = \
            not(eventorg.send_email_for_new_subscriptions)
        eventorg.save()
    return HttpResponseRedirect('/evenements/%s/edit/' % event.id)
