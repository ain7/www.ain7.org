# -*- coding: utf-8 -*-
#
# groupes_professionnels/forms.py
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

import datetime

from django import forms
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from ain7.fields import AutoCompleteField
from ain7.widgets import DateTimeWidget
from ain7.annuaire.models import Person
from ain7.groupes_professionnels.models import *

dateWidget = DateTimeWidget()
dateWidget.dformat = '%d/%m/%Y'

class SubscribeGroupProForm(forms.Form):
    member = forms.IntegerField(label=_('Person to subscribe'), widget=AutoCompleteField(url='/ajax/person/'))

    def save(self, group=None):
        membership = Membership()
        membership.member = \
            Person.objects.get(user__id=self.cleaned_data['member'])
        membership.group = group
        membership.save()
        return membership

    def clean_member(self):
        m = self.cleaned_data['member']
        if m==None:
            raise ValidationError(_('This field is mandatory.'))
        else:
            try:
                member = Person.objects.get(id=self.cleaned_data['member'])
            except Person.DoesNotExist:
                raise ValidationError(_('This person does not exist in the base.'))
            return m
    
class UnsubscribeGroupProForm(forms.Form):
    member = forms.IntegerField(label=_('Person to unsubscribe'),
                                widget=AutoCompleteField(url='/ajax/person/'))

    def unsubscribe(self, group=None):
        person = Person.objects.get(user__id=self.cleaned_data['member'])
        membership = Membership.objects\
            .filter(group=group, member=person)\
            .exclude(end_date__isnull=False,
                     end_date__lte=datetime.datetime.now())\
            .latest('end_date')
        membership.end_date = datetime.datetime.now()
        membership.save()

class GroupProForm(forms.ModelForm):
    web_page = forms.CharField(label=_('web page').capitalize(),
        widget = forms.widgets.Textarea(attrs={'rows':10, 'cols':90}),
        required=False)
    
    class Meta:
        model = GroupPro

    def save(self, user=None):
        groupPro =  super(GroupProForm, self).save()
        groupPro.logged_save(user.person)
        return groupPro

class NewRoleForm(forms.Form):
    username = forms.CharField(label=_('Username'), max_length=100,
        required=True, widget=AutoCompleteField(url='/ajax/person/'))
    start_date = forms.DateTimeField(label=_('start date').capitalize(),
        widget=dateWidget, required=True)
    end_date = forms.DateTimeField(label=_('end date').capitalize(),
        widget=dateWidget, required=False)

    def clean_end_date(self):
        if self.cleaned_data.get('start_date') and \
            self.cleaned_data.get('end_date') and \
            self.cleaned_data['start_date']>self.cleaned_data['end_date']:
            raise forms.ValidationError(_('Start date is later than end date'))
        return self.cleaned_data['end_date']

    def save(self, group, type):
        gr = GroupProRole()
        gr.type = type
        gr.start_date = self.cleaned_data['start_date']
        gr.end_date = self.cleaned_data['end_date']
        gr.group = group
        gr.member = get_object_or_404(Person,
                                      pk=self.cleaned_data['username'])
        gr.save()
        return gr

class ChangeDatesForm(forms.Form):
    start_date = forms.DateTimeField(label=_('start date').capitalize(),
        widget=dateWidget, required=True)
    end_date = forms.DateTimeField(label=_('end date').capitalize(),
        widget=dateWidget, required=False)

    def clean_end_date(self):
        if self.cleaned_data.get('start_date') and \
            self.cleaned_data.get('end_date') and \
            self.cleaned_data['start_date']>self.cleaned_data['end_date']:
            raise forms.ValidationError(_('Start date is later than end date'))
        return self.cleaned_data['end_date']

    def save(self, role):
        role.start_date = self.cleaned_data['start_date']
        role.end_date = self.cleaned_data['end_date']
        return role.save()
