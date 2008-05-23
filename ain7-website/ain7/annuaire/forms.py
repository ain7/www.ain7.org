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

from django import newforms as forms
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404

from ain7.fields import AutoCompleteField
from ain7.widgets import DateTimeWidget
from ain7.annuaire.models import *
from ain7.search_engine.models import SearchFilter

dateWidget = DateTimeWidget()
dateWidget.dformat = '%d/%m/%Y'
dateTimeWidget = DateTimeWidget()
dateTimeWidget.dformat = '%d/%m/%Y %H:%M'

class SearchPersonForm(forms.Form):
    last_name = forms.CharField(label=_('Last name'), max_length=50, required=False)
    first_name = forms.CharField(label=_('First name'), max_length=50, required=False)
    promo = forms.IntegerField(label=_('Promo'), required=False, widget=AutoCompleteField(url='/ajax/promo/'))
    track = forms.IntegerField(label=_('Track'), required=False, widget=AutoCompleteField(url='/ajax/track/'))
    organization = forms.CharField(label=_('company').capitalize(), max_length=50, required=False)

    def criteria(self):
        # criteres sur le nom et prenom, et sur l'organisation
        criteria={
            'person__last_name__icontains': self.cleaned_data['last_name'].encode('utf8'),
            'person__first_name__icontains': self.cleaned_data['first_name'].encode('utf8')}
        if self.cleaned_data['organization']!='':
            criteria['positions__office__company__name__icontains'] = \
                self.cleaned_data['organization'].encode('utf8')
        # ici on commence par rechercher toutes les promos
        # qui concordent avec l'annee de promotion et la filiere
        # saisis par l'utilisateur.
        promoCriteria={}
        if self.cleaned_data['promo'] != -1:
            promoCriteria['year']=self.cleaned_data['promo']
        if self.cleaned_data['track'] != -1:
            promoCriteria['track']=\
                Track.objects.get(id=self.cleaned_data['track'])
        # on ajoute ces promos aux critères de recherche
        # si elle ne sont pas vides
        if len(promoCriteria)!=0:
            # Pour éviter http://groups.google.es/group/django-users/browse_thread/thread/32143d024b17dd00,
            # on convertit en liste
            criteria['promos__in']=\
                [promo for promo in Promo.objects.filter(**promoCriteria)]
        return criteria

    def search(self, criteria):
        return AIn7Member.objects.filter(**criteria).distinct()

class SendmailForm(forms.Form):
    subject = forms.CharField(label=_('subject'),max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))
    body = forms.CharField(label=_('body'),max_length=500, required=False, widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':95}))
    send_test = forms.BooleanField(label=_('Send me a test'), required=False)

class NewMemberForm(forms.Form):
    first_name = forms.CharField(label=_('First name'),max_length=50, required=True, widget=forms.TextInput(attrs={'size':50}))
    last_name = forms.CharField(label=_('Last name'),max_length=50, required=True, widget=forms.TextInput(attrs={'size': 50}))
    mail = forms.EmailField(label=_('Mail'),max_length=50, required=True, widget=forms.TextInput(attrs={'size': 50}))
    nationality = forms.IntegerField(label=_('Nationality'), required=True, widget=AutoCompleteField(url='/ajax/nationality/'))
    birth_date = forms.DateTimeField(label=_('Date of birth'), required=True, widget=dateWidget)
    sex = forms.ChoiceField(label=_('sex'), required=True, choices=Person.SEX)
    promo = forms.IntegerField(label=_('Promo'), required=True, widget=AutoCompleteField(url='/ajax/promo/'))
    track = forms.IntegerField(label=_('Track'), required=True,  widget=AutoCompleteField(url='/ajax/track/'))

    def save(self):
        login = (self.cleaned_data['first_name'][0]+self.cleaned_data['last_name']).lower()
        mail = self.cleaned_data['mail']
        new_user = User.objects.create_user(login, mail, 'password')
        new_user.first_name = self.cleaned_data['first_name']
        new_user.last_name = self.cleaned_data['last_name']
        new_user.save()
        
        new_person = Person()
        new_person.user = new_user
        new_person.first_name = self.cleaned_data['first_name']
        new_person.last_name = self.cleaned_data['last_name']
        new_person.complete_name = \
            new_person.first_name+' '+new_person.last_name
        new_person.sex = self.cleaned_data['sex']
        new_person.birth_date = datetime.date(1978,11,18)
        new_person.country = \
            Country.objects.get(id=self.cleaned_data['nationality'])
        new_person.save()

        new_ain7member = AIn7Member()
        new_ain7member.person = new_person
        new_ain7member.marital_status = \
            MaritalStatus.objects.get(status="Célibataire")
        new_ain7member.display_cv_in_directory = False
        new_ain7member.display_cv_in_job_section = False
        new_ain7member.receive_job_offers = False
        new_ain7member.member_type = \
            MemberType.objects.get(type="Membre actif")
        new_ain7member.person_type = PersonType.objects.get(type=u"Étudiant")
        new_ain7member.activity = Activity.objects.get(activity="Connue")
        new_ain7member.save()
        new_ain7member.promos.add(
            Promo.objects.get(id=self.cleaned_data['promo']))
        new_ain7member.save()

        new_couriel = Email()
        new_couriel.person = new_person
        new_couriel.email = self.cleaned_data['mail']
        new_couriel.preferred_email = True
        new_couriel.save()

        return new_person
    

class ChooseFieldForm(forms.Form):
    chosenField = forms.ChoiceField(label=_('Field'), required=True,
        choices = [])

class SearchFilterForm(forms.ModelForm):
    class Meta:
        model = SearchFilter
        fields = ('name')

class PersonForm(forms.ModelForm):
    sex = forms.CharField(widget=forms.Select(choices=Person.SEX))
    class Meta:
        model = Person
        exclude = ('user')

class AIn7MemberForm(forms.ModelForm):
    class Meta:
        model = AIn7Member
        exclude = ('person','avatar')

class EmailForm(forms.ModelForm):
    class Meta:
        model = Email
        exclude = ('person')

class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = PhoneNumber
        exclude = ('person')

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ('person')

class InstantMessagingForm(forms.ModelForm):
    class Meta:
        model = InstantMessaging
        exclude = ('person')

class IRCForm(forms.ModelForm):
    class Meta:
        model = IRC
        exclude = ('person')

class WebSiteForm(forms.ModelForm):
    class Meta:
        model = WebSite
        exclude = ('person')

class ClubMembershipForm(forms.ModelForm):
    class Meta:
        model = ClubMembership
        exclude = ('member')

class AIn7SubscriptionForm(forms.ModelForm):
    date = forms.DateTimeField(label=_('date').capitalize(),
        widget=dateTimeWidget)
    class Meta:
        model = AIn7Subscription
        exclude = ('member')
