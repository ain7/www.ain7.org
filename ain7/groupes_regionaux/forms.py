# -*- coding: utf-8 -*-
"""
 ain7/groupes_regionaux/forms.py
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

import re

from django import forms
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person
from ain7.fields import AutoCompleteField
from ain7.groups.models import Group, GroupLeader
from ain7.widgets import DateTimeWidget


DATE_WIDGET = DateTimeWidget()
DATE_WIDGET.dformat = '%d/%m/%Y'

class GroupForm(forms.ModelForm):
    """New Group Form"""
    slug = forms.CharField(label=_('short name').capitalize(),
        widget = forms.TextInput(attrs={'size': 40}), 
        required=False)
    about = forms.CharField(label=_('about').capitalize(),
        widget = forms.widgets.Textarea(attrs={'rows':10, 'cols':90}),
        required=False)

    def clean_shortname(self):
        if not re.match(r'^[a-z0-9\-_]+$', self.cleaned_data['slug']):
            raise forms.ValidationError(\
                 _('Please only use alphanumeric characters'))
        if Group.objects.filter(\
            shortname=self.cleaned_data['slug']).count() > 1:
            raise forms.ValidationError(\
                 _('A group with this name already exists'))
        return self.cleaned_data['slug']
   
    class Meta:
        """Meta Group Form Information"""
        model = Group
        exclude = ('group', 'type', 'access', 'private', 'web_site', 'email',)

class RoleForm(forms.ModelForm):
    """New role form"""
    person = forms.IntegerField(label=_('Person'),
        required=True, widget=AutoCompleteField(completed_obj_name='person'))
    start_date = forms.DateTimeField(label=_('start date').capitalize(),
        widget=DATE_WIDGET, required=True)
    end_date = forms.DateTimeField(label=_('end date').capitalize(),
        widget=DATE_WIDGET, required=False)

    class Meta:
        model = GroupLeader
        exclude = ['grouphead']

    def clean_end_date(self):
        """check end date for new role"""
        if self.cleaned_data.get('start_date') and \
            self.cleaned_data.get('end_date') and \
            self.cleaned_data['start_date'] > self.cleaned_data['end_date']:
            raise forms.ValidationError(_('Start date is later than end date'))
        return self.cleaned_data['end_date']

    def clean_person(self):
        """check username"""
        pid = self.cleaned_data['person']
        if pid == None:
            raise ValidationError(_('This field is mandatory.'))
            return None
        else:
            person = None
            try:
                person = Person.objects.get(id=pid)
            except Person.DoesNotExist:
                raise ValidationError(_('The entered person is not in\
 the database.'))
            return person

