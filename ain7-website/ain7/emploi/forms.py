# -*- coding: utf-8
#
# emploi/forms.py
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
from django.newforms import widgets

from ain7.annuaire.models import Track
from ain7.emploi.models import *
from ain7.fields import AutoCompleteField

class JobOfferForm(forms.Form):
    reference = forms.CharField(label=_('reference'),max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))
    title = forms.CharField(label=_('title'),max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))
    experience = forms.CharField(label=_('experience'),max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))
    contract_type = forms.IntegerField(label=_('contract type'),required=False)
    contract_type.widget = forms.Select(choices=JobOffer.JOB_TYPES)
    is_opened = forms.BooleanField(label=_('is opened'),required=False)
    description = forms.CharField(label=_('description'),max_length=500, required=False, widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':95}))

class SearchJobForm(forms.Form):
    title = forms.CharField(label=_('title'),max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))
    allTracks = forms.BooleanField(label=_('all tracks'), required=False)
    track = forms.ModelMultipleChoiceField(
        label=_('track'), queryset=Track.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super(SearchJobForm, self).__init__(*args, **kwargs)

    def clean_track(self):
        return self.clean_data['track']

    def search(self):
        maxTrackId = Track.objects.latest('id').id + 1
        # si des filières sont sélectionnées mais pas le joker
        # on filtre par rapport à ces filières
        jobsMatchingTracks = []
        if (not self.clean_data['allTracks'])\
               and len(self.clean_data['track'])>0:
            for track in self.clean_data['track']:
                jobsMatchingTracks.extend(track.jobs.all())
        else:
            jobsMatchingTracks = JobOffer.objects.all()
        # maintenant on filtre ces jobs par rapport au titre saisi
        matchingJobs = []
        if self.clean_data['title']:
            for job in jobsMatchingTracks:
                if str(self.clean_data['title']) in job.title:
                    matchingJobs.append(job)
        else:
            matchingJobs = jobsMatchingTracks
        return matchingJobs

class OrganizationForm(forms.Form):
    name = forms.CharField(
        label=_('Name'), max_length=50, required=True)
    size = forms.IntegerField(
        label=_('Size'), required=True,
        widget=forms.Select(choices=Company.COMPANY_SIZE))
    field = forms.CharField(
        label=_('Field'), max_length=50, required=True,
        widget=AutoCompleteField(url='/ajax/companyfield/'))
    short_description = forms.CharField(
        label=_('Short Description'), max_length=50)
    long_description = forms.CharField(
        label=_('Long Description'), max_length=5000, required=False,
        widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':95}))

    def save(self, is_a_proposal=False, organization=None):
        if organization:
            org = organization
        else:
            org = Company()
        # TODO : automatiser avec qqchose comme ça:
#         for field in org._meta.fields:
#             if field.name=='is_a_proposal':
#                 field.value = is_a_proposal
#             else:
#                 field.value = self.clean_data[field.name]
        org.name = self.clean_data['name']
        org.size = self.clean_data['size']
        org.field = CompanyField.objects.get(id=self.clean_data['field'])
        org.short_description = self.clean_data['short_description']
        org.long_description = self.clean_data['long_description']
        org.is_a_proposal = is_a_proposal
        org.save()
        return org


class OfficeForm(forms.Form):
    company = forms.ModelChoiceField(
        label=_('organization'),
        queryset=Company.objects.filter(is_a_proposal=False),required=True)
    name = forms.CharField(
        label=_('name'), max_length=50, required=True)
    line1 = forms.CharField(
        label=_('line1'), max_length=50, required=False)
    line2 = forms.CharField(
        label=_('line2'), max_length=100, required=False)
    zip_code = forms.CharField(
        label=_('zip code'), max_length=20, required=False)
    city = forms.CharField(
        label=_('city'), max_length=50, required=False)
    country = forms.ModelChoiceField(
        label=_('country'), queryset=Country.objects.all(), required=False)
    phone_number = forms.CharField(
        label=_('phone number'), max_length=20, required=False)
    web_site = forms.CharField(
        label=_('web site'), max_length=100, required=False)

    def save(self, is_a_proposal=False, office=None):
        if not office:
            office = Office()
        office.company = self.clean_data['company']
        office.name = self.clean_data['name']
        office.line1 = self.clean_data['line1']
        office.line2 = self.clean_data['line2']
        office.zip_code = self.clean_data['zip_code']
        office.city = self.clean_data['city']
        office.country = self.clean_data['country']
        office.phone_number = self.clean_data['phone_number']
        office.web_site = self.clean_data['web_site']
        office.is_a_proposal = is_a_proposal
        office.save()
        return office
