# -*- coding: utf-8
#
# news/forms.py
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

from django import newforms as forms
from django.utils.translation import ugettext as _

from ain7.fields import AutoCompleteField
from ain7.news.models import *

class SearchNewsForm(forms.Form):
    title = forms.CharField(label=_('News title'), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'50'}))
    date = forms.DateField(label=_('Date'), required=False,
        widget=forms.TextInput(attrs={'size':'50'}))
    content = forms.CharField(label=_('News content'), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'50'}))


class NewsForm(forms.ModelForm):
    class Meta:
        model = NewsItem
        exclude = ('image')
