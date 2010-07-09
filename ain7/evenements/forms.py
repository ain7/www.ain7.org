# -*- coding: utf-8 -*-
"""
 ain7/evenements/forms.py
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

from django import forms
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person
from ain7.evenements.models import EventOrganizer, EventSubscription, Event
from ain7.fields import AutoCompleteField
from ain7.widgets import DateTimeWidget
from ain7.utils import AIn7ModelForm, AIn7Form

DATE_TIME_WIDGET = DateTimeWidget()
DATE_TIME_WIDGET.dformat = '%d/%m/%Y %H:%M'

class JoinEventForm(forms.Form):
    """Join Event Form"""
    subscriber_number = forms.IntegerField(label=_('Number of persons'),
                                           required=True)
    note = forms.CharField(label=_('Note, question, etc..'), max_length=200,
        required=False, widget=forms.TextInput(attrs={'size':'40'}))

    def clean_subscriber_number(self, *args, **kwargs):
        """check we have at least one member"""
        if self.cleaned_data['subscriber_number'] < 1:
            raise forms.ValidationError(_('This number includes yourself, so it\
 should be at least 1.'))
        return self.cleaned_data['subscriber_number']

    def save(self, *args, **kwargs):
        """save event participation"""
        subscription = EventSubscription()
        subscription.subscriber_number = self.cleaned_data['subscriber_number']
        subscription.subscriber = kwargs['subscriber']
        subscription.event = kwargs['event']
        subscription.note = self.cleaned_data['note']
        subscription.subscribed_by = kwargs['subscriber']
        subscription.save()
        return subscription

class SubscribeEventForm(forms.Form):
    """subscribe event form"""
    subscriber = forms.IntegerField(label=_('Person to subscribe'),
        widget=AutoCompleteField(completed_obj_name='person'))
    subscriber_number = forms.IntegerField(label=_('Number of persons'))
    note = forms.CharField(label=_('Note, question, etc..'), max_length=200,
        required=False, widget=forms.TextInput(attrs={'size':'40'}))

    def clean_subscriber_number(self, *args, **kwargs):
        """On vérifie qu'il y a au moins une personne."""
        if self.cleaned_data['subscriber_number'] < 1:
            raise forms.ValidationError(_('This number includes the person you\
 subscribe, so it should be at least 1.'))
        return self.cleaned_data['subscriber_number']

    def save(self, *args, **kwargs):
        """subscribe event save"""
        subscription = EventSubscription()
        subscription.subscriber_number = self.cleaned_data['subscriber_number']
        subscription.subscriber = Person.objects.get(
            id=self.cleaned_data['subscriber'])
        subscription.event = kwargs['event']
        subscription.note = self.cleaned_data['note']
        subscription.subscribed_by = kwargs['subscribed_by']
        subscription.save()
        return subscription

class SearchEventForm(forms.Form):
    """search event form"""
    title = forms.CharField(label=_('Event title'), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'40'}))
    location = forms.CharField(label=_('Location'), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'40'}))

    def search(self):
        """search event method"""
        return Event.objects.filter(
            title__icontains=self.cleaned_data['title'],
            location__icontains=self.cleaned_data['location'])        

class ContactEventForm(AIn7Form):
    """contact event form"""
    message = forms.CharField( label=_('your message').capitalize(),
        required=True,
        widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':65}))
    sender = forms.EmailField( label=_('your email').capitalize(),
        required=True)

class EventForm(AIn7ModelForm):
    """event form"""
    title = forms.CharField(label=_('Title'), max_length=60,
        widget=forms.TextInput(attrs={'size':'60'}))
    body = forms.CharField( label=_('description').capitalize(),
        required=False,
        widget=forms.widgets.Textarea(attrs={'rows':10, 'cols':40}))
    date = forms.DateTimeField(label=_('date').capitalize(),
        widget=DATE_TIME_WIDGET)
    
    class Meta:
        """event form meta"""
        model = Event
        exclude = ('organizers',)

    def save(self, *args, **kwargs):
        """save event"""
        if kwargs.has_key('contributor'):
            contributor = kwargs['contributor']
            event = super(EventForm, self).save()
            event.logged_save(contributor)
        else:
            event = super(EventForm, self).save()            
        return event

class EventOrganizerForm(forms.ModelForm):
    """event organizer form"""
    organizer = forms.IntegerField(label=_('organizer').capitalize(),
        widget=AutoCompleteField(completed_obj_name='person'))
    
    class Meta:
        """event organizer form meta"""
        model = EventOrganizer
        exclude = ('event',)

    def save(self, *args, **kwargs):
        """event organizer form save"""
        if kwargs.has_key('contributor') and kwargs.has_key('event'):
            event = kwargs['event']
            event_org = EventOrganizer()
            event_org.event = event
            event_org.organizer = Person.objects.get(
                id=self.cleaned_data['organizer'])
            event_org.send_email_for_new_subscriptions = \
                self.cleaned_data['send_email_for_new_subscriptions']
            event_org.save()
            event.logged_save(kwargs['contributor'])
            return event_org
        return None

