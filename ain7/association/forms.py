# -*- coding: utf-8 -*-
"""
 ain7/associations/forms.py
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

from django import forms
from django.forms.util import ValidationError
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person
from ain7.association.models import CouncilRole
from ain7.fields import AutoCompleteField
from ain7.widgets import DateTimeWidget


DATE_WIDGET = DateTimeWidget()
DATE_WIDGET.dformat = '%d/%m/%Y'

class NewCouncilRoleForm(forms.Form):
    """Council Role Form"""
    username = forms.CharField(label=_('Username'), max_length=100,
        required=True, widget=AutoCompleteField(completed_obj_name='person'))
    start_date = forms.DateTimeField(label=_('start date').capitalize(),
        widget=DATE_WIDGET, required=True)
    end_date = forms.DateTimeField(label=_('end date').capitalize(),
        widget=DATE_WIDGET, required=False)
    board_member = forms.BooleanField(label=_('board member').capitalize(),
        required=False)

    def clean_end_date(self):
        """check end date"""
        if self.cleaned_data.get('start_date') and \
            self.cleaned_data.get('end_date') and \
            self.cleaned_data['start_date']>self.cleaned_data['end_date']:
            raise forms.ValidationError(_('Start date is later than end date'))
        return self.cleaned_data['end_date']

    def clean_username(self):
        """check username"""
        pid = self.cleaned_data['username']
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
    
    def save(self, role_type):
        """save council role"""
        c_role = CouncilRole()
        c_role.role = role_type
        c_role.start_date = self.cleaned_data['start_date']
        c_role.end_date = self.cleaned_data['end_date']
        c_role.member = self.cleaned_data['username']
        c_role.board_member = self.cleaned_data['board_member']
        c_role.save()
        return c_role

class ChangeDatesForm(forms.Form):
    """change dates form"""
    start_date = forms.DateTimeField(label=_('start date').capitalize(),
        widget=DATE_WIDGET, required=True)
    end_date = forms.DateTimeField(label=_('end date').capitalize(),
        widget=DATE_WIDGET, required=False)

    def clean_end_date(self):
        """check end date"""
        if self.cleaned_data.get('start_date') and \
            self.cleaned_data.get('end_date') and \
            self.cleaned_data['start_date']>self.cleaned_data['end_date']:
            raise forms.ValidationError(_('Start date is later than end date'))
        return self.cleaned_data['end_date']

    def save(self, role):
        """save new dates"""
        role.start_date = self.cleaned_data['start_date']
        role.end_date = self.cleaned_data['end_date']
        return role.save()

