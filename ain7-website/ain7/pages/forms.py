# -*- coding: utf-8
#
# pages/forms.py
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

from django.forms.util import ValidationError

from ain7.annuaire.models import Email

class LostPasswordForm(forms.Form):
    """ Form to request a new password (when you loose the first one) """
    email = forms.EmailField(required=True)

    def clean_email(self):
        e = self.cleaned_data['email']

        try:
            Email.objects.get(email=e)
        except Email.DoesNotExist:
            raise ValidationError(_('This should be the email address registered for your AIn7 account.'))
        else:
            return self.cleaned_data['email']
