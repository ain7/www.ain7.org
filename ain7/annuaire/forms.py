# -*- coding: utf-8
"""
 ain7/annuaire/forms.py
"""
#
#   Copyright © 2007-2018 AIn7 Devel Team
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
from django.contrib.auth.models import User
from django.forms.utils import ValidationError
from django.utils import timezone

from ain7.annuaire.models import (
    AIn7Member, Promo, Track, PromoYear, Person,
    Country, PersonPrivate, MemberType,
    PersonType, MaritalStatus, Email
)

from ain7.utils import generate_login


class ChangePasswordForm(forms.Form):
    """ Change password and/or login"""
    login = forms.CharField(label=_('Login:'), max_length=50, required=True)
    password = forms.CharField(
        label=_('Password:'), max_length=50,
        required=True, widget=forms.PasswordInput()
    )
    new_password1 = forms.CharField(
        label=_('New password:'), max_length=50,
        required=True, widget=forms.PasswordInput()
    )
    new_password2 = forms.CharField(
        label=_('Confirm password:'), max_length=50,
        required=True, widget=forms.PasswordInput()
    )

    def clean(self):
        """check passwords"""
        cleaned_data = self.cleaned_data

        if cleaned_data.get('new_password1') and \
            cleaned_data.get('new_password2'):
            if not cleaned_data.get('new_password1') == \
                cleaned_data.get('new_password2'):
                raise ValidationError(_("Password doesn't match."))
            # TODO: check that password is strong enough ?

        return cleaned_data
