# -*- coding: utf-8
"""
 ain7/organizations/forms.py
"""
#
#   Copyright © 2007-2011 AIn7 Devel Team
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
from django.forms.util import ValidationError
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Country
from ain7.organizations.models import Office, OrganizationActivityField, \
     Organization
from ain7.fields import AutoCompleteField


class SearchOrganizationForm(forms.Form):
    """organization search form"""
    name = forms.CharField(label=_('Name'), max_length=50, required=False)
#     location = forms.CharField(
#         label=_('Location'), max_length=50, required=False)
    activity_field = forms.CharField(label=_('Activity field'), max_length=50,
        required=False,
        widget=AutoCompleteField(completed_obj_name='activity_field'))
    activity_code = forms.CharField(label=_('Activity code'), max_length=50,
        required=False,
        widget=AutoCompleteField(completed_obj_name='activitycode'))

    def criteria(self):
        """defines criterias for an organization"""
        criteria = {'name__icontains': self.cleaned_data['name'],
            'is_a_proposal': False}
#                     'location__contains': self.cleaned_data['location'],
        if self.cleaned_data['activity_field'] != "":
            criteria['activity_field__exact'] = \
                OrganizationActivityField.objects.get(
                id=self.cleaned_data['activity_field'])
        if self.cleaned_data['activity_code'] != "":
            criteria['activity_field__exact'] = \
                OrganizationActivityField.objects.get(
                id=self.cleaned_data['activity_code'])
        return criteria

    def search(self, criteria):
        """search method for an organization"""
        return Organization.objects.filter(**criteria).order_by('name')

class OrganizationForm(forms.ModelForm):
    """organization form"""

    name = forms.CharField(
        label=_('Name'), max_length=50, required=True)
    employment_agency = forms.BooleanField(
        label=_('employment agency').capitalize(), required=False)
    size = forms.IntegerField(
        label=_('Size'), required=True,
        widget=forms.Select(choices=Organization.ORGANIZATION_SIZE))
    #activity_field = forms.IntegerField(label=_('Activity field'),
    #    required=False,
    #    widget=AutoCompleteField(completed_obj_name='activity_field'))
    short_description = forms.CharField(
        label=_('Short Description'), max_length=50, required=False)
    long_description = forms.CharField(
        label=_('Long Description'), max_length=5000, required=False,
        widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':50}))

    class Meta:
        """meta organization form"""
        model = Organization
        exclude = ('is_a_proposal', 'is_valid', 'modification_of',
            'modification_date',)


class OfficeForm(forms.ModelForm):
    """office form"""

    country = forms.ModelChoiceField(
        label=_('country').capitalize(),
        queryset=Country.objects.all().order_by('name'), required=False)

    def clean_organization(self):
        """check organization in office"""
        org = self.cleaned_data['organization']
        if org == None:
            raise ValidationError(_('The organization is mandatory.'))
        try:
            org = Organization.objects.get(id=org)
        except Organization.DoesNotExist:
            raise ValidationError(_('The organization does not exist.'))
        else:
            return org
        
    class Meta:
        """meta office form"""
        model = Office
        exclude = ('old_id', 'organization', 'is_a_proposal', 'is_valid',
            'modification_of', 'modification_date')

class OrganizationListForm(forms.Form):
    """organization list form"""
    organization = forms.CharField(label=_('organization').capitalize(),
        max_length=50, required=False,
        widget=AutoCompleteField(completed_obj_name='organization'))

    def search(self):
        """search organization method"""
        result = None
        if self.cleaned_data['organization'] != "":
            result = Organization.objects.filter(\
                id=self.cleaned_data['organization']).distinct()
            if result:
                result = result[0]
        return result

class OfficeListForm(forms.Form):
    """office list form"""
    bureau = forms.CharField(label=_('office').capitalize(), required=True,
         widget=AutoCompleteField(completed_obj_name='office'))

    def search(self):
        """search office method"""
        result = None
        if self.cleaned_data['bureau'] != "":
            result = Office.objects.filter(\
                id=self.cleaned_data['bureau']).distinct()
            if result:
                result = result[0]
        return result

