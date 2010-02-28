# -*- coding: utf-8
"""
 ain7/annuaire/forms.py
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

import datetime

from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.forms.util import ValidationError

from ain7.fields import AutoCompleteField
from ain7.widgets import DateTimeWidget
from ain7.annuaire.models import *


DATE_WIDGET = DateTimeWidget()
DATE_WIDGET.dformat = '%d/%m/%Y'
DATE_TIME_WIDGET = DateTimeWidget()
DATE_TIME_WIDGET.dformat = '%d/%m/%Y %H:%M'

class SearchPersonForm(forms.Form):
    """search person form"""
    last_name = forms.CharField(label=_('Last name'), max_length=50,
        required=False)
    first_name = forms.CharField(label=_('First name'), max_length=50,
        required=False)
    promoyear = forms.IntegerField(label=_('Promo year'), required=False,
        widget=AutoCompleteField(completed_obj_name='promoyear'))
    track = forms.IntegerField(label=_('Track'), required=False,
        widget=AutoCompleteField(completed_obj_name='track'))
    organization = forms.CharField(label=_('organization').capitalize(),
        max_length=50, required=False)

    def criteria(self):
        """define search criteria for a person"""
        querry = models.Q()
        if self.cleaned_data['last_name']:
            querry &= models.Q(person__last_name__icontains=\
                self.cleaned_data['last_name']) | \
                models.Q(person__maiden_name__icontains=\
                    self.cleaned_data['last_name'])
        if self.cleaned_data['first_name']:
            querry &= models.Q(person__first_name__icontains=
                self.cleaned_data['first_name'])
        if self.cleaned_data['organization']:
            querry &= models.Q(positions__office__organization__name__icontains\
                =self.cleaned_data['organization']) | \
                 models.Q(positions__office__name__icontains=\
                 self.cleaned_data['organization'])

        # ici on commence par rechercher toutes les promos
        # qui concordent avec l'annee de promotion et la filiere
        # saisis par l'utilisateur.
        promo_criteria = {}
        if self.cleaned_data['promoyear']:
            promo_criteria['year'] = PromoYear.objects.get(\
                id=self.cleaned_data['promoyear'])
        if self.cleaned_data['track']:
            promo_criteria['track'] = Track.objects.get(\
                id=self.cleaned_data['track'])
        # on ajoute ces promos aux criteres de recherche
        # si elle ne sont pas vides
        if len(promo_criteria)!=0:
            # Pour éviter
            # http://groups.google.es/group/django-users/browse_thread
            # /thread/32143d024b17dd00,
            # on convertit en liste
            querry &= models.Q(promos__in=
                [promo for promo in Promo.objects.filter(**promo_criteria)])

        return querry

    def search(self, criteria):
        """perform the search for a person"""
        return AIn7Member.objects.filter(criteria).distinct().\
            order_by('person__last_name','person__first_name')

class NewMemberForm(forms.Form):
    """new member form"""
    first_name = forms.CharField(label=_('First name'), max_length=50,
        required=True, widget=forms.TextInput(attrs={'size':40}))
    last_name = forms.CharField(label=_('Last name'), max_length=50,
        required=True, widget=forms.TextInput(attrs={'size': 40}))
    mail = forms.EmailField(label=_('Mail'), max_length=50, required=True,
        widget=forms.TextInput(attrs={'size': 40}))
    nationality = forms.IntegerField(label=_('Nationality'), required=False,
        widget=AutoCompleteField(completed_obj_name='nationality',addable=True))
    birth_date = forms.DateTimeField(label=_('Date of birth'), required=False,
        widget=DATE_WIDGET)
    sex = forms.ChoiceField(label=_('Sex'), required=True, choices=Person.SEX)
    promoyear = forms.IntegerField(label=_('Promo year'), required=True,
        widget=AutoCompleteField(completed_obj_name='promoyear'))
    track = forms.IntegerField(label=_('Track'), required=True, 
        widget=AutoCompleteField(completed_obj_name='track'))

    def genlogin(self):
        """login generation"""
        login = (self.cleaned_data['first_name'][0] + \
            self.cleaned_data['last_name']).lower()

        tries = 0
        while (User.objects.filter(username=login).count() > 0):
            tries = tries + 1
            if tries < len(self.cleaned_data['first_name']):
                login = (self.cleaned_data['first_name'][0:tries] + \
                    self.cleaned_data['last_name']).lower()
            else:
                login = (self.cleaned_data['first_name'][0] + \
                    self.cleaned_data['last_name'] + str(tries)).lower()

        return login

    def clean_birth_date(self):
        """check birth date"""
        bdate = self.cleaned_data['birth_date']

        now = datetime.datetime.now()

        if (bdate and (now < bdate)):
            raise ValidationError(_('Invalid date of birth'))

        return self.cleaned_data['birth_date']

    def clean_nationality(self):
        """check nationality"""
        nationality = self.cleaned_data['nationality']

        try:
            Country.objects.get(id=nationality)
        except Country.DoesNotExist:
            raise ValidationError(_('The entered nationality does not exist.'))
        else:
            return self.cleaned_data['nationality']

    def clean_promoyear(self):
        """check promo year"""
        promoyear = self.cleaned_data['promoyear']

        try:
            PromoYear.objects.get(id=promoyear)
        except PromoYear.DoesNotExist:
            raise ValidationError(_('The entered year of\
 promotion does not exist.'))
        else:
            return self.cleaned_data['promoyear']

    def clean_track(self):
        """check track"""
        track_id = self.cleaned_data['track']
        try:
            track = Track.objects.get(id=track_id)
        except Track.DoesNotExist:
            raise ValidationError(_('The entered track does not exist.'))

        if self.cleaned_data.has_key('promoyear'):
            promoyear_id = self.cleaned_data['promoyear']
            if self.cleaned_data['promoyear']  and self.cleaned_data['track']:
                try:
                    promo_year = PromoYear.objects.get(id=promoyear_id)
                    Promo.objects.get(year=promo_year, track=track)
                except PromoYear.DoesNotExist:
                    raise ValidationError(_('The entered year of promotion\
 does not exist.'))
                except Promo.DoesNotExist:
                    raise ValidationError(_('There is no year of promotion and\
 track associated.'))
                else:
                    return self.cleaned_data['track']

    def save(self):
        """save the new user"""
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
   
        new_ain7member.promos.add(Promo.objects.get(track=track,
            year=promoyear))
        new_ain7member.save()

        new_couriel = Email()
        new_couriel.person = new_person
        new_couriel.email = self.cleaned_data['mail']
        new_couriel.preferred_email = True
        new_couriel.save()

        return new_person
    
class PersonForm(forms.ModelForm):
    """person form with no death date"""
    sex = forms.CharField(widget=forms.Select(choices=Person.SEX),
        label=_('Sex'))
    birth_date = forms.DateTimeField(label=_('birth date').capitalize(),
        widget=DATE_WIDGET, required=False)
    country = forms.IntegerField(label=_('nationality'), required=False,
        widget=AutoCompleteField(completed_obj_name='nationality'))

    class Meta:
        """person form with no death date meta"""
        model = Person
        exclude = ('user','old_id')

    def clean_country(self):
        """person form no deatch clean_country"""
        country_id = self.cleaned_data['country']
        try:
            Country.objects.get(id=country_id)
        except Country.DoesNotExist:
            raise ValidationError(_('The entered nationality does not exist.'))
        else:
            return Country.objects.get(id=country_id)

class PersonPrivateForm(forms.ModelForm):
    """person private form"""
    death_date = forms.DateTimeField(label=_('death date').capitalize(),
        widget=DATE_WIDGET, required=False)

    class Meta:
        """person form meta"""
        model = PersonPrivate
        exclude = ('person')

    def clean_death_date(self):
        """check death date"""
        if self.cleaned_data.get('birth_date') and \
            self.cleaned_data.get('death_date') and \
            self.cleaned_data['birth_date']>self.cleaned_data['death_date']:
            raise forms.ValidationError(_('Birth date is later than\
 death date.'))
        return self.cleaned_data['death_date']


class AIn7MemberForm(forms.ModelForm):
    """AIn7Member Form"""

    class Meta:
        """AIn7 Member form meta"""
        model = AIn7Member
        exclude = ('person','promos')

class EmailForm(forms.ModelForm):
    """email form"""

    class Meta:
        """email form meta"""
        model = Email

class PhoneNumberForm(forms.ModelForm):
    """phone number form"""

    class Meta:
        """phone number form meta"""
        model = PhoneNumber

class PromoForm(forms.Form):
    """promo form"""
    promoyear = forms.IntegerField(label=_('Promo year'), required=False,
        widget=AutoCompleteField(completed_obj_name='promoyear'))
    track = forms.IntegerField(label=_('Track'), required=False,
        widget=AutoCompleteField(completed_obj_name='track'))

    def clean_promoyear(self):
        """check promo year"""
        promoyear_id = self.cleaned_data['promoyear']

        try:
            PromoYear.objects.get(id=promoyear_id)
        except PromoYear.DoesNotExist:
            raise ValidationError(_('The entered year of promotion\
 does not exist.'))
        else:
            return self.cleaned_data['promoyear']

    def clean_track(self):
        """check track"""
        track_id = self.cleaned_data['track']
        try:
            track = Track.objects.get(id=track_id)
        except Track.DoesNotExist:
            raise ValidationError(_('The entered track does not exist.'))

        if self.cleaned_data.has_key('promoyear'):
            promoyear_id = self.cleaned_data['promoyear']
            if self.cleaned_data['promoyear'] and self.cleaned_data['track']:
                try:
                    promo_year = PromoYear.objects.get(id=promoyear_id)
                    Promo.objects.get(year=promo_year, track=track)
                except PromoYear.DoesNotExist:
                    raise ValidationError(_('The entered year of promotion\
 does not exist.'))
                except Promo.DoesNotExist:
                    raise ValidationError(_('There is no year of promotion\
 and track associated.'))
                else:
                    return self.cleaned_data['track']

    def search(self):
        """perform search"""
        track = Track.objects.get(id=self.cleaned_data['track'])
        promo_year = PromoYear.objects.get(id=self.cleaned_data['promoyear'])
        promo = Promo.objects.get(year=promo_year, track=track)
        return promo

class AddressForm(forms.ModelForm):
    """address form"""
    country = forms.IntegerField(label=_('country').capitalize(),
        required=False,
        widget=AutoCompleteField(completed_obj_name='country'))

    class Meta:
        """address form meta"""
        model = Address

    def clean_country(self):
        """check country"""
        country_id = self.cleaned_data['country']
        try:
            return Country.objects.get(id=country_id)
        except Country.DoesNotExist:
            raise ValidationError(_('The entered country does not exist.'))
            return None

class InstantMessagingForm(forms.ModelForm):
    """Instant Messaging Form"""

    class Meta:
        """instant messaging form meta"""
        model = InstantMessaging

class IRCForm(forms.ModelForm):
    """IRC form"""

    class Meta:
        """IRC form meta"""
        model = IRC

class WebSiteForm(forms.ModelForm):
    """web site form"""

    class Meta:
        """web site form meta"""
        model = WebSite

class ClubMembershipForm(forms.ModelForm):
    "club membership form"""

    class Meta:
        """club membership form meta"""
        model = ClubMembership

class ChangePasswordForm(forms.Form):
    """ Change password and/or login"""
    login = forms.CharField(label=_('Login:'), max_length=50, required=True)
    password = forms.CharField(label=_('Password:'), max_length=50,
                         required=True, widget=forms.PasswordInput())
    new_password1 = forms.CharField(label=_('New password:'), max_length=50,
                         required=True, widget=forms.PasswordInput())
    new_password2 = forms.CharField(label=_('Confirm password:'), max_length=50,
                         required=True, widget=forms.PasswordInput())

    def clean(self):
        """check passwords"""
        cleaned_data = self.cleaned_data

        if cleaned_data.get('new_password1') and \
            cleaned_data.get('new_password2'):
            if not cleaned_data.get('new_password1') == \
                cleaned_data.get('new_password2'):
                raise ValidationError(_("Password doesn't match."))
            # TODO: check that password is strong enough ?

        return cleaned_data

