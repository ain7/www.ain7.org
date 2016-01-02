# -*- coding: utf-8
"""
 ain7/manage/forms.py
"""
#
#   Copyright © 2007-2016 AIn7 Devel Team
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
from django.forms.utils import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person, Country, Email
from ain7.organizations.models import Organization


class SearchUserForm(forms.Form):
    """user search form"""
    last_name = forms.CharField(label=_('Last name'), max_length=50,
        required=False)
    first_name = forms.CharField(label=_('First name'), max_length=50,
        required=False)
    organization = forms.CharField(label=_('organization').capitalize(), 
        max_length=50, required=False)

    def search(self):
        """search method for a user"""
        querry = models.Q(\
            last_name__icontains=self.cleaned_data['last_name']) | \
            models.Q(maiden_name__icontains=self.cleaned_data['last_name'])
        querry &= models.Q(\
            first_name__icontains=self.cleaned_data['first_name'])
        if self.cleaned_data['organization'] != "":
            querry &= models.Q(\
                ain7member__positions__office__organization__exact=\
                Organization.objects.get(id=self.cleaned_data['organization']))
        return Person.objects.filter(querry).distinct()

class NewPersonForm(forms.ModelForm):
    """new person form"""
    first_name = forms.CharField(label=_('First name'), max_length=50,
        required=True, widget=forms.TextInput(attrs={'size':40}))
    last_name = forms.CharField(label=_('Last name'), max_length=50, 
        required=True, widget=forms.TextInput(attrs={'size': 40}))
    mail = forms.EmailField(label=_('Mail'), max_length=50, required=True,
        widget=forms.TextInput(attrs={'size': 40}))
    country = forms.IntegerField(label=_('Nationality'), required=False) 
    birth_date = forms.DateTimeField(label=_('Date of birth'), required=False)
    sex = forms.CharField(label=_('Sex'), required=False,  
        widget=forms.Select(choices=Person.SEX))

    class Meta:
        """NewPersonForm meta informations"""
        model = Person
        exclude = ('user', 'complete_name', 'maiden_name', 'death_date',
                   'wiki_name', 'notes')

    def genlogin(self):
        """login generation method"""
        login = (self.cleaned_data['first_name'][0] + \
            self.cleaned_data['last_name']).lower()

        tries = 0
        while (User.objects.filter(username=login).count() > 0):
            tries = tries + 1
            if tries < len(self.cleaned_data['first_name']):
                login = (self.cleaned_data['first_name'][0:tries] + \
                    self.cleaned_data['last_name']).lower()
            else:
                login = (self.cleaned_data['first_name'][0] + \
                    self.cleaned_data['last_name']+str(tries)).lower()

        return login

    def save(self):
        """save new user method"""
        login = self.genlogin()
        mail = self.cleaned_data['mail']
        new_user = User.objects.create_user(login, mail, 'password')
        new_user.first_name = self.cleaned_data['first_name']
        new_user.last_name = self.cleaned_data['last_name']
        new_user.save()

        new_person = Person(user = new_user,
            first_name = self.cleaned_data['first_name'],
            last_name = self.cleaned_data['last_name'],
            complete_name = \
                self.cleaned_data['first_name'] + ' ' +
                self.cleaned_data['last_name'],
            sex = self.cleaned_data['sex'])
        new_person.save()
       
        if self.cleaned_data.has_key('birth_date'): 
            new_person.birth_date = self.cleaned_data['birth_date']
            new_person.save()

        if self.cleaned_data.has_key('country'):
            new_person.country = Country.objects.get( \
                id=self.cleaned_data['country'])
            new_person.save()

        new_couriel = Email(person = new_person,
            email = self.cleaned_data['mail'], preferred_email = True)
        new_couriel.save()

        return new_person


class ErrorRangeForm(forms.Form):
    """error range form"""

    range_from = forms.IntegerField(label=_('from')+' #', required=True)
    range_to   = forms.IntegerField(label=_('to')  +' #', required=True)
    comment = forms.CharField(label=_('Comment (added)'), required=False,
        widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':80}))
    fixed = forms.BooleanField(label=_('fixed').capitalize(), required=False)

    def clean(self):
        range_from = self.cleaned_data['range_from']
        range_to   = self.cleaned_data['range_to']
        if range_to < range_from:
            raise ValidationError(_('End of range precedes its beginning.'))
        for index in range(range_from, range_to+1):
            if not PortalError.objects.filter(pk=index):
                raise ValidationError(_('Error #%s does not exist.') % index)
        return self.cleaned_data

    def save(self):
        """save this form"""
        range_from = self.cleaned_data['range_from']
        range_to   = self.cleaned_data['range_to']
        for index in range(range_from, range_to+1):
            error = PortalError.objects.get(pk=index)
            error.fixed    = self.cleaned_data['fixed']
            if not error.comment:
                error.comment = ''
            error.comment += self.cleaned_data['comment']
            error.save()
        return

