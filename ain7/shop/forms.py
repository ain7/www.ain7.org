# -*- coding: utf-8
"""
 ain7/shop/forms.py
"""
#
#   Copyright © 2007-2016 AIn7 Devel Team
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
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from ain7.shop.models import Payment


class PaymentMethodForm(forms.ModelForm):

    class Meta:
        model = Payment
        fields = ('type',)


class PaymentForm(forms.ModelForm):
    """payment form"""
    date = forms.DateTimeField(label=_('Payment Date'), required=False)
    deposited = forms.DateTimeField(label=_('Deposit Date'), required=False)

    class Meta:
        """Payment meta information"""
        model = Payment
        exclude = ('method', 'person')

