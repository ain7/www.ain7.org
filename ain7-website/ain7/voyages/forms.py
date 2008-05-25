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

from django import newforms as forms
from django.utils.translation import ugettext as _

from ain7.fields import AutoCompleteField
from ain7.voyages.models import *


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
    
    description = forms.CharField( required=False, 
        widget=forms.widgets.Textarea(attrs={'rows':10, 'cols':90}))
    report = forms.CharField( required=False, 
        widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':90}))

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
