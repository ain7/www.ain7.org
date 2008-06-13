# -*- coding: utf-8 -*-
#
# groupes_regionaux/forms.py
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
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from ain7.groupes_regionaux.models import Group, GroupRole
from ain7.annuaire.models import Person
from ain7.widgets import DateTimeWidget
from ain7.fields import AutoCompleteField

dateWidget = DateTimeWidget()
dateWidget.dformat = '%d/%m/%Y'

class GroupForm(forms.ModelForm):
    description = forms.CharField(label=_('description').capitalize(),
        widget = forms.widgets.Textarea(attrs={'rows':10, 'cols':90}))
    
    class Meta:
        model = Group
        exclude = ('group')

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
        gr = GroupRole()
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
