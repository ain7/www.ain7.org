# -*- coding: utf-8
""""
 ain7/voyages/forms.py
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

from datetime import datetime

from django import forms
from django.utils.translation import ugettext as _

from ain7.fields import AutoCompleteField
from ain7.voyages.models import Travel, Subscription, TravelResponsible
from ain7.widgets import DateTimeWidget


dateWidget = DateTimeWidget()
dateWidget.dformat = '%d/%m/%Y'

class SearchTravelForm(forms.Form):
    """ search travel form"""
    label = forms.CharField(label=_('label').capitalize(),
        max_length=50, required=False)
    visited_places = forms.CharField(label=_('visited places').capitalize(),
        max_length=50, required=False)
    search_old_travel = forms.BooleanField(
        label=_('search in old travels').capitalize(), required=False)

    def __init__(self, *args, **kwargs):
        """search form init method"""
        super(SearchTravelForm, self).__init__(*args, **kwargs)

    def search(self):
        """search method"""
        criteria = {
            'label__icontains': self.cleaned_data['label'],
            'label__icontains': self.cleaned_data['visited_places']}

        if not self.cleaned_data['search_old_travel']:
            criteria['start_date__gte'] = datetime.now()
        return Travel.objects.filter(**criteria)


class TravelForm(forms.ModelForm):
    """Travel form"""
    label = forms.CharField(label=_('label'), 
        widget=forms.TextInput(attrs={'size': 50}))
    description = forms.CharField(label=_('description').capitalize(),
        required=False,
        widget=forms.widgets.Textarea(attrs={'rows':10, 'cols':90}))
#    report = forms.CharField(label=_('report').capitalize(),required=False, 
#        widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':90}))
    start_date = forms.DateTimeField(label=_('start date').capitalize(),
         widget=dateWidget, required=False)
    end_date = forms.DateTimeField(label=_('end date').capitalize(),
         widget=dateWidget, required=False)
    
    def clean_end_date(self):
        """check dates in travel form method"""
        if self.cleaned_data.get('start_date') and \
            self.cleaned_data.get('end_date') and \
            self.cleaned_data['start_date']>self.cleaned_data['end_date']:
            raise forms.ValidationError(_('Start date is later than end date'))
        return self.cleaned_data['end_date']

    class Meta:
        """meta information for travel form"""
        model = Travel


class JoinTravelForm(forms.ModelForm):
    """Join Travel Form"""
    
    class Meta:
        """meta join travel form information"""
        model = Subscription
        exclude = ('subscriber','travel')


class SubscribeTravelForm(forms.ModelForm):
    """subscribe travel form"""
    subscriber = forms.IntegerField(label=_('Subscriber'), required=True,
        widget=AutoCompleteField(completed_obj_name='person'))
    
    class Meta:
        """meta subscribe travel form"""
        model = Subscription
        exclude = ('travel',)


class TravelResponsibleForm(forms.ModelForm):
    """travel responsible form"""
    responsible = forms.IntegerField(label=_('Responsible'), required=True,
         widget=AutoCompleteField(completed_obj_name='person'))
    
    class Meta:
        """meta travel responsible form"""
        model = TravelResponsible
        exclude = ('travel',)

