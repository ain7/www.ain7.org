# -*- coding: utf-8
""""
 ain7/voyages/forms.py
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

from datetime import datetime

from django import forms
from django.utils.translation import ugettext as _

from ain7.voyages.models import Travel


class SearchTravelForm(forms.Form):
    """ search travel form"""
    label = forms.CharField(label=_('label').capitalize(),
        max_length=50, required=False)
    visited_places = forms.CharField(label=_('visited places').capitalize(),
        max_length=50, required=False)
    search_old_travel = forms.BooleanField(
        label=_('search in old travels').capitalize(), required=False)

    def __init__(self, *args, **kwargs):
        """search form init method"""
        super(SearchTravelForm, self).__init__(*args, **kwargs)

    def search(self):
        """search method"""
        criteria = {
            'label__icontains': self.cleaned_data['label'],
            'label__icontains': self.cleaned_data['visited_places']}

        if not self.cleaned_data['search_old_travel']:
            criteria['start_date__gte'] = datetime.now()
        return Travel.objects.filter(**criteria)

