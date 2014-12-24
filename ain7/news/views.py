# -*- coding: utf-8
"""
 ain7/news/views.py
"""
#
#   Copyright © 2007-2015 AIn7 Devel Team
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

from django.contrib import messages
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Email, Person
from ain7.decorators import access_required, confirmation_required
from ain7.news.models import NewsItem, RSVPAnswer
from ain7.news.forms import SearchNewsForm, NewsForm, EventForm, \
     SearchEventForm, ContactEventForm, EventOrganizerForm, RSVPAnswerForm
from ain7.shop.models import Order, ShoppingCart, ShoppingCartItem


def index(request):
    """news index page"""
    news = NewsItem.objects.filter(date__isnull=True).\
        order_by('-creation_date')[:20]
    page_title = 'Actualités'
    return render(request, 'news/index.html', {'news': news, 'page_title': page_title })

def details(request, news_slug):
    """news details"""
    news_item = get_object_or_404(NewsItem, slug=news_slug)
    page_title = news_item.title
    return render(request, 'news/details.html',
                            {'news_item': news_item, 'page_title': page_title})

@access_required(groups=['ain7-ca','ain7-secretariat','ain7-contributeur'])
def edit(request, news_slug=None):
    """news edit"""

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
            messages.success(request, _('Modifications have been successfully saved.'))

            return HttpResponseRedirect(reverse(details, 
                args=[news_item.slug]))

    return render(
        request, 'news/edit.html',
        {'form': form, 'title': _("News edition"), 'news_item': news_item,
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda news_slug=None, object_id=None: '', 
     'base.html', 
     _('Do you really want to delete the image of this news'))
@access_required(groups=['ain7-ca','ain7-secretariat','ain7-contributeur'])
def image_delete(request, news_slug):
    """news image delete"""

    news_item = get_object_or_404(NewsItem, slug=news_slug)
    news_item.image = None
    news_item.logged_save(request.user.person)

    messages.success(request, _('The image of this news item has been successfully deleted.'))
    return HttpResponseRedirect('/actualites/%s/edit/' % news_slug)

@confirmation_required(lambda news_slug=None, object_id=None: '', 
    'base.html', 
    _('Do you really want to delete this news'))
@access_required(groups=['ain7-ca', 'ain7-secretariat', 'ain7-contributeur'])
def delete(request, news_slug):
    """news delete"""

    news_item = get_object_or_404(NewsItem, slug=news_slug)
    news_item.delete()

    messages.success(request, _('The news has been successfully deleted.'))
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

    return render(request, 'news/search.html',
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
        order_by('date')[:10]
    page_title = _('Events')
    return render(request, 'evenements/index.html',
        {'events': events, 
         'event_list': NewsItem.objects.filter(date__isnull=False),
         'next_events': NewsItem.objects.next_events(), 'page_title': page_title})

def event_details(request, event_id):
    """event details"""
    event = get_object_or_404(NewsItem, pk=event_id)

    rsvp = None
    if request.user.is_authenticated() and \
        RSVPAnswer.objects.filter(person=request.user.person, \
        event=event).count() == 1:
            rsvp = RSVPAnswer.objects.get(person=request.user.person, \
                event=event)

    today = datetime.date.today()
    now = datetime.datetime.now()

    if not event.date:
        return HttpResponseRedirect(reverse(details, args=[event.slug]))

    rsvp_display = event.date > now
    if rsvp_display and event.rsvp_begin:
        rsvp_display = rsvp_display and event.rsvp_begin < today
    if rsvp_display and event.rsvp_end:
        rsvp_display = rsvp_display and event.rsvp_end > today

    page_title = event.title

    return render(request, 'evenements/details.html',
        {'event': event, 
         'event_list': NewsItem.objects.filter(date__isnull=False),
         'next_events': NewsItem.objects.next_events(),
         'rsvp_display': rsvp_display,
         'rsvp': rsvp,
         'page_title': page_title})

@access_required(groups=['ain7-ca','ain7-secretariat','ain7-contributeur'])
def event_edit(request, event_id=None):
    """event edit"""

    form = EventForm()
    event = None

    if event_id:
        event = get_object_or_404(NewsItem, pk=event_id)
        form = EventForm(instance=event)

    if request.method == 'POST':
        if event_id:
            form = EventForm(request.POST, request.FILES, instance=event)
        else:
            form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            evt = form.save()
            evt.logged_save(request.user.person)
            messages.success(request, _('Event successfully saved'))

            return HttpResponseRedirect(reverse(event_details, args=[evt.id]))

    return render(
        request, 'evenements/edit.html',
        {'form': form, 
         'action_title': _("Event modification"),
         'event': event,
         'event_list': NewsItem.objects.all(),
         'next_events': NewsItem.objects.next_events(),
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda event_id=None, object_id=None : '', 
    'evenements/base.html', 
    _('Do you really want to delete the image of this event'))
@access_required(groups=['ain7-ca','ain7-secretariat','ain7-contributeur'])
def event_image_delete(request, event_id):
    """event image delete"""

    event = get_object_or_404(NewsItem, pk=event_id)
    event.image = None
    event.logged_save(request.user.person)

    messages.success(request, _('The image of this event has been successfully deleted.'))
    return HttpResponseRedirect(reverse(event_details, args=[event.id]))

@access_required(groups=['ain7-ca','ain7-secretariat','ain7-contributeur'])
def event_attendees(request, event_id):

    from django.db.models import Sum

    event = get_object_or_404(NewsItem, pk=event_id)

    attendees_yes = RSVPAnswer.objects.filter(event=event, yes=True)
    attendees_number = RSVPAnswer.objects.filter(event=event, 
        yes=True).aggregate(Sum('number'))['number__sum']
    attendees_no = RSVPAnswer.objects.filter(event=event, no=True)
    attendees_maybe = RSVPAnswer.objects.filter(event=event, maybe=True)

    return render(
        request, 'evenements/attendees.html',
        {'attendees_yes': attendees_yes,
         'attendees_number': attendees_number,
         'attendees_no': attendees_no,
         'attendees_maybe': attendees_maybe,
         'back': request.META.get('HTTP_REFERER', '/'),
         'event': event})

@access_required(groups=['ain7-ca','ain7-secretariat','ain7-contributeur'],
                 allow_rsvp=True)
def event_rsvp(request, event_id, rsvp_id=None):
    """RSVP answer to an event"""

    event = get_object_or_404(NewsItem, pk=event_id)
    myself = False

    form = RSVPAnswerForm()

    if rsvp_id:
        rsvpanswer = get_object_or_404(RSVPAnswer, pk=rsvp_id)
        if rsvpanswer.person == request.user.person:
            myself = True
        form = RSVPAnswerForm(instance=rsvpanswer, 
            edit_person=False, myself=myself)

    if request.method == 'POST':
        if rsvp_id:
            form = RSVPAnswerForm(request.POST, 
                instance=rsvpanswer, edit_person=False, myself=myself)
        else:
            form = RSVPAnswerForm(request.POST)
        if form.is_valid():
            rsvp = form.save(commit=False)
            rsvp.event = event
            rsvp.updated_by = request.user.person
            if not rsvp.id:
                rsvp.created_by = request.user.person
            rsvp.save()
            messages.success(request, _('RSVP successfully saved'))

            if not myself:
                return HttpResponseRedirect(\
                    reverse('ain7.news.views.event_attendees',
                    args=[event.id]))

            if event.package:

                shc = ShoppingCart()
                shc.person = request.user.person
                shc.save()

                sci = ShoppingCartItem()
                sci.shoppingcart = shc
                sci.package = event.package
                sci.quantity = rsvp.number
                sci.save()

                order = Order()
                order.shoppingcart = shc
                order.person = request.user.person
                order.save()

                if order.amount() > 0:
                    return HttpResponseRedirect(\
                        reverse('ain7.shop.views.order_pay',
                        args=[order.id]))

            return HttpResponseRedirect(\
                    reverse('ain7.news.views.event_details',
                    args=[event.id]))

    return render(
        request, 'evenements/rsvp.html',
        {'form': form, 
         'action_title': _("RSVP Answer"),
         'event': event,
         'back': request.META.get('HTTP_REFERER', '/')})

@access_required(groups=['ain7-secretariat', 'ain7-membre'])
def event_attend_yes(request, event_id):
    """event details"""

    event = get_object_or_404(NewsItem, pk=event_id)

    rsvp = event.rsvp_answer(request.user.person, yes=True)

    return HttpResponseRedirect(reverse('ain7.news.views.event_rsvp', 
        args=[event.id, rsvp.id]))

@access_required(groups=['ain7-secretariat', 'ain7-membre'])
def event_attend_no(request, event_id):
    """event details"""

    event = get_object_or_404(NewsItem, pk=event_id)

    event.rsvp_answer(request.user.person, no=True)

    return HttpResponseRedirect(reverse('ain7.news.views.event_details', 
        args=[event.id]))

@access_required(groups=['ain7-secretariat', 'ain7-membre'])
def event_attend_maybe(request, event_id):
    """event details"""

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

    return render(request, 'evenements/search.html',
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

@access_required(groups=['ain7-membre','ain7-ca','ain7-secretariat',
                         'ain7-contributeur'])
def event_contact(request, event_id):
    """event contact"""

    event = get_object_or_404(NewsItem, pk=event_id)

    if request.method == 'GET':
        person = request.user.person    
        try:
            email = Email.objects.get(person=person, preferred_email=True)
        except Email.DoesNotExist:
            form = ContactEventForm()
        else:
            form = ContactEventForm(initial={'sender': email})
        return render(request, 'evenements/contact.html',
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
                
            messages.success(request, _('Your message has been sent to the event responsible.'))
            return HttpResponseRedirect(reverse(event_details, args=[event_id]))
        else:
            messages.error(request, _("Something was wrong in the form you filled. No message sent."))
            return render(request,
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
            evt.add('description').value = event.body
        if event.status:
            evt.add('status').value = event.get_status_display()
        evt.add('dtstamp').value = event.last_change_at

    icalstream = cal.serialize()
    response = HttpResponse(icalstream, mimetype='text/calendar')
    response['Filename'] = 'ain7.ics'  # IE needs this
    response['Content-Disposition'] = 'attachment; filename=ain7.ics'

    return response

@access_required(groups=['ain7-ca','ain7-secretariat','ain7-contributeur'])
def event_organizer_add(request, event_id):
    """add organizer"""

    event = get_object_or_404(NewsItem, pk=event_id)

    form = EventOrganizerForm()

    if request.method == 'POST':
        form = EventOrganizerForm(request.POST)
        if form.is_valid():
            evt_org = form.save(commit=False)
            evt_org.event = event
            evt_org.save()
            messages.success(request, _('Modifications have been successfully saved.'))

        return HttpResponseRedirect(reverse(event_details, args=[event.id]))

    return render(
        request, 'evenements/organizer_add.html',
        {'form': form, 'action_title': _("Adding organizer"),
         'event_list': NewsItem.objects.filter(date__isnull=False),
         'next_events': NewsItem.objects.next_events(),
         'back': request.META.get('HTTP_REFERER', '/')})

confirmation_required(lambda event_id=None, organizer_id=None : 
    str(get_object_or_404(Person, pk=organizer_id)), 
    'evenements/base.html', 
    _('Do you really want to remove this organizer'))

@access_required(groups=['ain7-ca','ain7-secretariat','ain7-contributeur'])
def event_organizer_delete(request, event_id, organizer_id):
    """delete organizer"""

    event = get_object_or_404(NewsItem, pk=event_id)
    organizer = get_object_or_404(Person, pk=organizer_id)
    eventorg = event.event_organizers.get(organizer=organizer)
    if eventorg:
        eventorg.delete()
        messages.success(request, _('Organizer successfully removed'))
    return HttpResponseRedirect(reverse(event_edit, args=[event_id]))

@access_required(groups=['ain7-ca','ain7-secretariat','ain7-contributeur'])
def event_swap_email_notif(request, event_id, organizer_id):
    """swap email notification"""

    event = get_object_or_404(NewsItem, pk=event_id)
    organizer = get_object_or_404(Person, pk=organizer_id)
    eventorg = event.event_organizers.get(organizer=organizer)
    if eventorg:
        eventorg.send_email_for_new_subscriptions = \
           not(eventorg.send_email_for_new_subscriptions)
        eventorg.save()
    return HttpResponseRedirect(reverse(event_edit, args=[event_id]))

