# -*- coding: utf-8
#
# annuaire/forms.py
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
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.forms.util import ValidationError

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
    promoyear = forms.IntegerField(label=_('Promo year'), required=False, widget=AutoCompleteField(url='/ajax/promoyear/'))
    track = forms.IntegerField(label=_('Track'), required=False, widget=AutoCompleteField(url='/ajax/track/'))
    organization = forms.IntegerField(label=_('organization').capitalize(), required=False,widget=AutoCompleteField(url='/ajax/organization/'))

    def criteria(self):
        q = models.Q()
        if self.cleaned_data['last_name']:
            ln = self.cleaned_data['last_name']
            q &= models.Q(person__last_name__icontains=ln) | \
                models.Q(person__maiden_name__icontains=ln)
        if self.cleaned_data['first_name']:
            q &= models.Q(person__first_name__icontains=
                self.cleaned_data['first_name'])
        if self.cleaned_data['organization']:
            q &= models.Q(positions__office__organization__id=\
                self.cleaned_data['organization'])

        # ici on commence par rechercher toutes les promos
        # qui concordent avec l'annee de promotion et la filiere
        # saisis par l'utilisateur.
        promoCriteria={}
        if self.cleaned_data['promoyear']:
            promoCriteria['year'] = PromoYear.objects.get(id=self.cleaned_data['promoyear'])
        if self.cleaned_data['track']:
            promoCriteria['track'] = Track.objects.get(id=self.cleaned_data['track'])
        # on ajoute ces promos aux criteres de recherche
        # si elle ne sont pas vides
        if len(promoCriteria)!=0:
            # Pour éviter http://groups.google.es/group/django-users/browse_thread/thread/32143d024b17dd00,
            # on convertit en liste
            q &= models.Q(promos__in=
                [promo for promo in Promo.objects.filter(**promoCriteria)])
        return q

    def search(self, criteria):
        return AIn7Member.objects.filter(criteria).distinct().order_by('person__last_name','person__first_name')

class SendmailForm(forms.Form):
    subject = forms.CharField(label=_('subject'),max_length=50, required=False, widget=forms.TextInput(attrs={'size':'40'}))
    body = forms.CharField(label=_('body'),max_length=500, required=False, widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':95}))
    send_test = forms.BooleanField(label=_('Send me a test'), required=False)

class NewMemberForm(forms.Form):
    first_name = forms.CharField(label=_('First name'),max_length=50, required=True, widget=forms.TextInput(attrs={'size':40}))
    last_name = forms.CharField(label=_('Last name'),max_length=50, required=True, widget=forms.TextInput(attrs={'size': 40}))
    mail = forms.EmailField(label=_('Mail'),max_length=50, required=True, widget=forms.TextInput(attrs={'size': 40}))
    nationality = forms.IntegerField(label=_('Nationality'), required=True, widget=AutoCompleteField(url='/ajax/nationality/',addable=True))
    birth_date = forms.DateTimeField(label=_('Date of birth'), required=True, widget=dateWidget)
    sex = forms.ChoiceField(label=_('Sex'), required=True, choices=Person.SEX)
    promoyear = forms.IntegerField(label=_('Promo year'), required=True, widget=AutoCompleteField(url='/ajax/promoyear/'))
    track = forms.IntegerField(label=_('Track'), required=True,  widget=AutoCompleteField(url='/ajax/track/'))

    def genlogin(self):
        login = (self.cleaned_data['first_name'][0]+self.cleaned_data['last_name']).lower()

        tries = 0
        while (User.objects.filter(username=login).count() > 0):
            tries = tries + 1
            if tries < len(self.cleaned_data['first_name']):
                login = (self.cleaned_data['first_name'][0:tries]+self.cleaned_data['last_name']).lower()
            else:
                login = (self.cleaned_data['first_name'][0]+self.cleaned_data['last_name']+str(tries)).lower()

        return login

    def clean_birth_date(self):
        d = self.cleaned_data['birth_date']

        now = datetime.datetime.now()

        if (now < d):
            raise ValidationError(_('Invalid date of birth.'))

        return self.cleaned_data['birth_date']

    def clean_nationality(self):
        n = self.cleaned_data['nationality']

        try:
            Country.objects.get(id=n)
        except Country.DoesNotExist:
            raise ValidationError(_('The entered nationality does not exist.'))
        else:
            return self.cleaned_data['nationality']

    def clean_promoyear(self):
        p = self.cleaned_data['promoyear']

        try:
            PromoYear.objects.get(id=p)
        except PromoYear.DoesNotExist:
            raise ValidationError(_('The entered year of promotion does not exist.'))
        else:
            return self.cleaned_data['promoyear']

    def clean_track(self):
        t = self.cleaned_data['track']
        try:
            track = Track.objects.get(id=t)
        except Track.DoesNotExist:
            raise ValidationError(_('The entered track does not exist.'))

        if self.cleaned_data.has_key('promoyear'):
            p = self.cleaned_data['promoyear']
            if self.cleaned_data['promoyear']  and self.cleaned_data['track']:
                try:
                    promo_year = PromoYear.objects.get(id=p)
                    promo = Promo.objects.get(year=promo_year,track=track)
                except PromoYear.DoesNotExist:
                    raise ValidationError(_('The entered year of promotion does not exist.'))
                except Promo.DoesNotExist:
                    raise ValidationError(_('There is no year of promotion and track associated.'))
                else:
                    return self.cleaned_data['track']

    def save(self):
        login = self.genlogin()
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
        new_person.birth_date = self.cleaned_data['birth_date']
        new_person.country = \
            Country.objects.get(id=self.cleaned_data['nationality'])
        new_person.save()

        new_ain7member = AIn7Member()
        new_ain7member.person = new_person
        new_ain7member.marital_status = \
            MaritalStatus.objects.get(pk=1)
        new_ain7member.display_cv_in_directory = False
        new_ain7member.display_cv_in_job_section = False
        new_ain7member.receive_job_offers = False
        new_ain7member.member_type = \
            MemberType.objects.get(type="Membre actif")
        new_ain7member.person_type = PersonType.objects.get(type=u"Étudiant")
        new_ain7member.activity = Activity.objects.get(activity="Connue")
        new_ain7member.save()

        track = Track.objects.get(id=self.cleaned_data['track'])
        promoyear = PromoYear.objects.get(id=self.cleaned_data['promoyear'])
   
        new_ain7member.promos.add(Promo.objects.get(track=track,year=promoyear))
        new_ain7member.save()

        new_couriel = Email()
        new_couriel.person = new_person
        new_couriel.email = self.cleaned_data['mail']
        new_couriel.preferred_email = True
        new_couriel.save()

        return new_person
    

class PersonForm(forms.ModelForm):
    sex = forms.CharField(widget=forms.Select(choices=Person.SEX), label=_('Sex'))
    birth_date = forms.DateTimeField(label=_('birth date').capitalize(),
        widget=dateWidget, required=False)
    death_date = forms.DateTimeField(label=_('death date').capitalize(),
        widget=dateWidget, required=False)
    class Meta:
        model = Person
        exclude = ('user')
    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        # on convertit une liste de noms de pays en une liste de nationalités
        nats = []
        for i,c in self.fields['country'].choices:
            if i:
                nats.append((i,Country.objects.get(name=c).nationality))
            else:
                nats.append((i,c))
        self.fields['country'].choices = nats
    def clean_death_date(self):
        if self.cleaned_data.get('birth_date') and \
            self.cleaned_data.get('death_date') and \
            self.cleaned_data['birth_date']>self.cleaned_data['death_date']:
            raise forms.ValidationError(_('Birth date is later than death date'))
        return self.cleaned_data['death_date']



class AIn7MemberForm(forms.ModelForm):
    receive_job_offers_for_tracks = forms.ModelMultipleChoiceField(queryset=Track.objects.filter(active=True), required=False)
    class Meta:
        model = AIn7Member
        exclude = ('person','promos')

class EmailForm(forms.ModelForm):
    class Meta:
        model = Email
        exclude = ('person')

class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = PhoneNumber
        exclude = ('person')

class PromoForm(forms.Form):
    promoyear = forms.IntegerField(label=_('Promo year'), required=False, widget=AutoCompleteField(url='/ajax/promoyear/'))
    track = forms.IntegerField(label=_('Track'), required=False, widget=AutoCompleteField(url='/ajax/track/'))

    def clean_promoyear(self):
        p = self.cleaned_data['promoyear']

        try:
            PromoYear.objects.get(id=p)
        except PromoYear.DoesNotExist:
            raise ValidationError(_('The entered year of promotion does not exist.'))
        else:
            return self.cleaned_data['promoyear']

    def clean_track(self):
        t = self.cleaned_data['track']
        try:
            track = Track.objects.get(id=t)
        except Track.DoesNotExist:
            raise ValidationError(_('The entered track does not exist.'))

        if self.cleaned_data.has_key('promoyear'):
            p = self.cleaned_data['promoyear']
            if self.cleaned_data['promoyear'] and self.cleaned_data['track']:
                try:
                    promo_year = PromoYear.objects.get(id=p)
                    promo = Promo.objects.get(year=promo_year,track=track)
                except PromoYear.DoesNotExist:
                    raise ValidationError(_('The entered year of promotion does not exist.'))
                except Promo.DoesNotExist:
                    raise ValidationError(_('There is no year of promotion and track associated.'))
                else:
                    return self.cleaned_data['track']

    def search(self):
        track = Track.objects.get(id=self.cleaned_data['track'])
        promo_year = PromoYear.objects.get(id=self.cleaned_data['promoyear'])
        promo = Promo.objects.get(year=promo_year,track=track)
        return promo

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
    start_date = forms.DateTimeField(label=_('start date').capitalize(),widget=dateTimeWidget)
    end_date = forms.DateTimeField(label=_('end date').capitalize(),widget=dateTimeWidget)
    class Meta:
        model = ClubMembership
        exclude = ('member')
