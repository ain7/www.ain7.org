# -*- coding: utf-8
"""
 ain7/annuaire/views.py
"""
#
#   Copyright © 2007-2015 AIn7 Devel Team
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
import datetime

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404, redirect, render

from ain7.annuaire.models import PersonPrivate, UserActivity, Promo, \
                                 PhoneNumber, InstantMessaging, Email, IRC, \
                                 WebSite, ClubMembership, Person, \
                                 AIn7Member, Address
from ain7.emploi.models import Position
from ain7.annuaire.forms import SearchPersonForm, ChangePasswordForm, \
                                PromoForm, NewMemberForm
from ain7.adhesions.forms import Subscription
from ain7.decorators import access_required, confirmation_required
from ain7.utils import ain7_generic_delete


@login_required
def home(request, user_name):
    user = get_object_or_404(User, username=user_name)
    user_id = Person.objects.get(user=user).id
    return details(request, user_id)

@login_required
def details(request, user_id):

    is_subscriber = False
    ain7member = None
    last_activity = None
    is_myself = int(request.user.id) == int(user_id)

    person = get_object_or_404(Person, pk=user_id)
    personprivate = get_object_or_404(PersonPrivate, person=person)

    if AIn7Member.objects.filter(person=person).count() > 0:
        ain7member = get_object_or_404(AIn7Member, person=person)
        is_subscriber = Subscription.objects.filter(member=ain7member).\
            filter(validated=True).exclude(start_year__gt=datetime.date.\
            today().year).exclude(end_year__lt=datetime.date.today().year)

    if UserActivity.objects.filter(person=person):
        last_activity = UserActivity.objects.filter(person=person).latest('id')

    return render(request, 'annuaire/details.html',
        {'person': person, 'personprivate': personprivate, 
         'is_subscriber': is_subscriber,
         'ain7member': ain7member, 'is_myself': is_myself, 
         'last_activity': last_activity})

@login_required
def search(request):

    form = SearchPersonForm()
    dosearch = False
    ain7members = False

    if request.GET.has_key('first_name') or request.GET.has_key('last_name') \
       or request.GET.has_key('organization') or \
       request.GET.has_key('promoyear') or request.GET.has_key('track'):
        form = SearchPersonForm(request.GET)
        if form.is_valid():

            dosearch = True

            # perform search
            #criteria = form.criteria()
            #ain7members = form.search(criteria)
            ain7members = AIn7Member.objects.all().order_by('person__last_name','person__first_name')

            if len(ain7members) == 1:
                messages.info(request, _('Only one result matched your criteria.'))
                return redirect(ain7members[0].person)

    return render(request, 'annuaire/search.html',
        {
            'form': form,
            'ain7members': ain7members,
            'request': request,
            'dosearch': dosearch,
        }
    )

@login_required
def change_credentials(request, user_id):
    is_myself = int(request.user.id) == int(user_id)

    if not is_myself:
        return HttpResponseRedirect(\
            reverse('ain7.annuaire.views.details', args=[person.id]))

    person = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

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
                return HttpResponseRedirect(\
                    reverse('ain7.annuaire.views.details', args=[person.id]))
            else:
                messages.error(request, _("Wrong authentication"))

    form = ChangePasswordForm(initial={'login': person.user.username})

    return render(request, 'annuaire/credentials.html',
        {
            'form': form,
            'person': person,
            'ain7member': ain7member,
            'is_myself': is_myself,
        }
    )

@access_required(groups=['ain7-secretariat'])
def send_new_credentials(request, user_id):
    """Send a link for reseting password"""

    person = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    person.password_ask(request=request)

    messages.success(request, _("New credentials have been sent"))

    return HttpResponseRedirect(reverse('ain7.annuaire.views.details', 
        args=[person.id]))

@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def edit(request, user_id=None):

    ain7member = None

    person = get_object_or_404(Person, pk=user_id)
    personprivate = get_object_or_404(PersonPrivate, person=person)

    if AIn7Member.objects.filter(person=person).count() > 0:
        ain7member = get_object_or_404(AIn7Member, person=person)

    return render(request, 'annuaire/edit.html',
        {
            'person': person,
            'ain7member': ain7member, 
            'personprivate': personprivate,
            'is_myself': int(request.user.id) == int(user_id),
        }
    )

@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def person_edit(request, user_id):

    person = get_object_or_404(Person, user=user_id)
    PersonForm = modelform_factory(Person, exclude=('old_id', 'user',))
    form = PersonForm(request.POST or None, instance=person)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _('Modifications have been\
 successfully saved.'))

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html',
        {
            'form': form,
            'action_title': _("Modification of personal data for"),
            'back': request.META.get('HTTP_REFERER', '/'),
        }
    )

@access_required(groups=['ain7-secretariat','ain7-ca'])
def personprivate_edit(request, user_id):

    personprivate = get_object_or_404(PersonPrivate, person=user_id)
    PersonPrivateForm = modelform_factory(PersonPrivate, exclude=('person',))
    form = PersonPrivateForm(request.POST or None, instance=personprivate)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _('Modifications have been\
 successfully saved.'))

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html',
        {
            'form': form,
            'action_title': _("Modification of personal data for"),
            'back': request.META.get('HTTP_REFERER', '/')
        }
    )

@access_required(groups=['ain7-secretariat','ain7-ca'], allow_myself=True)
def ain7member_edit(request, user_id):

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    AIn7MemberForm = modelform_factory(AIn7Member, exclude=('person',))

    form = AIn7MemberForm(request.POST, request.FILES, instance=ain7member)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _('Modifications have been\
 successfully saved.'))

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html',
        {
             'form': form,
             'action_title': _("Modification of personal data for"),
             'back': request.META.get('HTTP_REFERER', '/'),
        }
    )

# Promos
@access_required(groups=['ain7-secretariat','ain7-ca'], allow_myself=True)
def promo_edit(request, user_id=None, promo_id=None):

    person = get_object_or_404(Person, id=user_id)
    ain7member = person.ain7member

    form = PromoForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        promo = form.search()
        ain7member.promos.add(promo)
        messages.success(request, _('Promotion successfully added.'))

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html',
        {
            'form': form,
            'action_title': _(u'Adding a promotion for %s' % ain7member),
        },
    )

@confirmation_required(lambda user_id=None, promo_id=None :
     str(get_object_or_404(Promo, pk=promo_id)), 
     'annuaire/base.html', 
     _('Do you really want to remove the membership to the promotion'))
@access_required(groups=['ain7-secretariat','ain7-ca'], allow_myself=True)
def promo_delete(request, user_id=None, promo_id=None):

    person = get_object_or_404(Person, id=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    promo = get_object_or_404(Promo, id=promo_id)
    ain7member.promos.remove(promo)
    ain7member.save()
    messages.success(request, "Membership to promotion %s\
 successfully removed.")
    return HttpResponseRedirect('/annuaire/%s/edit/#promos' % user_id)

# Adresses
@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def address_edit(request, user_id=None, address_id=None):

    person = get_object_or_404(Person, user=user_id)
    address = None
    if address_id:
        address = get_object_or_404(Address, id=address_id)
    title = _('Creation of an address for')

    AddressForm = modelform_factory(Address, exclude=('person',))
    form = AddressForm(request.POST or None, instance=address)

    if request.method == 'POST' and form.is_valid():
        adr = form.save(commit=False)
        adr.person = person
        adr.save()

        messages.success(request, _('Address successfully saved'))

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html',
        {
            'form': form,
            'action_title': title,
            'person': person,
            'back': request.META.get('HTTP_REFERER', '/'),
        }
    )

@confirmation_required(lambda user_id=None, address_id=None :
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

    return render(request, 'annuaire/edit_form.html',
        {
             'form': form,
             'action_title': title,
             'person': person,
             'back': request.META.get('HTTP_REFERER', '/'),
        }
    )

@confirmation_required(lambda user_id=None, phone_id=None :
    str(get_object_or_404(PhoneNumber, pk=phone_id)), 'annuaire/base.html', 
    _('Do you really want to delete your phone number'))
@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def phone_delete(request, user_id=None, phone_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(PhoneNumber, pk=phone_id),
        '/annuaire/%s/edit/#phone' % user_id,
        _('Phone number successfully deleted.'))

# Adresses de courriel
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

    return render(request, 'annuaire/edit_form.html',
        {
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

# Comptes de messagerie instantanee
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

    return render(request, 'annuaire/edit_form.html',
        {
             'form': form, 
             'action_title': title,
             'person': person,
             'back': request.META.get('HTTP_REFERER', '/'),
        }
    )

@confirmation_required(lambda user_id=None, im_id=None :
    str(get_object_or_404(InstantMessaging, pk=im_id)), 'annuaire/base.html',
    _('Do you really want to delete your instant messaging account'))
@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def im_delete(request, user_id=None, im_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(InstantMessaging, pk=im_id),
        '/annuaire/%s/edit/#im' % user_id,
        _('Instant messaging account successfully deleted.'))

# Comptes IRC
@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def irc_edit(request, user_id=None, irc_id=None):

    person = get_object_or_404(Person, user=user_id)
    irc = None
    title = _('Creation of an IRC account for')

    irc = None
    if irc_id:
        irc = get_object_or_404(IRC, pk=irc_id)

    IRCForm = modelform_factory(IRC, exclude=('person',))
    form = IRCForm(request.POST or None, instance=irc)

    if request.method == 'POST' and form.is_valid():
        this_irc = form.save(commit=False)
        this_irc.person = person
        this_irc.save()

        messages.success(request, _('irc contact successfully saved'))

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html',
        {
            'form': form,
            'action_title': title,
            'person': person,
            'back': request.META.get('HTTP_REFERER', '/'),
        }
    )

@confirmation_required(lambda user_id=None, irc_id=None:
    str(get_object_or_404(IRC, pk=irc_id)), 'annuaire/base.html',
    _('Do you really want to delete your IRC account'))
@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def irc_delete(request, user_id=None, irc_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(IRC, pk=irc_id),
        '/annuaire/%s/edit/#irc' % user_id,
        _('IRC account successfully deleted.'))

# Sites Internet
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

    return render(request, 'annuaire/edit_form.html',
        {
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
    ain7member = get_object_or_404(AIn7Member, person=person)
    title = _('Creation of a club membership for')
 
    club_membership = None
    if club_membership_id:
        club_membership = get_object_or_404(ClubMembership,
            pk=club_membership_id)

    ClubMembershipForm = modelform_factory(ClubMembership, exclude=('person',))
    form = ClubMembershipForm(request.POST or None, instance=club_membership)

    if request.method == 'POST' and form.is_valid():
        membership = form.save(commit=False)
        membership.member = ain7member
        membership.save()

        messages.success(request, _('Club membership successfully saved'))

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html',
        {
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

    return ain7_generic_delete(request,
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

        return redirect('annuaire-edit', user_id)

    return render(request, 'annuaire/edit_form.html',
        {
            'action_title': _('Register new user'),
            'back': request.META.get('HTTP_REFERER', '/'),
            'form': form,
        }
    )

@access_required(groups=['ain7-secretariat', 'ain7-member'])
def vcard(request, user_id):

    person = get_object_or_404(Person, pk=user_id)

    mail = None
    mail_list = Email.objects.filter(person=person, preferred_email=True, \
        confidentiality__in=[0,1])
    if mail_list:
        mail = mail_list[0].email

    vcard = vobject.vCard()
    vcard.add('n').value = vobject.vcard.Name( family=person.last_name, \
        given=person.first_name )
    vcard.add('fn').value = person.first_name+' '+person.last_name
    if mail:
        email = vcard.add('email')
        email.value = mail
        email.type_param = ['INTERNET', 'PREF']
    for address in  Address.objects.filter(person=person, \
        confidentiality__in=[0,1]):
        street = ''
        if address.line1:
            street = street + address.line1
        if address.line2:
            street = street + address.line2
        adr = vcard.add('adr')
        adr.value = vobject.vcard.Address(street=street, city=address.city, \
            region='', code=address.zip_code, country=address.country.name, \
            box='', extended='')
        adr.type_param = address.type.type
    for phone in PhoneNumber.objects.filter(person=person, \
        confidentiality__in=[0,1]):
        tel = vcard.add('tel')
        tel.value = phone.number
        tel.type_param = ['HOME', 'FAX', 'CELL'][phone.type-1]

    vcardstream = vcard.serialize()

    response = HttpResponse(vcardstream, mimetype='text/x-vcard')
    response['Filename'] = person.user.username+'.vcf'  # IE needs this
    response['Content-Disposition'] = 'attachment; filename=' + \
        person.user.username+'.vcf'

    return response

