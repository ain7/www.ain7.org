# -*- coding: utf-8
"""
 ain7/adhesions/forms.py
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

from django import forms

from ain7.adhesions.models import Subscription, SubscriptionConfiguration


class SubscriptionForm(forms.ModelForm):
    """AIn7Member Subscription Form"""
    dues_amount = forms.IntegerField(widget=forms.HiddenInput())
    newspaper_amount = forms.IntegerField(required=False,
        widget=forms.HiddenInput())
    start_year = forms.IntegerField(initial=datetime.datetime.now().year, 
        widget=forms.HiddenInput())

    class Meta:
        """Meta SubscriptionForm"""
        model = Subscription
        exclude = ('old_id', 'member', 'validated', 'end_year', 'payment', 'date')

class ConfigurationForm(forms.ModelForm):
    """Subscription Configuration Form"""

    class Meta:
        """Meta ConfigurationForm"""
        model = SubscriptionConfiguration

