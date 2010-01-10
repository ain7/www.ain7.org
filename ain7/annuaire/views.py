# -*- coding: utf-8
"""
 ain7/annuaire/views.py
"""
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

import vobject
import datetime

from django.contrib import auth
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _
from django.http import Http404

from ain7.annuaire.models import *
from ain7.annuaire.forms import *
from ain7.adhesions.forms import Subscription
from ain7.decorators import confirmation_required
from ain7.search_engine.models import *
from ain7.search_engine.utils import *
from ain7.search_engine.views import *
from ain7.utils import ain7_render_to_response, ain7_generic_edit
from ain7.utils import ain7_generic_delete, check_access
from ain7.settings import AIN7_PORTAL_ADMIN


# Main functions

def annuaire_search_engine():
    return get_object_or_404(SearchEngine, name="annuaire")

@login_required
def details(request, user_id):
    person = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    is_myself = int(request.user.id) == int(user_id)
    last_activity = None
    user_activities = UserActivity.objects.filter(person=person)
    if len(user_activities) > 0:
        last_activity = user_activities.reverse()[0]
    is_subscriber = Subscription.objects.filter(member=ain7member).\
        filter(validated=True).exclude(start_year__gt=datetime.date.today().\
        year).exclude(end_year__lt=datetime.date.today().year)
    return ain7_render_to_response(request, 'annuaire/details.html',
        {'person': person, 'is_subscriber': is_subscriber,
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
                request.user.message_set.create(\
                     message=_("Only one result matched your criteria."))
                return HttpResponseRedirect('/annuaire/%s/' % \
                    (ain7members[0].id))

            # put the criteria in session: they must be accessed when
            # performing a CSV export, sending a mail...
            request.session['filter'] = criteria
            paginator = Paginator(ain7members, nb_results_by_page)

            try:
                page = int(request.GET.get('page', '1'))
                ain7members = paginator.page(page).object_list
            except InvalidPage:
                raise Http404

    return ain7_render_to_response(request, 'annuaire/search.html',
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
        return HttpResponseRedirect('/annuaire/'+str(user_id)+'/')

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
                request.user.message_set.create(\
                    message=_("Credentials updated."))
                return HttpResponseRedirect('/annuaire/'+str(person.id)+'/')
            else:
                request.user.message_set.create(message=_("Wrong authentication"))

    form = ChangePasswordForm(initial={'login': person.user.username})
    return ain7_render_to_response(request, 'annuaire/credentials.html',
        {'form': form, 'person': person, 'ain7member': ain7member,
         'is_myself': is_myself})

@login_required
def send_new_credentials(request, user_id):

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access

    person = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    password = User.objects.make_random_password(8)

    person.send_mail(_('Password reset of your AIn7 account'), \
    _("""Hi %(firstname)s,

Someone of the AIn7 Team has requested a new password for your
AIn7 account.

Your new credentials are:
Login: %(login)s
Password: %(password)s

-- 
http://ain7.com""") % { 'firstname': person.first_name, 
 'login': person.user.username, 'password': password } )

    request.user.message_set.create(message=_("New credentials have been sent"))
    return HttpResponseRedirect('/annuaire/'+str(person.id)+'/')

@login_required
def advanced_search(request):

    access = check_access(request, request.user,
        ['ain7-membre','ain7-secretariat'])
    if access:
        return access

    filter = annuaire_search_engine().unregistered_filters(request.user.person)
    if filter:
        return ain7_render_to_response(request, 'annuaire/adv_search.html',
            dict_for_filter(request, filter.id))
    else:
        return ain7_render_to_response(request, 'annuaire/adv_search.html',
            dict_for_filter(request, None))
    

@login_required
def filter_details(request, filter_id):

    access = check_access(request, request.user,
        ['ain7-membre','ain7-secretariat'])
    if access:
        return access

    return ain7_render_to_response(request, 'annuaire/adv_search.html',
        dict_for_filter(request, filter_id))


@login_required
def dict_for_filter(request, filter_id):

    access = check_access(request, request.user,
        ['ain7-membre','ain7-secretariat'])
    if access:
        return access

    ain7members = False
    dosearch = False
    person = request.user.person
    nb_results_by_page = 25
    paginator = Paginator(AIn7Member.objects.none(), nb_results_by_page)
    page = 1
    search_filter = None
    if filter_id:
        search_filter = get_object_or_404(SearchFilter, pk=filter_id)
        

    if request.method == 'POST':

        ain7members = AIn7Member.objects.all()
        if filter_id:
            ain7members = search_filter.search()
        dosearch = True
        paginator = Paginator(ain7members, nb_results_by_page)

        try:
            page = int(request.GET.get('page', '1'))
            ain7members = paginator.page(page).object_list
        except InvalidPage:
            raise http.Http404

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


@login_required
def filter_register(request):

    access = check_access(request, request.user,
        ['ain7-membre','ain7-secretariat'])
    if access:
        return access

    search_filter = annuaire_search_engine().unregistered_filters(\
        request.user.person)
    if not search_filter:
        return HttpResponseRedirect('/annuaire/advanced_search/')

    form = SearchFilterForm()

    if request.method != 'POST':
        return ain7_render_to_response(request,
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
                request.user.message_set.create(message=_("One of your filters\
 already has this name."))
                return HttpResponseRedirect('/annuaire/advanced_search/')

            # Set the registered flag to True
            search_filter.registered = True
            search_filter.name = fName
            search_filter.save()

            # Redirect to filter page
            request.user.message_set.create(
                message=_("Modifications have been successfully saved."))
            return HttpResponseRedirect(
                '/annuaire/advanced_search/filter/%s/' % search_filter.id)
        else:
            request.user.message_set.create(message=_("Something was wrong in\
 the form you filled. No modification done."))
        return HttpResponseRedirect('/annuaire/advanced_search/')


@login_required
def filter_edit(request, filter_id):

    access = check_access(request, request.user,
        ['ain7-membre','ain7-secretariat'])
    if access:
        return access

    filtr = get_object_or_404(SearchFilter, pk=filter_id)
    form = SearchFilterForm(instance=filtr)

    if request.method == 'POST':
        form = SearchFilterForm(request.POST, instance=filtr)
        if form.is_valid():
            form.cleaned_data['user'] = filtr.user
            form.cleaned_data['operator'] = filtr.operator
            form.save()
            request.user.message_set.create(message=_("Modifications have been\
 successfully saved."))
        else:
            request.user.message_set.create(message=_("Something was wrong in\
 the form you filled. No modification done."))
        return HttpResponseRedirect(
            '/annuaire/advanced_search/filter/%s/' % filter_id)
    return ain7_render_to_response(
        request, 'annuaire/edit_form.html',
        {'form': form, 'action_title': _("Modification of the filter")})


@login_required
def remove_criteria(request, filtr):
    for crit in filtr.criteriaField.all():  crit.delete()
    for crit in filtr.criteriaFilter.all(): crit.delete()
    # TODO non recursivite + supprimer filtres sans criteres
    return

@login_required
def filter_reset(request, filter_id):

    access = check_access(request, request.user,
        ['ain7-membre','ain7-secretariat'])
    if access:
        return access

    filtr = get_object_or_404(SearchFilter, pk=filter_id)
    remove_criteria(request, filtr)
    if filtr.registered:
        return HttpResponseRedirect(
            '/annuaire/advanced_search/filter/%s/' % filter_id)
    else:
        return HttpResponseRedirect('/annuaire/advanced_search/')

@login_required
def filter_delete(request, filter_id):

    access = check_access(request, request.user,
        ['ain7-membre','ain7-secretariat'])
    if access:
        return access

    filtr = get_object_or_404(SearchFilter, pk=filter_id)
    try:
        # remove criteria linked to this filter from database
        remove_criteria(request, filtr)
        # now remove the filter
        filtr.delete()
        request.user.message_set.create(
            message=_("Your filter has been successfully deleted."))
    except KeyError:
        request.user.message_set.create(
            message=_("Something went wrong. The filter has not been deleted.")) 
    return HttpResponseRedirect('/annuaire/advanced_search/')

@login_required
def filter_new(request):

    access = check_access(request, request.user,
        ['ain7-membre','ain7-secretariat'])
    if access:
        return access

    filter = annuaire_search_engine().unregistered_filters(request.user.person)
    if not filter:
        return HttpResponseRedirect('/annuaire/advanced_search/')
    remove_criteria(request, filter)
    if filter.registered:
        return HttpResponseRedirect(
            '/annuaire/advanced_search/filter/%s/' % filter.id)
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
    return se_criterionField_edit(request, annuaire_search_engine(),
        filter_id, criterion_id, reverse(filter_details, args=[filter_id]),
        reverse(advanced_search), 'annuaire/criterion_edit.html')

@login_required
def criterionFilter_edit(request, filter_id=None, criterion_id=None):
    return se_criterionFilter_edit(request, annuaire_search_engine(),
        filter_id, criterion_id, reverse(filter_details, args=[filter_id]),
        'annuaire/criterionFilter_edit.html')

@login_required
def criterion_delete(request, filtr_id=None, crit_id=None, crit_type=None):
    return se_criterion_delete(request, filtr_id, crit_id, crit_type,
        reverse(filter_details, args=[filtr_id]), reverse(advanced_search))

@login_required
def export_csv(request):

    access = check_access(request, request.user,
        ['ain7-secretariat','ain7-ca'])
    if access:
        return access

    if not request.session.has_key('filter'):
        request.user.message_set.create(message=_("You have to make a search\
 before using csv export."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    criteria = request.session['filter']
    ain7members = AIn7Member.objects.filter(criteria).distinct()

    return se_export_csv(request, ain7members, annuaire_search_engine(),
        'annuaire/edit_form.html')

@login_required
def adv_export_csv(request, filter_id=None):

    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-ca'])
    if access:
        return access

    se = annuaire_search_engine()
    if not filter_id and not se.unregistered_filters(request.user.person):
        request.user.message_set.create(message=
            _("You have to make a search before using csv export."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    if filter_id:
        search_filter = get_object_or_404(SearchFilter, id=filter_id)
    else:
        search_filter = se.unregistered_filters(request.user.person)
    return se_export_csv(request, search_filter.search(), se, 
        'annuaire/edit_form.html')

@login_required
def edit(request, user_id=None):

    is_myself = int(request.user.id) == int(user_id)

    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-ca'])
    if access and not is_myself:
        return access

    person = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    return ain7_render_to_response(request, 'annuaire/edit.html',
        {'person': person, 'ain7member': ain7member, 'is_myself': is_myself})

@login_required
def person_edit(request, user_id=None):

    is_myself = int(request.user.id) == int(user_id)

    access = check_access(request, request.user,
        ['ain7-secretariat','ain7-ca'])
    if access and not is_myself:
        return access

    person = None
    if user_id:
        person = Person.objects.get(user=user_id)
    # si la personne n'est pas du secrétariat, pas de date de décès
    user_groups = request.user.groups.values_list('name', flat=True)
    if 'ain7-secretariat' in user_groups \
        or AIN7_PORTAL_ADMIN in user_groups:
        return ain7_generic_edit(
            request, person, PersonForm, {'user': person.user},
            'annuaire/edit_form.html',
            {'action_title': _("Modification of personal data for"),
             'person': person, 'back': request.META.get('HTTP_REFERER', '/')},
            {}, '/annuaire/%s/edit' % (person.user.id),
            _("Modifications have been successfully saved."))
    else:
        return ain7_generic_edit(
            request, person, PersonFormNoDeath,
            {'user': person.user,'death_date': person.death_date},
            'annuaire/edit_form.html',
            {'action_title': _("Modification of personal data for"),
             'person': person, 'back': request.META.get('HTTP_REFERER', '/')},
             {}, '/annuaire/%s/edit' % (person.user.id),
            _("Modifications have been successfully saved."))

@login_required
def ain7member_edit(request, user_id=None):

    is_myself = int(request.user.id) == int(user_id)

    access = check_access(request, request.user,
        ['ain7-secretariat','ain7-ca'])
    if access and not is_myself:
        return access

    person = None
    ain7member = None
    if user_id:
        person = get_object_or_404(Person, user=user_id)
        ain7member = get_object_or_404(AIn7Member, person=person)
    return ain7_generic_edit(
        request, ain7member, AIn7MemberForm, {'person': person},
        'annuaire/edit_form.html',
        {'action_title': _("Modification of personal data for"),
         'person': person, 'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/annuaire/%s/edit' % (person.user.id),
        _("Modifications have been successfully saved."))

@confirmation_required(lambda user_id=None, object_id=None : '',
     'annuaire/base.html', _('Do you really want to delete your avatar'))
@login_required
def avatar_delete(request, user_id):

    is_myself = int(request.user.id) == int(user_id)

    access = check_access(request, request.user,
        ['ain7-secretariat','ain7-ca'])
    if access and not is_myself:
        return access

    person = Person.objects.get(user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    ain7member.avatar = None
    ain7member.save()

    request.user.message_set.create(message=
        _('Your avatar has been successfully deleted.'))
    return HttpResponseRedirect('/annuaire/%s/edit/' % user_id)

# Promos
@login_required
def promo_edit(request, person_id=None, promo_id=None):

    is_myself = int(request.user.id) == int(person_id)

    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-ca'])
    if access and not is_myself:
        return access

    person = get_object_or_404(Person, id=person_id)
    ain7member = person.ain7member
    form = PromoForm()
    if request.method == 'POST':
        form = PromoForm(request.POST)
        if form.is_valid():
            promo = form.search()
            ain7member.promos.add(promo)
            request.user.message_set.create(message=_('Promotion successfully added.'))
        else:
            return ain7_render_to_response(
                request, 'annuaire/edit_form.html',
                {'form': form, 
                 'action_title': _(u'Adding a promotion for %s' % ain7member)})
#             request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))
        return HttpResponseRedirect(
            '/annuaire/%s/edit/#promos' % person_id)
    return ain7_render_to_response(
        request, 'annuaire/edit_form.html',
        {'form': form, 'action_title': 
         _(u'Adding a promotion for %s' % ain7member)})

@confirmation_required(lambda person_id=None, promo_id=None :
     str(get_object_or_404(Promo, pk=promo_id)), 
     'annuaire/base.html', 
     _('Do you really want to remove the membership to the promotion'))
@login_required
def promo_delete(request, person_id=None, promo_id=None):

    person = get_object_or_404(Person, id=person_id)
    is_myself = int(request.user.id) == int(person.user.id)

    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-ca'])
    if access and not is_myself:
        return access
    ain7member = get_object_or_404(AIn7Member, person=person)
    promo = get_object_or_404(Promo, id=promo_id)
    ain7member.promos.remove(promo)
    ain7member.save()
    request.user.message_set.create(message="Membership to promotion %s\
 successfully removed.")
    return HttpResponseRedirect('/annuaire/%s/edit/#promos' % person_id)

# Adresses
@login_required
def address_edit(request, user_id=None, address_id=None):

    is_myself = int(request.user.id) == int(user_id)

    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-ca'])
    if access and not is_myself:
        return access

    person = get_object_or_404(Person, user=user_id)
    address = None
    title = _('Creation of an address for')
    msg_done = _('Address successfully added.')
    if address_id:
        address = get_object_or_404(Address, pk=address_id)
        title = _('Modification of an address for')
        msg_done = _('Address informations updated successfully.')
    return ain7_generic_edit(
        request, address, AddressForm, {'person': person},
        'annuaire/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/annuaire/%s/edit/#address' % user_id, msg_done)

@confirmation_required(lambda user_id=None, address_id=None :
    str(get_object_or_404(Address, pk=address_id)), 'annuaire/base.html', 
    _('Do you really want to delete your address'))
@login_required
def address_delete(request, user_id=None, address_id=None):

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user, 
        ['ain7-secretariat', 'ain7-ca'])
    if access and not is_myself:
        return access

    return ain7_generic_delete(request,
        get_object_or_404(Address, pk=address_id),
        '/annuaire/%s/edit/#address' % user_id,
        _('Address successfully deleted.'))

# Numeros de telephone
@login_required
def phone_edit(request, user_id=None, phone_id=None):

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-ca'])
    if access and not is_myself:
        return access

    person = get_object_or_404(Person, user=user_id)
    phone = None
    title = _('Creation of a phone number for')
    msg_done = _('Phone number added successfully.')
    if phone_id:
        phone = get_object_or_404(PhoneNumber, pk=phone_id)
        title = _('Modification of a phone number for')
        msg_done = _('Phone number informations updated successfully.')
    return ain7_generic_edit(
        request, phone, PhoneNumberForm, {'person': person},
        'annuaire/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/annuaire/%s/edit/#phone' % user_id, msg_done)

@confirmation_required(lambda user_id=None, phone_id=None :
    str(get_object_or_404(PhoneNumber, pk=phone_id)), 'annuaire/base.html', 
    _('Do you really want to delete your phone number'))
@login_required
def phone_delete(request, user_id=None, phone_id=None):

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user, 
        ['ain7-secretariat', 'ain7-ca'])
    if access and not is_myself:
        return access

    return ain7_generic_delete(request,
        get_object_or_404(PhoneNumber, pk=phone_id),
        '/annuaire/%s/edit/#phone' % user_id,
        _('Phone number successfully deleted.'))

# Adresses de courriel
@login_required
def email_edit(request, user_id=None, email_id=None):

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user, 
        ['ain7-secretariat', 'ain7-ca'])
    if access and not is_myself:
        return access

    person = get_object_or_404(Person, user=user_id)
    email = None
    title = _('Creation of an email address for')
    msg_done = _('Email address successfully added.')
    if email_id:
        email = get_object_or_404(Email, pk=email_id)
        title = _('Modification of an email address for')
        msg_done = _('Email informations updated successfully.')
    return ain7_generic_edit(
        request, email, EmailForm, {'person': person},
        'annuaire/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
         '/annuaire/%s/edit/#email' % user_id, msg_done)

@confirmation_required(lambda user_id=None, email_id=None:
    str(get_object_or_404(Email, pk=email_id)), 'annuaire/base.html', 
    _('Do you really want to delete your email address'))
@login_required
def email_delete(request, user_id=None, email_id=None):

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-ca'])
    if access and not is_myself:
        return access

    return ain7_generic_delete(request, get_object_or_404(Email, pk=email_id),
                               '/annuaire/%s/edit/#email' % user_id,
                               _('Email address successfully deleted.'))

# Comptes de messagerie instantanee
@login_required
def im_edit(request, user_id=None, im_id=None):

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-ca'])
    if access and not is_myself:
        return access

    person = get_object_or_404(Person, user=user_id)
    ime = None
    title = _('Creation of an instant messaging account for')
    msg_done = _('Instant messaging account successfully added.')
    if im_id:
        ime = get_object_or_404(InstantMessaging, pk=im_id)
        title = _('Modification of an instant messaging account for')
        msg_done = _('Instant messaging informations updated successfully.')
    return ain7_generic_edit(
        request, ime, InstantMessagingForm, {'person': person},
        'annuaire/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/annuaire/%s/edit/#im' % user_id, msg_done)

@confirmation_required(lambda user_id=None, im_id=None :
    str(get_object_or_404(InstantMessaging, pk=im_id)), 'annuaire/base.html',
    _('Do you really want to delete your instant messaging account'))
@login_required
def im_delete(request, user_id=None, im_id=None):

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-ca'])
    if access and not is_myself:
        return access

    return ain7_generic_delete(request,
        get_object_or_404(InstantMessaging, pk=im_id),
        '/annuaire/%s/edit/#im' % user_id,
        _('Instant messaging account successfully deleted.'))

# Comptes IRC
@login_required
def irc_edit(request, user_id=None, irc_id=None):

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-ca'])
    if access and not is_myself:
        return access

    person = get_object_or_404(Person, user=user_id)
    irc = None
    title = _('Creation of an IRC account for')
    msg_done = _('IRC account successfully added.')
    if irc_id:
        irc = get_object_or_404(IRC, pk=irc_id)
        title = _('Modification of an IRC account for')
        msg_done = _('IRC account informations updated successfully.')
    return ain7_generic_edit(
        request, irc, IRCForm, {'person': person},
        'annuaire/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/annuaire/%s/edit/#irc' % user_id, msg_done)

@confirmation_required(lambda user_id=None, irc_id=None:
    str(get_object_or_404(IRC, pk=irc_id)), 'annuaire/base.html',
    _('Do you really want to delete your IRC account'))
@login_required
def irc_delete(request, user_id=None, irc_id=None):

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-ca'])
    if access and not is_myself:
        return access

    return ain7_generic_delete(request,
        get_object_or_404(IRC, pk=irc_id),
        '/annuaire/%s/edit/#irc' % user_id,
        _('IRC account successfully deleted.'))

# Sites Internet
@login_required
def website_edit(request, user_id=None, website_id=None):

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user, 
        ['ain7-secretariat', 'ain7-ca'])
    if access and not is_myself:
        return access

    person = get_object_or_404(Person, user=user_id)
    website = None
    title = _('Creation of a website for')
    msg_done = _('Website successfully added.')
    if website_id:
        website = get_object_or_404(WebSite, pk=website_id)
        title = _('Modification of a website for')
        msg_done = _('Website informations updated successfully.')
    return ain7_generic_edit(
        request, website, WebSiteForm, {'person': person},
        'annuaire/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/annuaire/%s/edit/#website' % user_id, msg_done)

@confirmation_required(lambda user_id=None, website_id=None:
    str(get_object_or_404(WebSite, pk=website_id)), 'annuaire/base.html',
    _('Do you really want to delete your website'))
@login_required
def website_delete(request, user_id=None, website_id=None):

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-ca'])
    if access and not is_myself:
        return access

    return ain7_generic_delete(request,
        get_object_or_404(WebSite, pk=website_id),
        '/annuaire/%s/edit/#website' % user_id,
        _('Website successfully deleted.'))

# Vie associative a l'n7

@login_required
def club_membership_edit(request, user_id=None, club_membership_id=None):

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-ca'])
    if access and not is_myself:
        return access

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    club_membership = None
    title = _('Creation of a club membership for')
    msg_done = _('Club membership successfully added.')
    if club_membership_id:
        club_membership = get_object_or_404(ClubMembership,
                                            pk=club_membership_id)
        title = _('Modification of a club membership for')
        msg_done = _('Club membership informations updated successfully.')
    return ain7_generic_edit(
        request, club_membership, ClubMembershipForm,
        {'member': ain7member}, 'annuaire/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/annuaire/%s/edit/#assoc' % user_id, msg_done)

@confirmation_required(lambda user_id=None, club_membership_id=None:
    str(get_object_or_404(ClubMembership, pk=club_membership_id)),
    'annuaire/base.html', 
    _('Do you really want to delete your club membership'))
@login_required
def club_membership_delete(request, user_id=None, club_membership_id=None):

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-ca'])
    if access and not is_myself:
        return access

    return ain7_generic_delete(request,
        get_object_or_404(ClubMembership, pk=club_membership_id),
        '/annuaire/%s/edit/#assoc' % user_id,
        _('Club membership successfully deleted.'))

@login_required
def add(request, user_id=None):

    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-ca'])
    if access:
        return access

    form = NewMemberForm()

    if request.method == 'POST':
        form = NewMemberForm(request.POST)
        if form.is_valid():
            new_person = form.save()
            request.user.message_set.create(message=\
                _("New user successfully created"))
            return HttpResponseRedirect('/annuaire/%s/edit/' % \
                (new_person.user.id))
        else:
            request.user.message_set.create(message=_("Something was wrong in\
 the form you filled. No modification done."))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request,
        'annuaire/edit_form.html',
        {'action_title': _('Register new user'), 'back': back, 'form': form})

@login_required
def vcard(request, user_id):

    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-membre'])
    if access:
        return access

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

