# -*- coding: utf-8 -*-
#
# evenements/forms.py
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

from django import forms
from django.utils.translation import ugettext as _

from ain7.fields import AutoCompleteField
from ain7.widgets import DateTimeWidget
from ain7.evenements.models import *
from ain7.annuaire.models import UserContribution, UserContributionType

dateTimeWidget = DateTimeWidget()
dateTimeWidget.dformat = '%d/%m/%Y %H:%M'

class JoinEventForm(forms.Form):
    subscriber_number = forms.IntegerField(label=_('Number of persons'),
                                           required=True)

    def clean_subscriber_number(self, *args, **kwargs):
        """On vérifie qu'il y a au moins une personne."""
        if self.cleaned_data['subscriber_number']<1:
            raise forms.ValidationError(_('This number includes yourself, so it should be at least 1.'))
        return self.cleaned_data['subscriber_number']

    def save(self, *args, **kwargs):
        subscription = EventSubscription()
        subscription.subscriber_number = self.cleaned_data['subscriber_number']
        subscription.subscriber = kwargs['subscriber']
        subscription.event = kwargs['event']
        subscription.save()
        contrib_type=UserContributionType.objects.get(key='event_subcription')
        contrib=UserContribution(user=kwargs['subscriber'], type=contrib_type)
        contrib.save()
        return subscription

class SubscribeEventForm(forms.Form):
    subscriber = forms.IntegerField(label=_('Person to subscribe'))
    subscriber_number = forms.IntegerField(label=_('Number of persons'))

    def __init__(self, *args, **kwargs):
        personList = []
        for person in Person.objects.all():
            personList.append( (person.user.id, str(person)) )
        self.base_fields['subscriber'].widget = \
            forms.Select(choices=personList)
        super(SubscribeEventForm, self).__init__(*args, **kwargs)

    def clean_subscriber_number(self, *args, **kwargs):
        """On vérifie qu'il y a au moins une personne."""
        if self.cleaned_data['subscriber_number']<1:
            raise forms.ValidationError(_('This number includes the person you subscribe, so it should be at least 1.'))
        return self.cleaned_data['subscriber_number']

    def save(self, *args, **kwargs):
        subscription = EventSubscription()
        subscription.subscriber_number = self.cleaned_data['subscriber_number']
        subscription.subscriber = Person.objects.get(
            id=self.cleaned_data['subscriber'])
        subscription.event = kwargs['event']
        subscription.save()
        return subscription

class SearchEventForm(forms.Form):
    name = forms.CharField(label=_('Event name'), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'50'}))
    location = forms.CharField(label=_('Location'), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'50'}))

    def search(self):
        return Event.objects.filter(
            name__icontains=self.cleaned_data['name'],
            location__icontains=self.cleaned_data['location'])        

class EventForm(forms.ModelForm):
    description = forms.CharField( label=_('description').capitalize(),
        required=False,
        widget=forms.widgets.Textarea(attrs={'rows':10, 'cols':40}))
    question = forms.CharField( label=_('question').capitalize(),
        required=False, 
        widget=forms.widgets.Textarea(attrs={'rows':10, 'cols':40}))
    start = forms.DateTimeField(label=_('start').capitalize(),
        widget=dateTimeWidget)
    end = forms.DateTimeField(label=_('end').capitalize(),
        widget=dateTimeWidget)
    publication_start = forms.DateTimeField(
        label=_('publication start').capitalize(), widget=dateTimeWidget)
    publication_end = forms.DateTimeField(
        label=_('publication end').capitalize(), widget=dateTimeWidget)
    
    class Meta:
        model = Event

    def clean_end(self):
        if self.cleaned_data.get('start') and \
            self.cleaned_data.get('end') and \
            self.cleaned_data['start']>self.cleaned_data['end']:
            raise forms.ValidationError(_('Start date is later than end date'))
        return self.cleaned_data['end']

    def clean_publication_end(self):
        if self.cleaned_data.get('publication_start') and \
            self.cleaned_data.get('publication_end') and \
            self.cleaned_data['publication_start']>self.cleaned_data['publication_end']:
            raise forms.ValidationError(_('Start date is later than end date'))
        return self.cleaned_data['publication_end']

    def save(self, *args, **kwargs):
        event = super(EventForm, self).save()
        if kwargs.has_key('contributor'):
            contributor = kwargs['contributor']
            contrib_type = \
                UserContributionType.objects.get(key=u'event_register')
            contrib = UserContribution(user=contributor, type=contrib_type)
            contrib.save()
        return event

