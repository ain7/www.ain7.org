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
from ain7.fields import AutoCompleteField

class SearchPersonForm(forms.Form):
    last_name = forms.CharField(label=_('Last name'), max_length=50, required=False)
    first_name = forms.CharField(label=_('First name'), max_length=50, required=False)
    promo = forms.IntegerField(label=_('Promo'), required=False, widget=AutoCompleteField(url='/ajax/promo/'))
    track = forms.IntegerField(label=_('Track'), required=False, widget=AutoCompleteField(url='/ajax/track/'))
    organization = forms.CharField(label=_('company').capitalize(), max_length=50, required=False)

    def criteria(self):
        # criteres sur le nom et prenom, et sur l'organisation
        criteria={
            'person__last_name__contains': self.clean_data['last_name'].encode('utf8'),
            'person__first_name__contains': self.clean_data['first_name'].encode('utf8'),
            'positions__office__company__name__contains': self.clean_data['organization'].encode('utf8'),}
        # ici on commence par rechercher toutes les promos
        # qui concordent avec l'annee de promotion et la filiere
        # saisis par l'utilisateur.
        promoCriteria={}
        if self.clean_data['promo'] != -1:
            promoCriteria['year']=self.clean_data['promo']
        if self.clean_data['track'] != -1:
            promoCriteria['track']=\
                Track.objects.get(id=self.clean_data['track'])
        # on ajoute ces promos aux critères de recherche
        # si elle ne sont pas vides
        if len(promoCriteria)!=0:
            criteria['promos__in']=Promo.objects.filter(**promoCriteria)
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
    mail = forms.CharField(label=_('Mail'),max_length=50, required=True, widget=forms.TextInput(attrs={'size': 50}))
    nationality = forms.IntegerField(label=_('Nationality'), required=True, widget=AutoCompleteField(url='/ajax/nationality/'))
    birth_date = forms.DateTimeField(label=_('Date of birth'), required=True)
    sex = forms.CharField(label=_('sex'), required=True)
    promo = forms.IntegerField(label=_('Promo'), required=True, widget=AutoCompleteField(url='/ajax/promo/'))
    track = forms.IntegerField(label=_('Track'), required=True,  widget=AutoCompleteField(url='/ajax/track/'))

    def save(self):
        login = (self.clean_data['first_name'][0]+self.clean_data['last_name']).lower()
        mail = self.clean_data['mail']
        new_user = User.objects.create_user(login, mail, 'password')
        new_user.first_name = self.clean_data['first_name']
        new_user.last_name = self.clean_data['last_name']
        new_user.save()
        
        new_person = Person()
        new_person.user = new_user
        new_person.first_name = self.clean_data['first_name']
        new_person.last_name = self.clean_data['last_name']
        new_person.complete_name = \
            new_person.first_name+' '+new_person.last_name
        new_person.sex = self.clean_data['sex']
        new_person.birth_date = datetime.date(1978,11,18)
        new_person.country = \
            Country.objects.get(id=self.clean_data['nationality'])
        new_person.save()

        new_ain7member = AIn7Member()
        new_ain7member.person = new_person
        new_ain7member.promos.add(
            Promo.objects.get(id=self.clean_data['promo']))
        new_ain7member.marital_status = \
            MaritalStatus.objects.get(status="Célibataire")
        new_ain7member.display_cv_in_directory = False
        new_ain7member.display_cv_in_job_section = False
        new_ain7member.receive_job_offers = False
        new_ain7member.member_type = \
            MemberType.objects.get(type="Membre actif")
        new_ain7member.person_type = PersonType.objects.get(type="Etudiant")
        new_ain7member.activity = Activity.objects.get(activity="Connue")
        new_ain7member.save()

        new_couriel = Email()
        new_couriel.person = new_person
        new_couriel.email = self.clean_data['mail']
        new_couriel.preferred_email = True
        new_couriel.save()

        return new_person
    

class ChooseFieldForm(forms.Form):
    chosenField = forms.ChoiceField(label=_('Field'), required=True,
        choices = [])
