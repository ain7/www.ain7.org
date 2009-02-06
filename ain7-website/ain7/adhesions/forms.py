# -*- coding: utf-8
#
# annuaire/forms.py
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
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.forms.util import ValidationError

from ain7.fields import AutoCompleteField
from ain7.widgets import DateTimeWidget
from ain7.adhesions.models import *

dateWidget = DateTimeWidget()
dateWidget.dformat = '%d/%m/%Y'
dateTimeWidget = DateTimeWidget()
dateTimeWidget.dformat = '%d/%m/%Y %H:%M'

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        exclude = ('member', 'validated')

