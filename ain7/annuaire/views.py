# -*- coding: utf-8
"""
 ain7/annuaire/views.py
"""
#
#   Copyright © 2007-2017 AIn7 Devel Team
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

import vobject

from autocomplete_light import shortcuts as autocomplete_light

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404, redirect, render

from ain7.annuaire.models import (
    PersonPrivate, UserActivity, Promo,
    PhoneNumber, InstantMessaging, Email,
    WebSite, ClubMembership, Person, AIn7Member, Address,
    Position, EducationItem, LeisureItem, PublicationItem,
)
from ain7.annuaire.filters import AIn7MemberFilter, AIn7MemberAdvancedFilter
from ain7.annuaire.forms import (
    ChangePasswordForm, NewMemberForm
)
from ain7.decorators import access_required, confirmation_required
from ain7.utils import ain7_generic_delete, generate_login


@login_required
def home(request, user_name):
    user = get_object_or_404(User, username=user_name)
    user_id = Person.objects.get(user=user).id
    return details(request, user_id)


@login_required
def me(request):
    user_id = Person.objects.get(user=request.user).id
    return edit(request, user_id)


@access_required(groups=['ain7-membre', 'ain7-secretariat'])
def details(request, user_id):

    # ain7member = None
    last_activity = None
    is_myself = int(request.user.id) == int(user_id)

    person = get_object_or_404(Person, pk=user_id)
    personprivate = get_object_or_404(PersonPrivate, person=person)

    # if AIn7Member.objects.filter(person=person).count() > 0:
    #    ain7member = get_object_or_404(AIn7Member, person=person)

    if UserActivity.objects.filter(person=person):
        last_activity = UserActivity.objects.filter(person=person).latest('id')

    return render(request, 'annuaire/details.html', {
        'person': person,
        'is_myself': is_myself,
        'last_activity': last_activity,
        }
    )


@login_required
def search(request):

    filter = AIn7MemberFilter(request.GET, queryset=AIn7Member.objects.all())

    return render(request, 'annuaire/search.html', {
        'filter': filter,
        'request': request,
        }
    )


@login_required
def search_adv(request):

    filter = AIn7MemberAdvancedFilter(
        request.GET,
        queryset=AIn7Member.objects.all()
    )

    return render(request, 'annuaire/search.html', {
        'filter': filter,
        'request': request,
        }
    )


@login_required
def change_credentials(request, user_id):
    is_myself = int(request.user.id) == int(user_id)
    person = get_object_or_404(Person, pk=user_id)

    if not is_myself:
        return HttpResponseRedirect(
            reverse(details, args=[person.id]))

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(username=person.user.username,
                          password=form.cleaned_data['password'])
            if user is not None:
                person.user.username = form.cleaned_data['login']
                person.user.set_password(form.cleaned_data['new_password1'])
                person.user.save()
                messages.success(request, _("Credentials updated."))
                return redirect(person)
            else:
                messages.error(request, _("Wrong authentication"))

    form = ChangePasswordForm(initial={'login': person.user.username})

    return render(request, 'annuaire/credentials.html', {
        'form': form,
        'person': person,
        'is_myself': is_myself,
        }
    )


@access_required(groups=['ain7-secretariat'])
def send_new_credentials(request, user_id):
    """Send a link for reseting password"""

    person = get_object_or_404(Person, pk=user_id)

    person.password_ask(request=request)

    messages.success(request, _("New credentials have been sent"))

    return redirect(person)


@access_required(groups=['ain7-secretariat'])
def set_new_credentials(request, user_id):
    """Send a link for reseting password"""

    person = get_object_or_404(Person, pk=user_id)
    print person.user

    form = SetPasswordForm(data=request.POST or None, user=person.user)

    if request.method == 'POST' and form.is_valid():
        form.save()

        messages.success(request, _("New credentials have been set"))
        return redirect(person)

    return render(request, 'annuaire/edit_form.html', {
        'form': form,
        'person': person,
        'action_title': _("Modification of personal data for"),
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def edit(request, user_id=None):

    person = get_object_or_404(Person, pk=user_id)
    personprivate = get_object_or_404(PersonPrivate, person=person)

    return render(request, 'annuaire/edit.html', {
        'person': person,
        'personprivate': personprivate,
        'is_myself': int(request.user.id) == int(user_id),
        }
    )


@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def person_edit(request, user_id):

    person = get_object_or_404(Person, user=user_id)
    PersonForm = modelform_factory(
        Person, fields=(
            'last_name', 'first_name', 'maiden_name', 
            'birth_date', 'sex', 'nationality',
            )
    )
    form = PersonForm(request.POST or None, instance=person)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _('Modifications have been\
 successfully saved.'))

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html', {
        'form': form,
        'person': person,
        'action_title': _("Modification of personal data for"),
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@access_required(groups=['ain7-secretariat', 'ain7-ca'])
def personprivate_edit(request, user_id):

    person = get_object_or_404(Person, user=user_id)
    PersonPrivateForm = modelform_factory(Person, fields=('death_date', 'is_dead', 'notes'))
    form = PersonPrivateForm(request.POST or None, instance=person)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _('Modifications have been\
 successfully saved.'))

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html', {
        'form': form,
        'person': person,
        'action_title': _("Modification of personal data for"),
        'back': request.META.get('HTTP_REFERER', '/')
        }
    )


@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def ain7member_edit(request, user_id):

    person = get_object_or_404(Person, user=user_id)
    AIn7MemberForm = modelform_factory(
        Person, fields=(
            'marital_status','children_count', 'nick_name', 
            'avatar', 'year', 'track',
            )
    )

    form = AIn7MemberForm(
        request.POST or None,
        request.FILES or None,
        instance=person,
    )

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _('Modifications have been\
 successfully saved.'))

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html', {
        'form': form,
        'person': person,
        'action_title': _("Modification of personal data"),
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def promo_edit(request, user_id=None, promo_id=None):

    person = get_object_or_404(Person, id=user_id)
    ain7member = person.ain7member

    PromoForm = autocomplete_light.modelform_factory(
        AIn7Member, fields=('promos',),
    )
    form = PromoForm(request.POST or None, instance=ain7member)

    if request.method == 'POST' and form.is_valid():
        ain7member = form.save()
        messages.success(request, _('Promotion successfully added.'))

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html', {
        'form': form,
        'action_title': _(u'Adding a promotion for %s' % ain7member),
        },
    )


@confirmation_required(lambda user_id=None, promo_id=None:
    str(get_object_or_404(Promo, pk=promo_id)),
    'annuaire/base.html',
    _('Do you really want to remove the membership to the promotion'))
@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def promo_delete(request, user_id=None, promo_id=None):

    person = get_object_or_404(Person, id=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    promo = get_object_or_404(Promo, id=promo_id)
    ain7member.promos.remove(promo)
    ain7member.save()
    messages.success(request, "Membership to promotion %s\
 successfully removed.")
    return HttpResponseRedirect('/annuaire/%s/edit/#promos' % user_id)


@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def address_edit(request, user_id=None, address_id=None):

    person = get_object_or_404(Person, user=user_id)
    address = None
    if address_id:
        address = get_object_or_404(Address, id=address_id)
    title = _('Creation of an address for')

    AddressForm = modelform_factory(Address, exclude=('person', 'confidentiality', ))
    form = AddressForm(request.POST or None, instance=address)

    if request.method == 'POST' and form.is_valid():
        adr = form.save(commit=False)
        adr.person = person
        adr.save()

        messages.success(request, _('Address successfully saved'))

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html', {
        'form': form,
        'action_title': title,
        'person': person,
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@confirmation_required(lambda user_id=None, address_id=None:
    str(get_object_or_404(Address, pk=address_id)), 'annuaire/base.html',
    _('Do you really want to delete your address'))
@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def address_delete(request, user_id=None, address_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(Address, pk=address_id),
        '/annuaire/%s/edit/#address' % user_id,
        _('Address successfully deleted.'))


@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def phone_edit(request, user_id=None, phone_id=None):

    person = get_object_or_404(Person, user=user_id)
    phone = None
    if phone_id:
        phone = get_object_or_404(PhoneNumber, id=phone_id)
    title = _('Creation of a phone number for')

    PhoneNumberForm = modelform_factory(PhoneNumber, exclude=('person',))
    form = PhoneNumberForm(request.POST or None, instance=phone)

    if request.method == 'POST' and form.is_valid():
        phon = form.save(commit=False)
        phon.person = person
        phon.save()

        messages.success(request, _('Phone number successfully saved'))

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html', {
        'form': form,
        'action_title': title,
        'person': person,
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@confirmation_required(lambda user_id=None, phone_id=None:
    str(get_object_or_404(PhoneNumber, pk=phone_id)), 'annuaire/base.html',
    _('Do you really want to delete your phone number'))
@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def phone_delete(request, user_id=None, phone_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(PhoneNumber, pk=phone_id),
        '/annuaire/%s/edit/#phone' % user_id,
        _('Phone number successfully deleted.'))


@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def email_edit(request, user_id=None, email_id=None):

    person = get_object_or_404(Person, user=user_id)
    title = _('Creation of an email address for')

    email = None
    if email_id:
        email = get_object_or_404(Email, pk=email_id)

    EmailForm = modelform_factory(Email, exclude=('person',))
    form = EmailForm(request.POST or None, instance=email)

    if request.method == 'POST' and form.is_valid():
        mail = form.save(commit=False)
        mail.person = person
        mail.save()

        messages.success(request, _('Email successfully saved'))

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html', {
        'form': form,
        'action_title': title,
        'person': person,
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@confirmation_required(lambda user_id=None, email_id=None:
    str(get_object_or_404(Email, pk=email_id)), 'annuaire/base.html',
    _('Do you really want to delete your email address'))
@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def email_delete(request, user_id=None, email_id=None):

    return ain7_generic_delete(request, get_object_or_404(Email, pk=email_id),
                               '/annuaire/%s/edit/#email' % user_id,
                               _('Email address successfully deleted.'))


@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def im_edit(request, user_id=None, im_id=None):

    person = get_object_or_404(Person, user=user_id)
    ime = None
    if im_id:
        ime = get_object_or_404(InstantMessaging, pk=im_id)

    title = _('Creation of an instant messaging account for')
    InstantMessagingForm = modelform_factory(InstantMessaging, exclude=('person',))
    form = InstantMessagingForm(request.POST or None, instance=ime)

    if request.method == 'POST' and form.is_valid():
        inm = form.save(commit=False)
        inm.person = person
        inm.save()

        messages.success(request, _('Instant messaging successfully saved'))

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html', {
        'form': form,
        'action_title': title,
        'person': person,
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@confirmation_required(lambda user_id=None, im_id=None:
    str(get_object_or_404(InstantMessaging, pk=im_id)), 'annuaire/base.html',
    _('Do you really want to delete your instant messaging account'))
@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def im_delete(request, user_id=None, im_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(InstantMessaging, pk=im_id),
        '/annuaire/%s/edit/#im' % user_id,
        _('Instant messaging account successfully deleted.'))


@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def website_edit(request, user_id=None, website_id=None):

    person = get_object_or_404(Person, user=user_id)
    website = None
    title = _('Creation of a website for')

    website = None
    if website_id:
        website = get_object_or_404(WebSite, pk=website_id)

    WebSiteForm = modelform_factory(WebSite, exclude=('person',))
    form = WebSiteForm(request.POST or None, instance=website)

    if request.method == 'POST' and form.is_valid():
        web = form.save(commit=False)
        web.person = person
        web.save()

        messages.success(request, _('website successfully saved'))

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html', {
        'form': form,
        'action_title': title,
        'person': person,
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@confirmation_required(lambda user_id=None, website_id=None:
    str(get_object_or_404(WebSite, pk=website_id)), 'annuaire/base.html',
    _('Do you really want to delete your website'))
@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def website_delete(request, user_id=None, website_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(WebSite, pk=website_id),
        '/annuaire/%s/edit/#website' % user_id,
        _('Website successfully deleted.'))


# Vie associative a l'n7
@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def club_membership_edit(request, user_id=None, club_membership_id=None):

    person = get_object_or_404(Person, user=user_id)
    title = _('Creation of a club membership for')

    club_membership = None
    if club_membership_id:
        club_membership = get_object_or_404(ClubMembership,
            pk=club_membership_id)

    ClubMembershipForm = modelform_factory(ClubMembership, exclude=('person',))
    form = ClubMembershipForm(request.POST or None, instance=club_membership)

    if request.method == 'POST' and form.is_valid():
        membership = form.save(commit=False)
        membership.member = person
        membership.save()

        messages.success(request, _('Club membership successfully saved'))

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html', {
        'form': form,
        'action_title': title,
        'person': person,
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@confirmation_required(lambda user_id=None, club_membership_id=None:
    str(get_object_or_404(ClubMembership, pk=club_membership_id)),
    'annuaire/base.html',
    _('Do you really want to delete your club membership'))
@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def club_membership_delete(request, user_id=None, club_membership_id=None):

    return ain7_generic_delete(
        request,
        get_object_or_404(ClubMembership, pk=club_membership_id),
        '/annuaire/%s/edit/#assoc' % user_id,
        _('Club membership successfully deleted.'))


@access_required(groups=['ain7-secretariat', 'ain7-ca'])
def add(request, user_id=None):
    """ add a new person"""

    form = NewMemberForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        new_person = form.save()
        messages.success(request, _("New user successfully created"))

        return redirect(new_person)

    return render(request, 'annuaire/edit_form.html', {
        'action_title': _('Register new user'),
        'back': request.META.get('HTTP_REFERER', '/'),
        'form': form,
        }
    )


@access_required(groups=['ain7-secretariat', 'ain7-membre'])
def vcard(request, user_id):

    person = get_object_or_404(Person, pk=user_id)

    mail = None
    mail_list = Email.objects.filter(
        person=person, preferred_email=True, confidential=False
    )
    if mail_list:
        mail = mail_list[0].email

    vcard = vobject.vCard()
    vcard.add('n').value = vobject.vcard.Name(family=person.last_name,
        given=person.first_name)
    vcard.add('fn').value = person.first_name + ' ' + person.last_name
    if mail:
        email = vcard.add('email')
        email.value = mail
        email.type_param = ['INTERNET', 'PREF']
    for address in Address.objects.filter(person=person, confidential=False):
        street = ''
        if address.line1:
            street = street + address.line1
        if address.line2:
            street = street + address.line2
        adr = vcard.add('adr')
        adr.value = vobject.vcard.Address(street=street, city=address.city,
            region='', code=address.zip_code, country=address.country.name,
            box='', extended='')
        adr.type_param = address.type.type
    for phone in PhoneNumber.objects.filter(person=person, confidential=False):
        tel = vcard.add('tel')
        tel.value = phone.number
        tel.type_param = ['HOME', 'FAX', 'CELL'][phone.type-1]

    vcardstream = vcard.serialize()

    response = HttpResponse(vcardstream, content_type='text/x-vcard')
    response['Filename'] = person.user.username + '.vcf'  # IE needs this
    response['Content-Disposition'] = ('attachment; filename=' +
        person.user.username + '.vcf')

    return response


@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def position_edit(request, user_id=None, position_id=None):
    """position edit"""

    person = get_object_or_404(Person, user=user_id)
    # ain7member = get_object_or_404(AIn7Member, person=person)

    position = None
    if position_id:
        position = get_object_or_404(Position, pk=position_id)

    PositionForm = autocomplete_light.modelform_factory(
        Position,
        exclude=('ain7member',),
    )
    form = PositionForm(request.POST or None, instance=position)

    if request.method == 'POST' and form.is_valid():
        pos = form.save(commit=False)
        pos.ain7member = person
        pos.save()
        messages.success(
            request,
            _('Modifications have been successfully saved.')
        )
        print('je suis la')

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html', {
        'form': form,
        'action_title': _("Position edit"),
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@confirmation_required(lambda user_id=None, position_id=None:
    str(get_object_or_404(Position, pk=position_id)), 'emploi/base.html',
    _('Do you really want to delete your position'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def position_delete(request, user_id=None, position_id=None):
    """position delete"""

    return ain7_generic_delete(
        request,
        get_object_or_404(Position, pk=position_id),
        reverse(edit, args=[user_id]) + '#prof_exp',
        _('Position successfully deleted.')
    )


@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def education_edit(request, user_id=None, education_id=None):
    """education edit"""

    person = get_object_or_404(Person, user=user_id)
    # ain7member = get_object_or_404(AIn7Member, person=person)

    educationitem = None
    if education_id:
        educationitem = get_object_or_404(EducationItem, pk=education_id)

    EducationItemForm = modelform_factory(
        EducationItem,
        exclude=('ain7member',)
    )
    form = EducationItemForm(request.POST or None, instance=educationitem)

    if request.method == 'POST' and form.is_valid():
        editem = form.save(commit=False)
        editem.ain7member = person
        editem.save()
        messages.success(
            request,
            _('Modifications have been successfully saved.')
        )

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html', {
        'form': form,
        'action_title': _("Position edit"),
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@confirmation_required(lambda user_id=None, education_id=None:
    str(get_object_or_404(EducationItem, pk=education_id)), 'emploi/base.html',
    _('Do you really want to delete your education item'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def education_delete(request, user_id=None, education_id=None):
    """education delete"""

    return ain7_generic_delete(
        request,
        get_object_or_404(EducationItem, pk=education_id),
        reverse(edit, args=[user_id]) + '#education',
        _('Education informations deleted successfully.')
    )


@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def leisure_edit(request, user_id=None, leisure_id=None):
    """leisure edit"""

    person = get_object_or_404(Person, user=user_id)
    # ain7member = get_object_or_404(AIn7Member, person=person)

    leisureitem = None
    if leisure_id:
        leisureitem = get_object_or_404(LeisureItem, pk=leisure_id)

    LeisureItemForm = modelform_factory(LeisureItem, exclude=('ain7member',))
    form = LeisureItemForm(request.POST or None, instance=leisureitem)

    if request.method == 'POST' and form.is_valid():
        leitem = form.save(commit=False)
        leitem.ain7member = person
        leitem.save()
        messages.success(
            request,
            _('Modifications have been successfully saved.')
        )

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html', {
        'form': form,
        'action_title': _("Position edit"),
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@confirmation_required(lambda user_id=None, leisure_id=None:
    str(get_object_or_404(LeisureItem, pk=leisure_id)), 'emploi/base.html',
    _('Do you really want to delete your leisure item'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def leisure_delete(request, user_id=None, leisure_id=None):
    """leisure delete"""

    return ain7_generic_delete(
        request,
        get_object_or_404(LeisureItem, pk=leisure_id),
        reverse(edit, args=[user_id]) + '#leisure',
        _('Leisure informations successfully deleted.')
    )


@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def publication_edit(request, user_id=None, publication_id=None):
    """publication edit"""

    person = get_object_or_404(Person, user=user_id)
    # ain7member = get_object_or_404(AIn7Member, person=person)

    publi = None
    if publication_id:
        publi = get_object_or_404(PublicationItem, pk=publication_id)

    PublicationItemForm = modelform_factory(
        PublicationItem,
        exclude=('ain7member',)
    )
    form = PublicationItemForm(request.POST or None, instance=publi)

    if request.method == 'POST' and form.is_valid():
        publication = form.save(commit=False)
        publication.ain7member = person
        publication.save()
        messages.success(
            request,
            _('Modifications have been successfully saved.')
        )

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html', {
        'form': form,
        'action_title': _("Position edit"),
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@confirmation_required(lambda user_id=None, publication_id=None:
    str(get_object_or_404(PublicationItem, pk=publication_id)),
    'emploi/base.html',
    _('Do you really want to delete your publication'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def publication_delete(request, user_id=None, publication_id=None):
    """publication delete"""

    return ain7_generic_delete(
        request,
        get_object_or_404(PublicationItem, pk=publication_id),
        reverse(edit, args=[user_id]) + '#publications',
        _('Publication informations deleted successfully.')
    )


def welcome(request):

    PersonForm = modelform_factory(Person, fields=('first_name', 'last_name',))
    MemberForm = modelform_factory(AIn7Member, fields=('promos',))
    EmailForm = modelform_factory(Email, fields=('email',))

    person_form = PersonForm(request.POST or None)
    member_form = MemberForm(request.POST or None)
    member_form.fields['promos'].queryset = Promo.objects.filter(year__year=2019)
    email_form = EmailForm(request.POST or None)

    if (
            request.method == 'POST' and
            person_form.is_valid() and
            member_form.is_valid() and
            email_form.is_valid()
    ):

        username = generate_login(
            person_form.cleaned_data['first_name'],
            person_form.cleaned_data['last_name']
        )

        user = User.objects.create_user(
            email=email_form.cleaned_data['email'],
            first_name=person_form.cleaned_data['first_name'],
            last_name=person_form.cleaned_data['last_name'],
            username=username,
        )
        user.save()
        person = person_form.save(commit=False)
        person.user = user
        person.validated = False
        person.save()
        pp = PersonPrivate()
        pp.person = person
        pp.save()
        member = member_form.save(commit=False)
        member.person = person
        member.save()
        member_form.save_m2m()
        email = email_form.save(commit=False)
        email.person = person
        email.preferred_email = True
        email.save()

        person.send_mail(_(u"Bienvenue à l'n7 et à l'AIn7"),
_(u"""%(firstname)s,

Nous avons bien enregistré ton inscription dans l'annuaire des anciens
de l'ENSEEIHT. Si tu as adhéré, nous te confirmerons ton adhésion dès que
le paiement aura été validé. Si tu n'as pas adhéré, tu pourras adhérer
directement depuis le site à tout moment.

Pour te connecter au site, il faut te rendre à l'adresse et y saisir ton
adresse email (%(email)s):
https://ain7.com/lostpassword/

N'hésite à pas nous contacter pour tout aide sur le site ou au sujet de l'AIn7.
Le secrétariat est derrière l'accueil et l'n7 et est ouvert tous les jours.

L'équipe de l'AIn7

""") % { 'firstname': person.first_name, 'email': email.email })

        return redirect('subscription-welcome', person.pk)

    return render(request, 'annuaire/welcome.html', {
        'email_form': email_form,
        'member_form': member_form,
        'person_form': person_form,
        }
    )
