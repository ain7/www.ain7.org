# -*- coding: utf-8
"""
 ain7/organizations/forms.py
"""
#
#   Copyright © 2007-2017 AIn7 Devel Team
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

from ain7.organizations.models import Office, Organization


class OrganizationListForm(forms.Form):
    """organization list form"""
    organization = forms.CharField(label=_('organization').capitalize(),
        max_length=50, required=False)

    def search(self):
        """search organization method"""
        result = None
        if self.cleaned_data['organization'] != "":
            result = Organization.objects.filter(
                id=self.cleaned_data['organization']).distinct()
            if result:
                result = result[0]
        return result


class OfficeListForm(forms.Form):
    """office list form"""
    bureau = forms.CharField(label=_('office').capitalize(), required=True)

    def search(self):
        """search office method"""
        result = None
        if self.cleaned_data['bureau'] != "":
            result = Office.objects.filter(
                id=self.cleaned_data['bureau']).distinct()
            if result:
                result = result[0]
        return result
