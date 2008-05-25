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

from django import newforms as forms
from django.utils.translation import ugettext as _

from ain7.fields import AutoCompleteField
from ain7.widgets import DateTimeWidget
from ain7.evenements.models import *

dateTimeWidget = DateTimeWidget()
dateTimeWidget.dformat = '%d/%m/%Y %H:%M'

class JoinEventForm(forms.Form):
    subscriber_number = forms.IntegerField(label=_('Number of persons'))

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

class SearchEventForm(forms.Form):
    name = forms.CharField(label=_('Event name'), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'50'}))
    location = forms.CharField(label=_('Location'), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'50'}))


class EventForm(forms.ModelForm):
    description = forms.CharField( label=_('description').capitalize(),
        required=False,
        widget=forms.widgets.Textarea(attrs={'rows':10, 'cols':70}))
    question = forms.CharField( label=_('question').capitalize(),
        required=False, 
        widget=forms.widgets.Textarea(attrs={'rows':10, 'cols':70}))
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
