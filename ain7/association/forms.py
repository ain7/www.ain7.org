# -*- coding: utf-8 -*-
"""
 ain7/associations/forms.py
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

from django import forms
from django.forms.util import ValidationError
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person
from ain7.fields import AutoCompleteField
from ain7.groups.models import GroupLeader
from ain7.widgets import DateTimeWidget


DATE_WIDGET = DateTimeWidget()
DATE_WIDGET.dformat = '%d/%m/%Y'

class CouncilRoleForm(forms.ModelForm):
    """Council Role Form"""
    person = forms.IntegerField(label=_('Person'),
        required=True, widget=AutoCompleteField(completed_obj_name='person'))
    start_date = forms.DateTimeField(label=_('start date').capitalize(),
        widget=DATE_WIDGET, required=True)
    end_date = forms.DateTimeField(label=_('end date').capitalize(),
        widget=DATE_WIDGET, required=False)
    board_member = forms.BooleanField(label=_('board member').capitalize(),
        required=False)

    class Meta:
        """form meta data"""
        model = GroupLeader
        exclude = ('grouphead',)

    def clean_end_date(self):
        """check end date"""
        if self.cleaned_data.get('start_date') and \
            self.cleaned_data.get('end_date') and \
            self.cleaned_data['start_date']>self.cleaned_data['end_date']:
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

