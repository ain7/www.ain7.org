# -*- coding: utf-8
"""
 ain7/annuaire/forms.py
"""
#
#   Copyright © 2007-2018 AIn7 Devel Team
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
from django.contrib.auth.models import User
from django.forms.utils import ValidationError
from django.utils import timezone

from ain7.annuaire.models import (
    AIn7Member, Promo, Track, PromoYear, Person,
    Country, PersonPrivate, MemberType,
    PersonType, MaritalStatus, Email
)

from ain7.utils import generate_login


class NewMemberForm(forms.Form):
    """new member form"""
    first_name = forms.CharField(
        label=_('First name'), max_length=50,
        required=True, widget=forms.TextInput(attrs={'size': 40})
    )
    last_name = forms.CharField(
        label=_('Last name'), max_length=50,
        required=True, widget=forms.TextInput(attrs={'size': 40})
    )
    mail = forms.EmailField(
        label=_('Mail'), max_length=50, required=True,
        widget=forms.TextInput(attrs={'size': 40})
    )
    nationality = forms.IntegerField(label=_('Nationality'), required=False)
    birth_date = forms.DateField(label=_('Date of birth'), required=False)
    sex = forms.ChoiceField(label=_('Sex'), required=True, choices=Person.SEX)
    promoyear = forms.IntegerField(label=_('Promo year'), required=False)
    track = forms.IntegerField(label=_('Track'), required=False)

    def genlogin(self):
        """login generation"""
        return generate_login(
            self.cleaned_data['first_name'],
            self.cleaned_data['last_name'],
        )

    def clean_birth_date(self):
        """check birth date"""
        bdate = self.cleaned_data['birth_date']

        now = timezone.now().date()

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
            if self.cleaned_data['promoyear'] and self.cleaned_data['track']:
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

        new_person_private = PersonPrivate()
        new_person_private.person = new_person
        new_person_private.person_type = PersonType.objects.get(type=u"Elèves")
        new_person_private.member_type = \
            MemberType.objects.get(type="Membre actif")
        new_person_private.save()

        new_ain7member = AIn7Member()
        new_ain7member.person = new_person
        new_ain7member.marital_status = MaritalStatus.objects.get(pk=2)
        new_ain7member.receive_job_offers = False
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


class ChangePasswordForm(forms.Form):
    """ Change password and/or login"""
    login = forms.CharField(label=_('Login:'), max_length=50, required=True)
    password = forms.CharField(
        label=_('Password:'), max_length=50,
        required=True, widget=forms.PasswordInput()
    )
    new_password1 = forms.CharField(
        label=_('New password:'), max_length=50,
        required=True, widget=forms.PasswordInput()
    )
    new_password2 = forms.CharField(
        label=_('Confirm password:'), max_length=50,
        required=True, widget=forms.PasswordInput()
    )

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
