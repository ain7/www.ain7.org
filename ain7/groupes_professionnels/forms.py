# -*- coding: utf-8 -*-
"""
 ain7/groupes_professionnels/forms.py
"""
#
#   Copyright © 2007-2011 AIn7 Devel Team
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
import re

from django import forms
from django.forms.util import ValidationError
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person
from ain7.fields import AutoCompleteField
from ain7.groups.models import Member, Group, GroupLeader
from ain7.widgets import DateTimeWidget


DATE_WIDGET = DateTimeWidget()
DATE_WIDGET.dformat = '%d/%m/%Y'

class SubscribeGroupProForm(forms.Form):
    """Subscribe Group Pro Form"""

    member = forms.IntegerField(label=_('Person to subscribe'),
        widget=AutoCompleteField(completed_obj_name='person'))

    def save(self, group=None):
        """save group pro membership"""
        membership = Member()
        membership.member = \
            Person.objects.get(user__id=self.cleaned_data['member'])
        membership.group = group
        membership.save()
        return membership

    def clean_member(self):
        """checker the new member"""
        member = self.cleaned_data['member']
        if member == None:
            raise ValidationError(_('This field is mandatory.'))
        else:
            try:
                Person.objects.get(id=self.cleaned_data['member'])
            except Person.DoesNotExist:
                raise ValidationError(
                    _('This person does not exist in the base.'))
            return member
    
class UnsubscribeGroupProForm(forms.Form):
    """unsubscribe from a professionnal group"""
    member = forms.IntegerField(label=_('Person to unsubscribe'),
        widget=AutoCompleteField(completed_obj_name='person'))

    def unsubscribe(self, group=None):
        """unsubscribe from a group pro method"""
        person = Person.objects.get(user__id=self.cleaned_data['member'])
        membership = Member.objects\
            .filter(group=group, member=person)\
            .exclude(end_date__isnull=False,
                     end_date__lte=datetime.datetime.now())\
            .latest('end_date')
        membership.end_date = datetime.datetime.today()
        membership.save()

class GroupProForm(forms.ModelForm):
    """group pro form"""
    slug = forms.CharField(label=_('slug').capitalize(),
        widget = forms.TextInput(attrs={'size': 40}), 
        required=False)
    about = forms.CharField(label=_('about').capitalize(),
        widget = forms.widgets.Textarea(attrs={'rows':10, 'cols':90}),
        required=False)

    def clean_slug(self):
        """check group name before registering"""
        if not re.match(r'^[a-z0-9\-_]+$', self.cleaned_data['slug']):
            raise forms.ValidationError(
                _('Please only use alphanumeric characters'))
        if Group.objects.filter(name=self.cleaned_data['slug']).count() > 1:
            raise forms.ValidationError(
                _('A group with this slug already exists'))
        return self.cleaned_data['slug']

    class Meta:
        """group pro meta"""
        model = Group
        exclude = ['type', 'access', 'private', 'web_site', 'email',]

    def save(self, user=None):
        """save group pro form method"""
        group_pro =  super(GroupProForm, self).save()
        group_pro.logged_save(user.person)
        return group_pro

class RoleForm(forms.ModelForm):
    """role form"""

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
        """clean membership en date"""

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

