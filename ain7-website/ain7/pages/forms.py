# -*- coding: utf-8
#
# pages/forms.py
#
#   Copyright © 2007-2009 AIn7 Devel Team
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

class TextForm(forms.Form):
    title = forms.CharField(label=_('title'), max_length=150, required=False, widget=forms.TextInput(attrs={'size':80}))
    body = forms.CharField(label=_('body'),max_length=10000, required=False, widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':215}))

