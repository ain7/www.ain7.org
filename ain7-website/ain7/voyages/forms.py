# -*- coding: utf-8
#
# voyages/forms.py
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

from django import forms
from django.db import models
from django.utils.translation import ugettext as _

from ain7.fields import AutoCompleteField
from ain7.voyages.models import Travel, Subscription, TravelResponsible
from ain7.widgets import DateTimeWidget

dateWidget = DateTimeWidget()
dateWidget.dformat = '%d/%m/%Y'

class SearchTravelForm(forms.Form):
    label = forms.CharField(label=_('label').capitalize(),
        max_length=50, required=False)
    date = forms.CharField(label=_('date').capitalize(),
        max_length=50, required=False)
    visited_places = forms.CharField(label=_('visited places').capitalize(),
        max_length=50, required=False)
    search_old_travel = forms.BooleanField(
        label=_('search in old travels').capitalize(), required=False)

    def __init__(self, *args, **kwargs):
        super(SearchTravelForm, self).__init__(*args, **kwargs)

    def search(self):
        criteria={
            'label__contains':self.cleaned_data['label'],
            'date__contains':self.cleaned_data['date']}
        # visited places are also searched in labels
        visited = self.cleaned_data['visited_places']
        q_visited = \
            models.Q(visited_places__contains = visited) | \
            models.Q(label__contains = visited)
        if not self.cleaned_data['search_old_travel']:
            criteria['start_date__gte'] = datetime.now()
        return Travel.objects.filter(**criteria).filter(q_visited)


class TravelForm(forms.ModelForm):
    description = forms.CharField(label=_('description').capitalize(),
        required=False,
        widget=forms.widgets.Textarea(attrs={'rows':10, 'cols':90}))
    report = forms.CharField(label=_('report').capitalize(),
        required=False, 
        widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':90}))
    start_date = forms.DateTimeField(label=_('start date').capitalize(),
        widget=dateWidget)
    end_date = forms.DateTimeField(label=_('end date').capitalize(),
        widget=dateWidget)
    
    def clean_end_date(self):
        if self.cleaned_data.get('start_date') and \
            self.cleaned_data.get('end_date') and \
            self.cleaned_data['start_date']>self.cleaned_data['end_date']:
            raise forms.ValidationError(_('Start date is later than end date'))
        return self.cleaned_data['end_date']

    class Meta:
        model = Travel


class JoinTravelForm(forms.ModelForm):
    
    class Meta:
        model = Subscription
        exclude = ('subscriber','travel')


class SubscribeTravelForm(forms.ModelForm):
    
    class Meta:
        model = Subscription
        exclude = ('travel')


class TravelResponsibleForm(forms.ModelForm):
    
    class Meta:
        model = TravelResponsible
        exclude = ('travel')
