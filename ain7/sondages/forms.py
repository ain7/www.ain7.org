# -*- coding: utf-8
"""
 ain7/sondages/forms.py
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
from django.utils.translation import ugettext as _

from ain7.sondages.models import Survey, Choice
from ain7.widgets import DateTimeWidget


dateWidget = DateTimeWidget()
dateWidget.dformat = '%d/%m/%Y'

class SurveyForm(forms.ModelForm):
    """survey form"""
    start_date = forms.DateTimeField(label=_('start date'), required=True,
        widget=dateWidget)
    end_date = forms.DateTimeField(label=_('end date'), required=True,
        widget=dateWidget)

    class Meta:
        """survey form meta"""
        model = Survey

    def clean_end_date(self):
        """check date in survey form"""
        if self.cleaned_data.get('start_date') and \
            self.cleaned_data.get('end_date') and \
            self.cleaned_data['start_date'] > self.cleaned_data['end_date']:
            raise forms.ValidationError(_('Start date is later than end date'))
        return self.cleaned_data['end_date']

class ChoiceForm(forms.ModelForm):
    """choice form"""

    class Meta:
        """meta choice form"""
        model = Choice
        exclude = ('survey')

