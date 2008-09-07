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

from django import forms
from django.utils.translation import ugettext as _

from ain7.fields import AutoCompleteField
from ain7.annuaire.models import Person
from ain7.groupes_professionnels.models import GroupPro, Membership

class SubscribeGroupProForm(forms.Form):
    member = forms.IntegerField(label=_('Person to subscribe'), widget=AutoCompleteField(url='/ajax/person/'))
    is_coordinator = forms.BooleanField(label=_('Is coordinator'), required=False)

    def save(self, group=None):
        membership = Membership()
        membership.member = \
            Person.objects.get(user__id=self.cleaned_data['member'])
        membership.group = group
        membership.is_coordinator = self.cleaned_data['is_coordinator']
        membership.save()
        print membership
        return membership

class GroupProForm(forms.ModelForm):
    web_page = forms.CharField(label=_('web page').capitalize(),
        widget = forms.widgets.Textarea(attrs={'rows':10, 'cols':90}),
        required=False)
    
    class Meta:
        model = GroupPro
