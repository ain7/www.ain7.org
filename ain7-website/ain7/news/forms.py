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

from django import forms
from django.utils.translation import ugettext as _

from ain7.fields import AutoCompleteField
from ain7.widgets import DateTimeWidget
from ain7.news.models import *

dateWidget = DateTimeWidget()
dateWidget.dformat = '%d/%m/%Y'

class SearchNewsForm(forms.Form):
    title = forms.CharField(label=_('News title'), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'40'}))
    date = forms.DateField(label=_('Date'), required=False,
        widget=dateWidget)
    content = forms.CharField(label=_('News content'), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'40'}))

    def search(self):
        criteria = {'title__icontains': self.cleaned_data['title'],
                    'description__icontains': self.cleaned_data['content']}
        if self.cleaned_data['date']:
            inputdate = self.cleaned_data['date']
            criteria['creation_date__year'] = inputdate.year
            criteria['creation_date__month'] = inputdate.month
            criteria['creation_date__day'] = inputdate.day
        return NewsItem.objects.filter(**criteria)

class NewsForm(forms.ModelForm):
    title = forms.CharField(label=_('title').capitalize(), max_length=100,
        required=False, widget=forms.TextInput(attrs={'size':'50'}))
    description = forms.CharField(label=_('description').capitalize(),
        required=False,
        widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':60}))
    class Meta:
        model = NewsItem
