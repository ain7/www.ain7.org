# -*- coding: utf-8
#
# search_engine/forms.py
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
from django.utils.translation import ugettext as _

from ain7.search_engine.models import SearchFilter
from ain7.widgets import DateTimeWidget


dateWidget = DateTimeWidget()
dateWidget.dformat = '%d/%m/%Y'
dateTimeWidget = DateTimeWidget()
dateTimeWidget.dformat = '%d/%m/%Y %H:%M'

class ChooseFieldForm(forms.Form):
    chosenField = forms.ChoiceField(label=_('Field'), required=True,
        choices = [])

class SearchFilterForm(forms.ModelForm):
    class Meta:
        model = SearchFilter
        fields = ('name',)

class ChooseCSVFieldsForm(forms.Form):
    chosenFields = forms.MultipleChoiceField(label='', choices = [])

