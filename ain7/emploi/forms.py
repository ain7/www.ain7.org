# -*- coding: utf-8
"""
 ain7/emploi/forms.py
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

from django.db import models
from django import forms
from django.utils.translation import ugettext as _

from ain7.emploi.models import JobOffer
from ain7.organizations.models import Office, Organization, \
                               OrganizationActivityField


class SearchJobForm(forms.Form):
    """search job form"""
    title = forms.CharField(label=_('title').capitalize(), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'40'}))
    activity_field = forms.IntegerField(label=_('Activity field'),
        required=False)
    experience = forms.CharField(label=_('experience').capitalize(),
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'size':'40'}))
    contract_type = forms.ChoiceField(label=_('Contract type'),
        required=False, choices=[])

    def __init__(self, *args, **kwargs):
        """init search job form"""
        super(SearchJobForm, self).__init__(*args, **kwargs)
        contract_types = [(0, _('all').capitalize())]
        for i, type in JobOffer.JOB_TYPES:
            contract_types.append((i+1, type))
        self.fields['contract_type'].choices = contract_types

    def clean_contract_type(self):
        """clean contract type"""
        return int(self.cleaned_data['contract_type'])

    def search(self):
        """search job form"""
        querry = models.Q(obsolete=False)
        if self.cleaned_data['title']:
            querry &= models.Q(title__icontains=self.cleaned_data['title'])
        if self.cleaned_data['activity_field']:
            querry &= models.Q(activity_field=\
                self.cleaned_data['activity_field'])
        if self.cleaned_data['experience']:
            querry &= models.Q(experience__icontains=\
                self.cleaned_data['experience'])
        if self.cleaned_data['contract_type']:
            querry &= models.Q(contract_type=self.cleaned_data['contract_type'])

        return JobOffer.objects.filter(querry).order_by('-id')


