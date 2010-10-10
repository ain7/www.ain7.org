# -*- coding: utf-8
"""
 ain7/news/views.py
"""
#
#   Copyright © 2007-2010 AIn7 Devel Team
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

import datetime
import vobject

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Email
from ain7.decorators import confirmation_required
from ain7.news.models import NewsItem, RSVPAnswer
from ain7.news.forms import SearchNewsForm, NewsForm, EventForm, \
     SearchEventForm, ContactEventForm, EventOrganizerForm
from ain7.utils import ain7_render_to_response, check_access


def index(request):
    """news index page"""
    news = NewsItem.objects.filter(date__isnull=True).\
        order_by('-creation_date')[:20]
    return ain7_render_to_response(request, 'news/index.html', {'news': news })

def details(request, news_slug):
    """news details"""
    news_item = get_object_or_404(NewsItem, slug=news_slug)
    return ain7_render_to_response(request, 'news/details.html',
                            {'news_item': news_item})

@login_required
def edit(request, news_slug=None):
    """news edit"""

    access = check_access(request, request.user,
       ['ain7-ca','ain7-secretariat','ain7-contributeur'])
    if access:
        return access

    news_item = None
    form = NewsForm()

    if news_slug:
        news_item = get_object_or_404(NewsItem, slug=news_slug)
        form = NewsForm(instance=news_item)

    if request.method == 'POST':
        if news_slug:
            form = NewsForm(request.POST, request.FILES, instance=news_item)
        else:
            form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news_item = form.save()
            news_item.logged_save(request.user.person)
            request.user.message_set.create(message=_('Modifications have been\
 successfully saved.'))

            return HttpResponseRedirect(reverse(details, args=[news_item.slug]))

    return ain7_render_to_response(
        request, 'news/edit.html',
        {'form': form, 'title': _("News edition"), 'news_item': news_item,
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda news_slug=None, object_id=None: '', 
     'base.html', 
     _('Do you really want to delete the image of this news'))
@login_required
def image_delete(request, news_slug):
    """news image delete"""

    access = check_access(request, request.user, 
        ['ain7-ca','ain7-secretariat','ain7-contributeur'])
    if access:
        return access

    news_item = get_object_or_404(NewsItem, slug=news_slug)
    news_item.image = None
    news_item.logged_save(request.user.person)

    request.user.message_set.create(message=
        _('The image of this news item has been successfully deleted.'))
    return HttpResponseRedirect('/actualites/%s/edit/' % news_slug)

@confirmation_required(lambda news_slug=None, object_id=None: '', 
    'base.html', 
    _('Do you really want to delete this news'))
@login_required
def delete(request, news_slug):
    """news delete"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat', 'ain7-contributeur'])
    if access:
        return access

    news_item = get_object_or_404(NewsItem, slug=news_slug)
    news_item.delete()

    request.user.message_set.create(message=
        _('The news has been successfully deleted.'))
    return HttpResponseRedirect('/actualites/')

def search(request):
    """news search"""

    form = SearchNewsForm()
    nb_results_by_page = 25
    list_news = False
    paginator = Paginator(NewsItem.objects.none(), nb_results_by_page)
    page = 1

    if request.method == 'POST':
        form = SearchNewsForm(request.POST)
        if form.is_valid():
            list_news = form.search()
            paginator = Paginator(list_news, nb_results_by_page)

            try:
                page = int(request.GET.get('page', '1'))
                list_news = paginator.page(page).object_list

            except InvalidPage:
                raise Http404

    return ain7_render_to_response(request, 'news/search.html',
        {'form': form, 'list_news': list_news,
         'request': request,'paginator': paginator,
         'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page,
         'next_page': page + 1, 'previous_page': page - 1,
         'pages': paginator.num_pages,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits' : paginator.count})

def event_index(request):
    """event index"""
    events = NewsItem.objects.filter(date__gte=datetime.datetime.now()).\
        order_by('date')[:5]
    return ain7_render_to_response(request, 'evenements/index.html',
        {'events': events, 
         'event_list': NewsItem.objects.filter(date__isnull=False),
         'next_events': NewsItem.objects.next_events()})


def event_details(request, event_id):
    """event details"""
    event = get_object_or_404(NewsItem, pk=event_id)

    rsvp = None
    if RSVPAnswer.objects.filter(person=request.user.person, event=event).count() == 1:
        rsvp = RSVPAnswer.objects.get(person=request.user.person, event=event)

    return ain7_render_to_response(request, 'evenements/details.html',
        {'event': event, 
         'event_list': NewsItem.objects.filter(date__isnull=False),
         'next_events': NewsItem.objects.next_events(),
         'rsvp': rsvp})

@login_required
def event_edit(request, event_id):
    """event edit"""

    access = check_access(request, request.user, 
        ['ain7-ca','ain7-secretariat','ain7-contributeur'])
    if access:
        return access

    event = get_object_or_404(NewsItem, pk=event_id)
    form = EventForm(instance=event)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            evt = form.save()
            evt.logged_save(request.user.person)
            request.user.message_set.create(message=_('Modifications have been\
 successfully saved.'))

        return HttpResponseRedirect(
            '/evenements/%s/' % event_id)

    return ain7_render_to_response(
        request, 'evenements/edit.html',
        {'form': form, 'action_title': _("Modification of event"),
         'event': event,
         'event_list': NewsItem.objects.all(),
         'next_events': NewsItem.objects.next_events(),
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda event_id=None, object_id=None : '', 
    'evenements/base.html', 
    _('Do you really want to delete the image of this event'))
@login_required
def event_image_delete(request, event_id):
    """event image delete"""

    access = check_access(request, request.user,
        ['ain7-ca','ain7-secretariat','ain7-contributeur'])
    if access:
        return access

    event = get_object_or_404(NewsItem, pk=event_id)
    event.image = None
    event.logged_save(request.user.person)

    request.user.message_set.create(message=
        _('The image of this event has been successfully deleted.'))
    return HttpResponseRedirect('/evenements/%s/edit/' % event_id)

@login_required
def event_add(request):
    """event add"""

    access = check_access(request, request.user,
        ['ain7-ca','ain7-secretariat','ain7-contributeur'])
    if access:
        return access

    form = EventForm()

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            evt = form.save()
            evt.logged_save(request.user.person)
            request.user.message_set.create(message=_('Modifications have been\
 successfully saved.'))

            return HttpResponseRedirect('/evenements/%s/' % evt.id)

    return ain7_render_to_response(
        request, 'evenements/edit.html',
        {'form': form, 'action_title': _("New event registration"),
         'event_list': NewsItem.objects.all(),
         'next_events': NewsItem.objects.next_events(),
         'back': request.META.get('HTTP_REFERER', '/')})

def event_attendees(request, event_id):

    access = check_access(request, request.user,
        ['ain7-ca','ain7-secretariat','ain7-contributeur'])
    if access:
        return access

    event = get_object_or_404(NewsItem, pk=event_id)

    attendees_yes = RSVPAnswer.objects.filter(event=event, yes=True)
    attendees_no = RSVPAnswer.objects.filter(event=event, no=True)
    attendees_maybe = RSVPAnswer.objects.filter(event=event, maybe=True)

    return ain7_render_to_response(
        request, 'evenements/attendees.html',
        {'attendees_yes': attendees_yes,
         'attendees_no': attendees_no,
         'attendees_maybe': attendees_maybe,
         'back': request.META.get('HTTP_REFERER', '/'),
         'event': event})

def event_attend_yes(request, event_id):
    """event details"""

    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-membre'])
    if access:
        return access

    event = get_object_or_404(NewsItem, pk=event_id)

    event.rsvp_answer(request.user.person, yes=True)

    return HttpResponseRedirect(reverse('ain7.news.views.event_details', 
        args=[event.id]))

def event_attend_no(request, event_id):
    """event details"""

    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-membre'])
    if access:
        return access

    event = get_object_or_404(NewsItem, pk=event_id)

    event.rsvp_answer(request.user.person, no=True)

    return HttpResponseRedirect(reverse('ain7.news.views.event_details', 
        args=[event.id]))

def event_attend_maybe(request, event_id):
    """event details"""

    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-membre'])
    if access:
        return access

    event = get_object_or_404(NewsItem, pk=event_id)

    event.rsvp_answer(request.user.person, maybe=True)

    return HttpResponseRedirect(reverse('ain7.news.views.event_details', 
        args=[event.id]))

def event_search(request):
    """event search"""

    form = SearchEventForm()
    nb_results_by_page = 25
    list_events = False
    paginator = Paginator(NewsItem.objects.none(), nb_results_by_page)
    page = 1

    if request.GET.has_key('location') or request.GET.has_key('title'):
        form = SearchEventForm(request.GET)
        if form.is_valid():
            list_events = form.search()
            paginator = Paginator(list_events, nb_results_by_page)
            try:
                page = int(request.GET.get('page', '1'))
                list_events = paginator.page(page).object_list
            except InvalidPage:
                raise Http404

    return ain7_render_to_response(request, 'evenements/search.html',
        {'form': form, 'list_events': list_events, 'request': request,
         'event_list': NewsItem.objects.all(),
         'next_events': NewsItem.objects.next_events(),
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
def event_contact(request, event_id):
    """event contact"""

    event = get_object_or_404(NewsItem, pk=event_id)

    access = check_access(request, request.user,
        ['ain7-membre','ain7-ca','ain7-secretariat','ain7-contributeur'])
    if access:
        return access

    if request.method == 'GET':
        person = request.user.person    
        try:
            email = Email.objects.get(person=person, preferred_email=True)
        except Email.DoesNotExist:
            form = ContactEventForm()
        else:
            form = ContactEventForm(initial={'sender': email})
        return ain7_render_to_response(request, 'evenements/contact.html',
            {'event': event, 'form': form,
             'back': request.META.get('HTTP_REFERER', '/'),
             'event_list': NewsItem.objects.filter(date__isnull=False),
             'next_events': NewsItem.objects.next_events()})

    if request.method == 'POST':
        form = ContactEventForm(request.POST)
        if form.is_valid():
            # Préparer le message et envoi au contact
            subject = '[ain7_event] ' + event.title
            sender = form.cleaned_data['sender']
            message = form.cleaned_data['message']
            send_mail(subject, message, sender, [event.contact_email],
                fail_silently=False)
                
            request.user.message_set.create(message=_('Your message has been\
 sent to the event responsible.'))
            return HttpResponseRedirect('/evenements/%s/' % (event.id))
        else:
            request.user.message_set.create(message=_("Something was wrong in\
 the form you filled. No message sent."))
            return ain7_render_to_response(request,
                'evenements/contact.html',
                {'event': event, 'form': form,
                 'back': request.META.get('HTTP_REFERER', '/'),
                 'event_list': NewsItem.objects.filter(date__isnull=False),
                 'next_events': NewsItem.objects.next_events()})

def ical(request):
    """event iCal stream"""

    list_events = NewsItem.objects.filter(date__gte=datetime.datetime.now())

    cal = vobject.iCalendar()
    cal.add('method').value = 'PUBLISH'  # IE/Outlook needs this

    for event in list_events:
        evt = cal.add('vevent')
        evt.add('summary').value = event.title
        if event.location:
            evt.add('location').value = event.location
        if event.date:
            evt.add('dtstart').value = event.date
        #ev.add('dtend').value = event.end
        if event.body:
            evt.add('body').value = event.body
        if event.status:
            evt.add('status').value = event.get_status_display()
        evt.add('dtstamp').value = event.last_change_at

    icalstream = cal.serialize()
    response = HttpResponse(icalstream, mimetype='text/calendar')
    response['Filename'] = 'ain7.ics'  # IE needs this
    response['Content-Disposition'] = 'attachment; filename=ain7.ics'

    return response

@login_required
def event_organizer_add(request, event_id):
    """add organizer"""

    access = check_access(request, request.user,
        ['ain7-ca','ain7-secretariat','ain7-contributeur'])
    if access:
        return access

    event = get_object_or_404(NewsItem, pk=event_id)

    form = EventOrganizerForm()

    if request.method == 'POST':
        form = EventOrganizerForm(request.POST)
        if form.is_valid():
            evt = form.save()
            evt.logged_save(request.user.person)
            request.user.message_set.create(message=_('Modifications have been\
 successfully saved.'))

        return HttpResponseRedirect('/evenements/%s/' % event_id)

    return ain7_render_to_response(
        request, 'evenements/organizer_add.html',
        {'form': form, 'action_title': _("Adding organizer"),
         'event_list': NewsItem.objects.filter(date__isnull=False),
         'next_events': NewsItem.objects.next_events(),
         'back': request.META.get('HTTP_REFERER', '/')})

confirmation_required(lambda event_id=None, organizer_id=None : 
    str(get_object_or_404(Person, pk=organizer_id)), 
    'evenements/base.html', 
    _('Do you really want to remove this organizer'))
@login_required
def event_organizer_delete(request, event_id, organizer_id):
    """delete organizer"""

    access = check_access(request, request.user,
        ['ain7-ca','ain7-secretariat','ain7-contributeur'])
    if access:
        return access

    event = get_object_or_404(NewsItem, pk=event_id)
    organizer = get_object_or_404(Person, pk=organizer_id)
    eventorg = event.event_organizers.get(organizer=organizer)
    if eventorg:
        eventorg.delete()
        request.user.message_set.create(
            message=_('Organizer successfully removed'))
    return HttpResponseRedirect('/evenements/%s/edit/' % event_id)

@login_required
def event_swap_email_notif(request, event_id, organizer_id):
    """swap email notification"""

    access = check_access(request, request.user,
        ['ain7-ca','ain7-secretariat','ain7-contributeur'])
    if access:
        return access

    event = get_object_or_404(NewsItem, pk=event_id)
    organizer = get_object_or_404(Person, pk=organizer_id)
    eventorg = event.event_organizers.get(organizer=organizer)
    if eventorg:
        eventorg.send_email_for_new_subscriptions = \
           not(eventorg.send_email_for_new_subscriptions)
        eventorg.save()
    return HttpResponseRedirect('/evenements/%s/edit/' % event.id)

