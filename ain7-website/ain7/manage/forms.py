# -*- coding: utf-8
#
# manage/forms.py
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
from django.contrib.auth.models import User, Group

from ain7.annuaire.models import Person, Country, Email
from ain7.emploi.models import ActivityField, Organization
from ain7.fields import AutoCompleteField
from ain7.widgets import DateTimeWidget
from ain7.manage.models import Notification

dateWidget = DateTimeWidget()
dateWidget.dformat = '%d/%m/%Y'

class SearchUserForm(forms.Form):
    last_name = forms.CharField(label=_('Last name'), max_length=50, required=False)
    first_name = forms.CharField(label=_('First name'), max_length=50, required=False)
    organization = forms.CharField(label=_('organization').capitalize(), max_length=50, required=False,widget=AutoCompleteField(url='/ajax/organization/'))

    def search(self):
        criteria={
            'last_name__contains':self.cleaned_data['last_name'],\
            'first_name__contains':self.cleaned_data['first_name']}
        return Person.objects.filter(**criteria)

class SearchRoleForm(forms.Form):
    name = forms.CharField(label=_('Name'), max_length=50, required=False)

    def search(self):
        criteria={'name__contains':self.cleaned_data['name']}
        return Group.objects.filter(**criteria).order_by('name')


class SearchOrganizationForm(forms.Form):
    name = forms.CharField(label=_('Name'), max_length=50, required=False)
#     location = forms.CharField(
#         label=_('Location'), max_length=50, required=False)
    activity_field = forms.CharField(label=_('Activity field'), max_length=50, required=False,widget=AutoCompleteField(url='/ajax/activityfield/'))
    activity_code = forms.CharField(label=_('Activity code'), max_length=50, required=False,widget=AutoCompleteField(url='/ajax/activitycode/'))

    def search(self):
        criteria = {'name__contains': self.cleaned_data['name'],
                    'is_a_proposal': False}
#                     'location__contains': self.cleaned_data['location'],
        if self.cleaned_data['activity_field']!="-1":
            criteria['activity_field__exact'] = ActivityField.objects.get(
                id=self.cleaned_data['activity_field'])
        if self.cleaned_data['activity_code']!="-1":
            criteria['activity_field__exact'] = ActivityField.objects.get(
                id=self.cleaned_data['activity_code'])
        return Organization.objects.filter(**criteria).order_by('name')
        

class SearchContributionForm(forms.Form):
    user = forms.CharField(label=_('User'), max_length=50, required=False)
    type = forms.CharField(label=_('Type'), max_length=50, required=False)

class PermRoleForm(forms.Form):
    perm = forms.CharField(label=_('Permission'), max_length=50, required=True, widget=AutoCompleteField(url='/ajax/permission/'))

class MemberRoleForm(forms.Form):
    username = forms.CharField(label=_('Username'), max_length=100, required=True, widget=AutoCompleteField(url='/ajax/person/'))

class NewPersonForm(forms.ModelForm):
    first_name = forms.CharField(label=_('First name'),max_length=50, required=True, widget=forms.TextInput(attrs={'size':50}))
    last_name = forms.CharField(label=_('Last name'),max_length=50, required=True, widget=forms.TextInput(attrs={'size': 50}))
    mail = forms.EmailField(label=_('Mail'),max_length=50, required=True, widget=forms.TextInput(attrs={'size': 50}))
    country = forms.IntegerField(label=_('Nationality'), required=False, widget=AutoCompleteField(url='/ajax/nationality/'))
    birth_date = forms.DateTimeField(label=_('Date of birth'), required=False, widget=dateWidget)
    sex = forms.CharField(label=_('Sex'), required=False,  widget=forms.Select(choices=Person.SEX))

    class Meta:
        model = Person
        exclude = ('user', 'complete_name', 'maiden_name', 'death_date',
                   'wiki_name', 'notes')

    def clean_nationality(self):
        n = self.cleaned_data['nationality']

        if n != -1:
            try:
                Country.objects.get(id=n)
            except Country.DoesNotExist:
                raise ValidationError(_('The nationality "%s" does not exist.') % n)
            else:
                return self.cleaned_data['nationality']
        else:
             return self.cleaned_data['nationality']

    def genlogin(self):
        login = (self.cleaned_data['first_name'][0]+self.cleaned_data['last_name']).lower()

        tries = 0
        while (User.objects.filter(username=login).count() > 0):
            tries = tries + 1
            if tries < len(self.cleaned_data['first_name']):
                login = (self.cleaned_data['first_name'][0:tries]+self.cleaned_data['last_name']).lower()
            else:
                login = (self.cleaned_data['first_name'][0]+self.cleaned_data['last_name']+str(tries)).lower()

        return login

    def save(self):
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

        if self.cleaned_data.has_key('country') and self.cleaned_data['country'] != -1:
            new_person.country = Country.objects.get(id=self.cleaned_data['country'])
            new_person.save()

        new_couriel = Email(person = new_person,
            email = self.cleaned_data['mail'], preferred_email = True)
        new_couriel.save()

        return new_person

class NewRoleForm(forms.ModelForm):
    name = forms.CharField(label=_('Name'),max_length=50, required=True, widget=forms.TextInput(attrs={'size':50}))

    class Meta:
        model = Group
        exclude = ('permissions')

    def save(self):
        new_role = Group(name = self.cleaned_data['name'])
        new_role.save()
        
        return new_role

class NotificationForm(forms.ModelForm):
    details = forms.CharField(label=_('details'), required=True,
        widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':90}))

    class Meta:
        model = Notification
        exclude = ('organization_proposal', 'office_proposal')

