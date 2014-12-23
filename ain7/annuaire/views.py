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
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404, render

from ain7.annuaire.models import PersonPrivate, UserActivity, Promo, \
                                 PhoneNumber, InstantMessaging, Email, IRC, \
                                 WebSite, ClubMembership, Person, \
                                 AIn7Member, Address
from ain7.emploi.models import Position
from ain7.annuaire.forms import SearchPersonForm, ChangePasswordForm, \
                                PersonForm,PersonPrivateForm, \
                                AIn7MemberForm, PromoForm, \
                                AddressForm, PhoneNumberForm, EmailForm, \
                                InstantMessagingForm, IRCForm, WebSiteForm, \
                                ClubMembershipForm, NewMemberForm
from ain7.adhesions.forms import Subscription
from ain7.decorators import access_required, confirmation_required
from ain7.search_engine.models import SearchEngine, SearchFilter
from ain7.search_engine.forms import SearchFilterForm
from ain7.search_engine.views import se_filter_swap_op, \
                                     se_criterion_field_edit, \
                                     se_criterion_add, se_criterion_delete, \
                                     se_criterion_filter_edit, se_export_csv
from ain7.utils import ain7_generic_delete


def annuaire_search_engine():
    return get_object_or_404(SearchEngine, name="annuaire")

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
    nb_results_by_page = 25
    paginator = Paginator(AIn7Member.objects.none(), nb_results_by_page)
    page = 1

    if request.GET.has_key('first_name') or request.GET.has_key('last_name') \
       or request.GET.has_key('organization') or \
       request.GET.has_key('promoyear') or request.GET.has_key('track'):
        form = SearchPersonForm(request.GET)
        if form.is_valid():

            dosearch = True

            # perform search
            criteria = form.criteria()
            ain7members = form.search(criteria)

            if len(ain7members) == 1:
                messages.info(request, _('Only one result matched your criteria.'))
                return HttpResponseRedirect('/annuaire/%s/' % \
                    (ain7members[0].person.id))

            # put the criteria in session: they must be accessed when
            # performing a CSV export, sending a mail...
            request.session['filter'] = criteria
            paginator = Paginator(ain7members, nb_results_by_page)

            try:
                page = int(request.GET.get('page', '1'))
                ain7members = paginator.page(page).object_list
            except InvalidPage:
                raise Http404

    return render(request, 'annuaire/search.html',
        {'form': form, 'ain7members': ain7members, 'request': request,
         'userFilters': annuaire_search_engine().registered_filters(
                            request.user.person),
         'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page, 'pages': paginator.num_pages,
         'next_page': page + 1, 'previous_page': page - 1,
         'first_result': (page-1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits' : paginator.count, 'dosearch': dosearch})

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
        {'form': form, 'person': person, 'ain7member': ain7member,
         'is_myself': is_myself})

@access_required(groups=['ain7-secretariat'])
def send_new_credentials(request, user_id):
    """Send a link for reseting password"""

    person = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    person.password_ask(request=request)

    messages.success(request, _("New credentials have been sent"))
    return HttpResponseRedirect(reverse('ain7.annuaire.views.details', 
        args=[person.id]))

@access_required(groups=['ain7-membre', 'ain7-secretariat'])
def advanced_search(request):

    search_filter = annuaire_search_engine().unregistered_filters(\
        request.user.person)
    if search_filter:
        return render(request, 'annuaire/adv_search.html',
            dict_for_filter(request, search_filter.id))
    else:
        return render(request, 'annuaire/adv_search.html',
            dict_for_filter(request, None))
    

@access_required(groups=['ain7-membre', 'ain7-secretariat'])
def filter_details(request, filter_id):

    return render(request, 'annuaire/adv_search.html',
        dict_for_filter(request, filter_id))


@access_required(groups=['ain7-membre','ain7-secretariat'])
def dict_for_filter(request, filter_id):

    ain7members = False
    dosearch = False
    person = request.user.person
    nb_results_by_page = 25
    paginator = Paginator(AIn7Member.objects.none(), nb_results_by_page)
    page = 1
    search_filter = None
    if filter_id:
        search_filter = get_object_or_404(SearchFilter, pk=filter_id)
        

    if request.method == 'POST' or request.GET.has_key('page'):

        ain7members = AIn7Member.objects.all()
        if filter_id:
            ain7members = search_filter.search()
        dosearch = True
        paginator = Paginator(ain7members, nb_results_by_page)

        try:
            page = int(request.GET.get('page', '1'))
            ain7members = paginator.page(page).object_list
        except InvalidPage:
            raise Http404

    return {'ain7members': ain7members,
         'filtr': search_filter,
         'userFilters': annuaire_search_engine().registered_filters(person),
         'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page,
         'next_page': page + 1, 'previous_page': page - 1,
         'pages': paginator.num_pages,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits' : paginator.count, 'dosearch': dosearch}


@access_required(groups=['ain7-membre','ain7-secretariat'])
def filter_register(request):

    search_filter = annuaire_search_engine().unregistered_filters(\
        request.user.person)
    if not search_filter:
        return HttpResponseRedirect('/annuaire/advanced_search/')

    form = SearchFilterForm()

    if request.method != 'POST':
        return render(request,
            'annuaire/edit_form.html',
            {'form': form, 'back': request.META.get('HTTP_REFERER', '/'),
             'action_title': _("Enter parameters of your filter")})
    else:
        form = SearchFilterForm(request.POST)
        if form.is_valid():
            fName = form.cleaned_data['name']
            # First we check that the user does not have
            # a filter with the same name
            same_name = annuaire_search_engine().\
                registered_filters(request.user.person).\
                filter(name=fName).count()
            if same_name > 0:
                messages.error(request, _("One of your filters\
 already has this name."))
                return HttpResponseRedirect('/annuaire/advanced_search/')

            # Set the registered flag to True
            search_filter.registered = True
            search_filter.name = fName
            search_filter.save()

            # Redirect to filter page
            messages.success(request, _("Modifications have been successfully saved."))
            return HttpResponseRedirect(
                '/annuaire/advanced_search/filter/%s/' % search_filter.id)
        else:
            messages.error(request, _("Something was wrong in\
 the form you filled. No modification done."))
        return HttpResponseRedirect('/annuaire/advanced_search/')


@access_required(groups=['ain7-membre','ain7-secretariat'])
def filter_edit(request, filter_id):

    filtr = get_object_or_404(SearchFilter, pk=filter_id)
    form = SearchFilterForm(instance=filtr)

    if request.method == 'POST':
        form = SearchFilterForm(request.POST, instance=filtr)
        if form.is_valid():
            form.cleaned_data['user'] = filtr.user
            form.cleaned_data['operator'] = filtr.operator
            form.save()
            messages.success(request, _("Modifications have been\
 successfully saved."))
        else:
            messages.error(request, _("Something was wrong in\
 the form you filled. No modification done."))
        return HttpResponseRedirect(
            '/annuaire/advanced_search/filter/%s/' % filter_id)
    return render(
        request, 'annuaire/edit_form.html',
        {'form': form, 'action_title': _("Modification of the filter")})


@login_required
def remove_criteria(request, filtr):
    for crit in filtr.criteriaField.all():  crit.delete()
    for crit in filtr.criteriaFilter.all(): crit.delete()
    # TODO non recursivite + supprimer filtres sans criteres
    return

@access_required(groups=['ain7-membre','ain7-secretariat'])
def filter_reset(request, filter_id):

    filtr = get_object_or_404(SearchFilter, pk=filter_id)
    remove_criteria(request, filtr)
    if filtr.registered:
        return HttpResponseRedirect(
            '/annuaire/advanced_search/filter/%s/' % filter_id)
    else:
        return HttpResponseRedirect('/annuaire/advanced_search/')

@access_required(groups=['ain7-membre','ain7-secretariat'])
def filter_delete(request, filter_id):

    filtr = get_object_or_404(SearchFilter, pk=filter_id)
    try:
        # remove criteria linked to this filter from database
        remove_criteria(request, filtr)
        # now remove the filter
        filtr.delete()
        messages.error(request, _("Your filter has been successfully deleted."))
    except KeyError:
        messages.error(request, 
                _("Something went wrong. The filter has not been deleted."))
    return HttpResponseRedirect('/annuaire/advanced_search/')

@access_required(groups=['ain7-membre','ain7-secretariat'])
def filter_new(request):

    search_filter = annuaire_search_engine().unregistered_filters(\
        request.user.person)
    if not search_filter:
        return HttpResponseRedirect('/annuaire/advanced_search/')
    remove_criteria(request, search_filter)
    if search_filter.registered:
        return HttpResponseRedirect(
            '/annuaire/advanced_search/filter/%s/' % search_filter.id)
    else:
        return HttpResponseRedirect('/annuaire/advanced_search/')

@login_required
def filter_swap_op(request, filter_id=None):
    return se_filter_swap_op(request, filter_id,
                            reverse(filter_details, args =[ filter_id ]),
                            reverse(advanced_search))

@login_required
def criterion_add(request, filter_id=None, criterion_type=None):
    redirect = reverse(advanced_search)
    if filter_id: redirect = reverse(filter_details, args=[ filter_id ])
    return se_criterion_add(request, annuaire_search_engine(),
        filter_id, criterion_type, criterionField_edit,
        redirect, 'annuaire/criterion_add.html')

@login_required
def criterionField_edit(request, filter_id=None, criterion_id=None):
    return se_criterion_field_edit(request, annuaire_search_engine(),
        filter_id, criterion_id, reverse(filter_details, args=[filter_id]),
        reverse(advanced_search), 'annuaire/criterion_edit.html')

@login_required
def criterionFilter_edit(request, filter_id=None, criterion_id=None):
    return se_criterion_filter_edit(request, annuaire_search_engine(),
        filter_id, criterion_id, reverse(filter_details, args=[filter_id]),
        'annuaire/criterionFilter_edit.html')

@login_required
def criterion_delete(request, filtr_id=None, crit_id=None, crit_type=None):
    return se_criterion_delete(request, filtr_id, crit_id, crit_type,
        reverse(filter_details, args=[filtr_id]), reverse(advanced_search))

@access_required(groups=['ain7-secretariat','ain7-ca'])
def export_csv(request):

    if not request.session.has_key('filter'):
        messages.info(request, _("You have to make a search\
 before using csv export."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    criteria = request.session['filter']
    ain7members = AIn7Member.objects.filter(criteria).distinct()

    return se_export_csv(request, ain7members, annuaire_search_engine(),
        'annuaire/edit_form.html')

@access_required(groups=['ain7-secretariat', 'ain7-ca'])
def adv_export_csv(request, filter_id=None):

    se = annuaire_search_engine()
    if not filter_id and not se.unregistered_filters(request.user.person):
        messages.info(request, 
            _("You have to make a search before using csv export."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    if filter_id:
        search_filter = get_object_or_404(SearchFilter, id=filter_id)
    else:
        search_filter = se.unregistered_filters(request.user.person)
    return se_export_csv(request, search_filter.search(), se, 
        'annuaire/edit_form.html')

@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def edit(request, user_id=None):

    ain7member = None

    person = get_object_or_404(Person, pk=user_id)
    personprivate = get_object_or_404(PersonPrivate, person=person)

    if AIn7Member.objects.filter(person=person).count() > 0:
        ain7member = get_object_or_404(AIn7Member, person=person)

    return render(request, 'annuaire/edit.html',
        {'person': person, 'ain7member': ain7member, 
         'personprivate': personprivate,
         'is_myself': int(request.user.id) == int(user_id)})

@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def person_edit(request, user_id):

    person = Person.objects.get(user=user_id)
    form = PersonForm(instance=person)

    if request.method == 'POST':
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            form.save()
            messages.success(request, _('Modifications have been\
 successfully saved.'))

        return HttpResponseRedirect(
            '/annuaire/%s/edit/' % user_id)

    return render(
        request, 'annuaire/edit_form.html',
        {'form': form, 'action_title': _("Modification of personal data for"),
         'back': request.META.get('HTTP_REFERER', '/')})

@access_required(groups=['ain7-secretariat','ain7-ca'])
def personprivate_edit(request, user_id):

    personprivate = PersonPrivate.objects.get(person=user_id)
    form = PersonPrivateForm(instance=personprivate)

    if request.method == 'POST':
        form = PersonPrivateForm(request.POST, instance=personprivate)
        if form.is_valid():
            form.save()
            messages.sucess(request, _('Modifications have been\
 successfully saved.'))

        return HttpResponseRedirect(
            '/annuaire/%s/edit/' % user_id)

    return render(
        request, 'annuaire/edit_form.html',
        {'form': form, 'action_title': _("Modification of personal data for"),
         'back': request.META.get('HTTP_REFERER', '/')})

@access_required(groups=['ain7-secretariat','ain7-ca'], allow_myself=True)
def ain7member_edit(request, user_id):

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    form = AIn7MemberForm(instance=ain7member)

    if request.method == 'POST':
        form = AIn7MemberForm(request.POST, request.FILES, instance=ain7member)
        if form.is_valid():
            if ain7member.avatar and form.cleaned_data['avatar']:
                ain7member.avatar.delete()
            form.save()
            messages.success(request, _('Modifications have been\
 successfully saved.'))

        return HttpResponseRedirect(
            '/annuaire/%s/edit/' % user_id)

    return render(
        request, 'annuaire/edit_form.html',
        {'form': form, 'action_title': _("Modification of personal data for"),
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda user_id=None, object_id=None : '',
     'annuaire/base.html', _('Do you really want to delete your avatar'))
@access_required(groups=['ain7-secretariat','ain7-ca'], allow_myself=True)
def avatar_delete(request, user_id):

    person = Person.objects.get(user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    ain7member.avatar.delete()
    ain7member.save()

    messages.success(request,
        _('Your avatar has been successfully deleted.'))
    return HttpResponseRedirect('/annuaire/%s/edit/' % user_id)

# Promos
@access_required(groups=['ain7-secretariat','ain7-ca'], allow_myself=True)
def promo_edit(request, user_id=None, promo_id=None):

    person = get_object_or_404(Person, id=user_id)
    ain7member = person.ain7member
    form = PromoForm()
    if request.method == 'POST':
        form = PromoForm(request.POST)
        if form.is_valid():
            promo = form.search()
            ain7member.promos.add(promo)
            messages.success(request,
                _('Promotion successfully added.'))
        else:
            return render(
                request, 'annuaire/edit_form.html',
                {'form': form, 
                 'action_title': _(u'Adding a promotion for %s' % ain7member)})
        return HttpResponseRedirect(
            '/annuaire/%s/edit/#promos' % user_id)
    return render(
        request, 'annuaire/edit_form.html',
        {'form': form, 'action_title': 
         _(u'Adding a promotion for %s' % ain7member)})

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
    title = _('Creation of an address for')
    form = AddressForm()

    if address_id:
        address = get_object_or_404(Address, pk=address_id)
        form = AddressForm(instance=address)

        title = _('Modification of an address for')

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            adr = form.save(commit=False)
            adr.person = person
            adr.save()

            messages.success(request, _('Address successfully saved'))

            return HttpResponseRedirect(reverse('ain7.annuaire.views.edit',
                 kwargs={'user_id': user_id}))

    return render(
        request, 'annuaire/edit_form.html',
        {'form': form, 'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda user_id=None, address_id=None :
    str(get_object_or_404(Address, pk=address_id)), 'annuaire/base.html', 
    _('Do you really want to delete your address'))
@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def address_delete(request, user_id=None, address_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(Address, pk=address_id),
        '/annuaire/%s/edit/#address' % user_id,
        _('Address successfully deleted.'))

# Numeros de telephone
@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def phone_edit(request, user_id=None, phone_id=None):

    person = get_object_or_404(Person, user=user_id)
    phone = None
    title = _('Creation of a phone number for')
    form = PhoneNumberForm()

    if phone_id:
        phone = get_object_or_404(PhoneNumber, pk=phone_id)
        form = PhoneNumberForm(instance=phone)

        title = _('Modification of a phone number for')

    if request.method == 'POST':
        form = PhoneNumberForm(request.POST, instance=phone)
        if form.is_valid():
            phon = form.save(commit=False)
            phon.person = person
            phon.save()

            messages.success(request, _('Phone number successfully saved'))

            return HttpResponseRedirect(reverse('ain7.annuaire.views.edit',
                kwargs={'user_id': user_id}))

    return render(
        request, 'annuaire/edit_form.html',
        {'form': form, 'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')})

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
    email = None
    title = _('Creation of an email address for')

    from django import forms

    class EmailFormDyn(EmailForm):
        """email form"""

        position = forms.ChoiceField(required=False, 
             choices = [('', '----------')] + [(p.id, p.office.organization) \
             for p in Position.objects.filter(\
             ain7member__person__id=person.id)])
        if email_id:
            email = get_object_or_404(Email, pk=email_id)
            if email and email.position_id:
                position.initial = email.position.id

    form = EmailFormDyn()

    if email_id:
        email = get_object_or_404(Email, pk=email_id)

        form = EmailFormDyn(instance=email)

        title = _('Modification of an email address for')

    if request.method == 'POST':
        form = EmailFormDyn(request.POST, instance=email)
        if form.is_valid():
            mail = form.save(commit=False)
            mail.person = person
            if form.cleaned_data['position']:
                mail.position = Position.objects.get(\
                    id=form.cleaned_data['position'])
            else:
                mail.position = None
            mail.save()

            messages.success(request, _('Email successfully saved'))

            return HttpResponseRedirect(reverse('ain7.annuaire.views.edit',
                kwargs={'user_id': user_id}))

    return render(
        request, 'annuaire/edit_form.html',
        {'form': form, 'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')})

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
    title = _('Creation of an instant messaging account for')
    form = InstantMessagingForm()

    if im_id:
        ime = get_object_or_404(InstantMessaging, pk=im_id)
        form = InstantMessagingForm(instance=ime)

        title = _('Modification of an instant messaging account for')

    if request.method == 'POST':
        form = InstantMessagingForm(request.POST, instance=ime)
        if form.is_valid():
            inm = form.save(commit=False)
            inm.person = person
            inm.save()

            messages.success(request, _('Instant messaging successfully saved'))

            return HttpResponseRedirect(reverse('ain7.annuaire.views.edit',
                kwargs={'user_id': user_id}))

    return render(
        request, 'annuaire/edit_form.html',
        {'form': form, 'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')})

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
    form = IRCForm()

    if irc_id:
        irc = get_object_or_404(IRC, pk=irc_id)
        form = IRCForm(instance=irc)

        title = _('Modification of an IRC account for')

    if request.method == 'POST':
        form = IRCForm(request.POST, instance=irc)
        if form.is_valid():
            this_irc = form.save(commit=False)
            this_irc.person = person
            this_irc.save()

            messages.success(request, _('irc contact successfully saved'))

            return HttpResponseRedirect(reverse('ain7.annuaire.views.edit',
                kwargs={'user_id': user_id}))

    return render(
        request, 'annuaire/edit_form.html',
        {'form': form, 'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')})

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
    form = WebSiteForm()

    if website_id:
        website = get_object_or_404(WebSite, pk=website_id)
        form = WebSiteForm(instance=website)

        title = _('Modification of a website for')

    if request.method == 'POST':
        form = WebSiteForm(request.POST, instance=website)
        if form.is_valid():
            web = form.save(commit=False)
            web.person = person
            web.save()

            messages.success(request, _('website successfully saved'))

            return HttpResponseRedirect(reverse('ain7.annuaire.views.edit',
                kwargs={'user_id': user_id}))

    return render(
        request, 'annuaire/edit_form.html',
        {'form': form, 'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')})

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
    club_membership = None
    title = _('Creation of a club membership for')
    form = ClubMembershipForm()
 
    if club_membership_id:
        club_membership = get_object_or_404(ClubMembership,
            pk=club_membership_id)
        form = ClubMembershipForm(instance=club_membership)

        title = _('Modification of a club membership for')

    if request.method == 'POST':
        form = ClubMembershipForm(request.POST, instance=club_membership)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.member = ain7member
            membership.save()

            messages.success(request, _('Club membership successfully saved'))

            return HttpResponseRedirect(reverse('ain7.annuaire.views.edit',
                kwargs={'user_id': user_id}))

    return render(
        request, 'annuaire/edit_form.html',
        {'form': form, 'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')})

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

    form = NewMemberForm()

    if request.method == 'POST':
        form = NewMemberForm(request.POST)
        if form.is_valid():
            new_person = form.save()
            messages.success(request, _("New user successfully created"))
            return HttpResponseRedirect('/annuaire/%s/edit/' % \
                (new_person.user.id))
        else:
            messages.error(request, _("Something was wrong in\
 the form you filled. No modification done."))

    back = request.META.get('HTTP_REFERER', '/')
    return render(request,
        'annuaire/edit_form.html',
        {'action_title': _('Register new user'), 'back': back, 'form': form})

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

