# -*- coding: utf-8
"""
 ain7/emploi/forms.py
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

from django.db import models
from django import forms
from django.forms.util import ValidationError
from django.utils.translation import ugettext as _

from ain7.emploi.models import JobOffer, \
                               Position, EducationItem, LeisureItem,\
                               PublicationItem
from ain7.organizations.models import Office, Organization, \
                               OrganizationActivityField
from ain7.fields import AutoCompleteField
from ain7.utils import AIn7Form
from ain7.widgets import DateTimeWidget


DATE_WIDGET = DateTimeWidget()
DATE_WIDGET.dformat = '%d/%m/%Y'

class JobOfferForm(AIn7Form):
    """ Job Offer Form"""
    reference = forms.CharField(label=_('reference').capitalize(), 
        max_length=50, required=False, 
        widget=forms.TextInput(attrs={'size':'60'}))
    title = forms.CharField(label=_('title').capitalize(), max_length=200,
        required=True, widget=forms.TextInput(attrs={'size':'60'}))
    office = forms.IntegerField(label=_('Office'), required=True,
        widget=AutoCompleteField(completed_obj_name='office'))
    experience = forms.CharField(label=_('experience').capitalize(),
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'size':'60'}))
    contract_type = forms.IntegerField(label=_('contract type'),
        required=False)
    contract_type.widget = forms.Select(choices=JobOffer.JOB_TYPES)
    description = forms.CharField(label=_('description').capitalize(),
        required=False,
        widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':80}))
    contact_name = forms.CharField(label=_('Contact name'), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'60'}))
    contact_email = forms.EmailField(label=_('Contact email').capitalize(),
        required=False, widget=forms.TextInput(attrs={'size':'60'}))
    activity_field = forms.IntegerField(label=_('Activity field'),
        required=False,
        widget=AutoCompleteField(completed_obj_name='activity_field'))
    obsolete = forms.BooleanField(label=_('obsolete'), required=False)
    
    def clean_office(self):
        """clean office for job offer"""
        org = self.cleaned_data['office']
        if org == None:
            raise ValidationError(_('The office is mandatory.'))
        else:
            office = None
            try:
                office = Office.objects.get(id=org)
            except Office.DoesNotExist:
                raise ValidationError(_('The entered office does not exist.'))
            return office
    
    def clean_activity_field(self):
        """clean activity field"""
        activity = self.cleaned_data['activity_field']
        if activity is None:
            return None
        activity_field = None
        try:
            activity_field = OrganizationActivityField.objects.get(pk=activity)
        except OrganizationActivityField.DoesNotExist:
            raise ValidationError(
                _('The entered activity field does not exist.'))
        return activity_field
    
    def save(self, user, job_offer=None):
        """save job offer"""
        if not job_offer:
            job_offer = JobOffer()
            job_offer.created_by = user.person

            user_groups = user.groups.all().values_list('name', flat=True)
            if 'ain7-secretariat' in user_groups or \
               'ain7-admin' in user_groups:
                job_offer.checked_by_secretariat = True

        job_offer.reference = self.cleaned_data['reference']
        job_offer.title = self.cleaned_data['title']
        job_offer.experience = self.cleaned_data['experience']
        job_offer.contract_type = self.cleaned_data['contract_type']
        job_offer.description = self.cleaned_data['description']
        job_offer.office = self.cleaned_data['office']
        job_offer.contact_name = self.cleaned_data['contact_name']
        job_offer.contact_email = self.cleaned_data['contact_email']
        job_offer.activity_field = self.cleaned_data['activity_field']
        job_offer.obsolete = self.cleaned_data['obsolete']
        job_offer.save()
        # needs to have a primary key before a many-to-many can be used
        job_offer.logged_save(user.person)
        return job_offer


class SearchJobForm(forms.Form):
    """search job form"""
    title = forms.CharField(label=_('title').capitalize(), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'40'}))
    activity_field = forms.IntegerField(label=_('Activity field'),
        required=False,
         widget=AutoCompleteField(completed_obj_name='activity_field'))
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

class PositionForm(forms.ModelForm):
    """Position Form"""

    office = forms.IntegerField(label=_('Office'), required=False, 
        widget=AutoCompleteField(completed_obj_name='office'))

    def clean_office(self):
        """clean office in position form"""
        off = self.cleaned_data['office']

        if off == None:
            raise ValidationError(_('The office is mandatory.'))
        else:
            try:
                office = Office.objects.get(id=self.cleaned_data['office'])
            except Office.DoesNotExist:
                raise ValidationError(_('The entered office does not exist.'))
            return office
    
    class Meta:
        """position form meta"""
        model = Position
        exclude = ('ain7member', 'email')

    def clean_end_date(self):
        """clean end date for position form"""
        if self.cleaned_data.get('start_date') and \
            self.cleaned_data.get('end_date') and \
            self.cleaned_data['start_date']>self.cleaned_data['end_date']:
            raise forms.ValidationError(_('Start date is later than end date'))
        return self.cleaned_data['end_date']

class EducationItemForm(forms.ModelForm):
    """Education Item form"""

    diploma = forms.CharField(label=_('diploma').capitalize(),
        widget=AutoCompleteField(completed_obj_name='diploma'), required=False)

    class Meta:
        """education item meta"""
        model = EducationItem
        exclude = ('ain7member',)

    def clean_end_date(self):
        """clean end date education item"""
        if self.cleaned_data.get('start_date') and \
            self.cleaned_data.get('end_date') and \
            self.cleaned_data['start_date']>self.cleaned_data['end_date']:
            raise forms.ValidationError(_('Start date is later than end date'))
        return self.cleaned_data['end_date']

class LeisureItemForm(forms.ModelForm):
    """leisure item form"""

    class Meta:
        """leisure item form meta"""
        model = LeisureItem
        exclude = ('ain7member',)

class PublicationItemForm(forms.ModelForm):
    """publication item form"""
    date = forms.DateField(label=_('year').capitalize(),
        input_formats=['%Y'], widget=forms.DateTimeInput(format='%Y'))

    class Meta:
        """publication item meta"""
        model = PublicationItem
        exclude = ('ain7member',)

class ChooseOrganizationForm(forms.Form):
    """choose organization form"""

    organization = forms.IntegerField(label=_('Organization'), required=False,
        widget=AutoCompleteField(completed_obj_name='organization'))

    def clean_organization(self):
        """clean organization"""
        org = self.cleaned_data['organization']

        if org == None:
            raise ValidationError(_('The organization is mandatory.'))

        try:
            Organization.objects.get(id=org)
        except Organization.DoesNotExist:
            raise ValidationError(\
                _('The organization "%s" does not exist.') % org)
        else:
            return self.cleaned_data['organization']

