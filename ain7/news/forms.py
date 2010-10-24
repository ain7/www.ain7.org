# -*- coding: utf-8
"""
 ain7/news/forms.py
"""
#
#   Copyright © 2007-2010 AIn7 Devel Team
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
from django.db.models import Q
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person
from ain7.groups.models import Group
from ain7.news.models import NewsItem, EventOrganizer, RSVPAnswer
from ain7.fields import AutoCompleteField
from ain7.utils import AIn7ModelForm, AIn7Form
from ain7.widgets import DateTimeWidget


DATE_TIME_WIDGET = DateTimeWidget()
DATE_TIME_WIDGET.dformat = '%d/%m/%Y %H:%M'

class SearchNewsForm(forms.Form):
    """search news form"""
    title = forms.CharField(label=_('News title'), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'40'}))
    date = forms.DateField(label=_('Date'), required=False,
        widget=DATE_TIME_WIDGET)
    content = forms.CharField(label=_('News content'), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'40'}))

    def search(self):
        """search news method"""
        criteria = {'title__icontains': self.cleaned_data['title'],
                    'body__icontains': self.cleaned_data['content']}
        if self.cleaned_data['date']:
            inputdate = self.cleaned_data['date']
            criteria['creation_date__year'] = inputdate.year
            criteria['creation_date__month'] = inputdate.month
            criteria['creation_date__day'] = inputdate.day
        return NewsItem.objects.filter(date__isnull=True).filter(**criteria)

class NewsForm(AIn7ModelForm):
    """news form"""
    title = forms.CharField(label=_('title').capitalize(), max_length=100,
        required=True, widget=forms.TextInput(attrs={'size':'50'}))
    body = forms.CharField(label=_('body').capitalize(),
        required=True,
        widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':60}))

    class Meta:
        """news form meta"""
        model = NewsItem
        exclude = ('slug', 'shorttext', 'date', 'location', 'status', \
            'contact_email', 'link', 'pictures_gallery')

    def __init__(self, *args, **kwargs):
        super (NewsForm,self ).__init__(*args,**kwargs)
        self.fields['groups'].queryset = Group.objects.filter(\
            Q(type__name='ain7-regional') | Q(type__name='ain7-professionnel'))


    def save(self, *args, **kwargs):
        """save event"""
        if kwargs.has_key('contributor'):
            contributor = kwargs['contributor']
            news = super(NewsForm, self).save()
            news.logged_save(contributor)
        else:
            news = super(NewsForm, self).save()
        return news

class SearchEventForm(forms.Form):
    """search event form"""
    title = forms.CharField(label=_('Event title'), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'40'}))
    location = forms.CharField(label=_('Location'), max_length=50,
        required=False, widget=forms.TextInput(attrs={'size':'40'}))

    def search(self):
        """search event method"""
        return NewsItem.objects.filter(
            title__icontains=self.cleaned_data['title'],
            location__icontains=self.cleaned_data['location']).order_by('-date')

class ContactEventForm(AIn7Form):
    """contact event form"""
    message = forms.CharField( label=_('your message').capitalize(),
        required=True,
        widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':65}))
    sender = forms.EmailField( label=_('your email').capitalize(),
        required=True)

class EventForm(AIn7ModelForm):
    """event form"""
    title = forms.CharField(label=_('Title'), max_length=60,
        widget=forms.TextInput(attrs={'size':'60'}))
    body = forms.CharField( label=_('description').capitalize(),
        required=False,
        widget=forms.widgets.Textarea(attrs={'rows':10, 'cols':40}))
    date = forms.DateTimeField(label=_('date').capitalize(),
        widget=DATE_TIME_WIDGET)

    class Meta:
        """event form meta"""
        model = NewsItem
        exclude = ('organizers','shorttext', 'slug',)

    def __init__(self, *args, **kwargs):
        super (EventForm,self ).__init__(*args,**kwargs)
        self.fields['groups'].queryset = Group.objects.filter(\
            Q(type__name='ain7-regional') | Q(type__name='ain7-professionnel'))

    def save(self, *args, **kwargs):
        """save event"""
        if kwargs.has_key('contributor'):
            contributor = kwargs['contributor']
            event = super(EventForm, self).save()
            event.logged_save(contributor)
        else:
            event = super(EventForm, self).save()
        return event

class EventOrganizerForm(forms.ModelForm):
    """event organizer form"""
    organizer = forms.IntegerField(label=_('organizer').capitalize(),
        widget=AutoCompleteField(completed_obj_name='person'))

    class Meta:
        """event organizer form meta"""
        model = EventOrganizer
        exclude = ('event',)

    def save(self, *args, **kwargs):
        """event organizer form save"""
        if kwargs.has_key('contributor') and kwargs.has_key('event'):
            event = kwargs['event']
            event_org = EventOrganizer()
            event_org.event = event
            event_org.organizer = Person.objects.get(
                id=self.cleaned_data['organizer'])
            event_org.send_email_for_new_subscriptions = \
                self.cleaned_data['send_email_for_new_subscriptions']
            event_org.save()
            event.logged_save(kwargs['contributor'])
            return event_org
        return None

class RSVPAnswerForm(forms.ModelForm):
    """rsvp answer for an event"""

    person = forms.IntegerField(label=_('person').capitalize(),
        widget=AutoCompleteField(completed_obj_name='person'))

    class Meta:
        """event rsvp answer meta"""
        model = RSVPAnswer
        exclude = ('created_by', 'updated_by', 'event', 'payment')

    def __init__(self, *args, **kwargs):
        self.edit_person = True
        self.myself = False
        if kwargs.has_key('edit_person'):
            self.edit_person = kwargs['edit_person']
            del kwargs['edit_person']
        if kwargs.has_key('myself'):
            self.myself = kwargs['myself']
            del kwargs['myself']
        super (RSVPAnswerForm,self ).__init__(*args,**kwargs)
        if not self.edit_person:
            del self.fields['person']
        if self.myself:
            del self.fields['yes']
            del self.fields['no']
            del self.fields['maybe']


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

