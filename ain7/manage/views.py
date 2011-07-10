# -*- coding: utf-8
"""
  ain7/manage/views.py
"""
#
#   Copyright © 2007-2011 AIn7 Devel Team
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

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _

from ain7.utils import check_access
from ain7.organizations.models import Organization, Office
from ain7.manage.models import Mailing, PortalError
from ain7.shop.models import Payment
from ain7.manage.forms import SearchUserForm, NewPersonForm, \
                              PortalErrorForm, ErrorRangeForm, \
                              MailingForm,PaymentForm
from ain7.news.models import NewsItem
from ain7.search_engine.models import SearchEngine, SearchFilter
from ain7.search_engine.forms import SearchFilterForm
from ain7.search_engine.views import se_filter_swap_op, \
                                     se_criterion_field_edit, \
                                     se_criterion_add, \
                                     se_criterion_filter_edit, \
                                     se_criterion_delete, se_export_csv


def organization_search_engine():
    """organization search"""
    return get_object_or_404(SearchEngine, name="organization")

@login_required
def index(request):
    """index management"""

    access = check_access(request, request.user,
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    return render(request, 'manage/default.html',
        {'notifications': None})

@login_required
def users_search(request):
    """search users"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    form = SearchUserForm()
    nb_results_by_page = 25
    persons = False
    paginator = Paginator([], nb_results_by_page)
    page = 1

    if request.GET.has_key('last_name') or \
       request.GET.has_key('first_name') or \
       request.GET.has_key('organization'):
        form = SearchUserForm(request.GET)
        if form.is_valid():
            persons = form.search()
            paginator = Paginator(persons, nb_results_by_page)
            try:
                page = int(request.GET.get('page', '1'))
                persons = paginator.page(page).object_list
            except InvalidPage:
                raise Http404

    return render(request, 'manage/users_search.html',
        {'form': form, 'persons': persons, 'request': request,
         'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page,
         'next_page': page + 1, 'previous_page': page - 1,
         'pages': paginator.num_pages,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits' : paginator.count})

@login_required
def user_register(request):
    """new user registration"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access

    form = NewPersonForm()

    if request.method == 'POST':
        form = NewPersonForm(request.POST)
        if form.is_valid():
            new_person = form.save()
            request.user.message_set.create(
                message=_("New user successfully created"))
            return HttpResponseRedirect(
                '/manage/users/%s/' % (new_person.user.id))
        else:
            request.user.message_set.create(message=_("Something was wrong in\
 the form you filled. No modification done."))

    back = request.META.get('HTTP_REFERER', '/')
    return render(request, 'manage/edit_form.html',
        {'action_title': _('Register new user'), 'back': back, 'form': form})

@login_required
def organizations_adv_search(request):
    """organization advanced search"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    filtr = organization_search_engine()\
            .unregistered_filters(request.user.person)
    if filtr:
        return render(request,
            'manage/organizations_adv_search.html',
            dict_for_filter(request, filtr.id))
    else:
        return render(request,
            'manage/organizations_adv_search.html',
            dict_for_filter(request, None))

@login_required
def dict_for_filter(request, filter_id):
    """dictionnary for search filter"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    offices = False
    person = request.user.person
    nb_results_by_page = 25
    paginator = Paginator(Office.objects.none(), nb_results_by_page)
    page = 1
    search_filter = None
    if filter_id:
        search_filter = get_object_or_404(SearchFilter, pk=filter_id)
        
    if request.method == 'POST':

        offices = Office.objects.all()
        if filter_id:
            offices = search_filter.search()
        paginator = Paginator(offices, nb_results_by_page)

        try:
            page = int(request.GET.get('page', '1'))
            offices = paginator.page(page).object_list
        except InvalidPage:
            raise Http404

    return {'offices': offices,
         'filtr': search_filter,
         'nb_org': Organization.objects.valid_organizations().count(),
         'nb_offices': Office.objects.valid_offices().count(),
         'userFilters': organization_search_engine().registered_filters(person),
         'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page,
         'next_page': page + 1, 'previous_page': page - 1,
         'pages': paginator.num_pages,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits' : paginator.count}

@login_required
def filter_details(request, filter_id):
    """filter details"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    return render(request,
        'manage/organizations_adv_search.html',
        dict_for_filter(request, filter_id))

@login_required
def filter_swap_op(request, filter_id=None):
    """change filter operator"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    return se_filter_swap_op(request, filter_id,
                            reverse(filter_details, args =[ filter_id ]),
                            reverse(organizations_adv_search))

@login_required
def filter_register(request):
    """register new filter"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    search_filter = organization_search_engine().\
         unregistered_filters(request.user.person)
    if not search_filter:
        return HttpResponseRedirect(reverse(organizations_adv_search))

    form = SearchFilterForm()

    if request.method != 'POST':
        return render(request,
            'manage/edit_form.html',
            {'form': form, 'back': request.META.get('HTTP_REFERER', '/'),
             'action_title': _("Enter parameters of your filter")})
    else:
        form = SearchFilterForm(request.POST)
        if form.is_valid():
            f_name = form.cleaned_data['name']
            # First we check that the user does not have
            # a filter with the same name
            same_name = organization_search_engine().\
                registered_filters(request.user.person).\
                filter(name=f_name).count()
            if same_name > 0:
                request.user.message_set.create(message=_("One of your\
 filters already has this name."))
                return HttpResponseRedirect(reverse(organizations_adv_search))

            # Set the registered flag to True
            search_filter.registered = True
            search_filter.name = f_name
            search_filter.save()

            # Redirect to filter page
            request.user.message_set.create(
                message=_("Modifications have been successfully saved."))
            return HttpResponseRedirect(
                reverse(filter_details, args=[ search_filter.id ]))
        else:
            request.user.message_set.create(message=_("Something was wrong in\
 the form you filled. No modification done."))
        return HttpResponseRedirect(reverse(organizations_adv_search))


@login_required
def filter_edit(request, filter_id):
    """edit search filter"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
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
            reverse(filter_details, args=[ filter_id ]))
    return render(
        request, 'manage/edit_form.html',
        {'form': form, 'action_title': _("Modification of the filter")})


@login_required
def remove_criteria(request, filtr):
    """remove search criteria"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    for crit in filtr.criteriaField.all():
        crit.delete()
    for crit in filtr.criteriaFilter.all():
        crit.delete()
    # TODO non recursivite + supprimer filtres sans criteres
    return

@login_required
def filter_reset(request, filter_id):
    """reset search filter"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    filtr = get_object_or_404(SearchFilter, pk=filter_id)
    remove_criteria(request, filtr)
    if filtr.registered:
        return HttpResponseRedirect(
            reverse(filter_details, args=[ filter_id ]))
    else:
        return HttpResponseRedirect(reverse(organizations_adv_search))

@login_required
def filter_delete(request, filter_id):
    """delete search filter"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
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
    return HttpResponseRedirect(reverse(organizations_adv_search))

@login_required
def filter_new(request):
    """new search filter"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    filter = organization_search_engine().unregistered_filters(\
        request.user.person)
    if not filter:
        return HttpResponseRedirect(reverse(organizations_adv_search))
    remove_criteria(request, filter)
    if filter.registered:
        return HttpResponseRedirect(
            reverse(filter_details, args=[ filter.id ]))
    else:
        return HttpResponseRedirect(reverse(organizations_adv_search))

@login_required
def criterion_add(request, filter_id=None, criterion_type=None):
    """add criterion to a search filter"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    redirect = reverse(organizations_adv_search)
    if filter_id:
        redirect = reverse(filter_details, args=[ filter_id ])
    return se_criterion_add(request, organization_search_engine(),
        filter_id, criterion_type, criterion_field_edit,
        redirect, 'manage/org_criterion_add.html')

@login_required
def criterion_field_edit(request, filter_id=None, criterion_id=None):
    """criterion edit in a search filter"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    return se_criterion_field_edit(request, organization_search_engine(),
        filter_id, criterion_id, reverse(filter_details, args=[filter_id]),
        reverse(organizations_adv_search),
        'manage/org_criterion_edit.html')

@login_required
def criterion_filter_edit(request, filter_id=None, criterion_id=None):
    """criterion edit in a search filter"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    return se_criterion_filter_edit(request, organization_search_engine(),
        filter_id, criterion_id, reverse(filter_details, args=[filter_id]),
        'manage/org_criterionFilter_edit.html')

@login_required
def criterion_delete(request, filtr_id=None, crit_id=None, crit_type=None):
    """criterion delete in a search filter"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    return se_criterion_delete(request, filtr_id, crit_id, crit_type,
        reverse(filter_details, args=[filtr_id]),
        reverse(organizations_adv_search))

@login_required
def export_csv(request):
    """csv export"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    if not request.session.has_key('filter'):
        request.user.message_set.create(message=_("You have to make a search\
 before using csv export."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    criteria = request.session['filter']
    orgs = Organization.objects.filter(**criteria).distinct()
    offices = Office.objects.filter(organization__in=orgs)

    return se_export_csv(request, offices, organization_search_engine(),
        'manage/edit_form.html')

@login_required
def adv_export_csv(request, filter_id=None):
    """advanced csv export"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    search_engine = organization_search_engine()
    if not filter_id and not \
        search_engine.unregistered_filters(request.user.person):
        request.user.message_set.create(message=
            _("You have to make a search before using csv export."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    if filter_id:
        search_filter = get_object_or_404(SearchFilter, id=filter_id)
    else:
        search_filter = search_engine.unregistered_filters(request.user.person)
    return se_export_csv(request, search_filter.search(), search_engine,
        'manage/edit_form.html')

@login_required
def errors_index(request):
    """errors index"""

    access = check_access(request, request.user, 
        ['ain7-ca', 'ain7-secretariat', 'ain7-devel'])
    if access:
        return access

    nb_results_by_page = 25 
    errors = PortalError.objects.all().order_by('-date')
    paginator = Paginator(errors, nb_results_by_page)
    try:
        page = int(request.GET.get('page', '1'))
        errors = paginator.page(page).object_list
    except InvalidPage:
        raise Http404

    return render(request, 'manage/errors_index.html',
        {'errors': errors, 'request': request,
         'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page,
         'next_page': page + 1, 'previous_page': page - 1,
         'pages': paginator.num_pages,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits' : paginator.count})

@login_required
def error_details(request, error_id):
    """error edition"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat', 'ain7-devel'])
    if access:
        return access

    error = get_object_or_404(PortalError, pk=error_id)
    form = PortalErrorForm(instance=error)

    from pygments import highlight
    from pygments.lexers import PythonTracebackLexer
    from pygments.formatters import HtmlFormatter

    traceback = highlight(error.exception, PythonTracebackLexer(), \
        HtmlFormatter())

    if request.method == 'POST':
        form = PortalErrorForm(request.POST.copy(), instance=error)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse(error_details, args=[error.id]))

    return render(
        request, 'manage/error_details.html',
        {'error': error, 'form': form, 'traceback': traceback, 
         'back': request.META.get('HTTP_REFERER', '/')})

@login_required
def errors_edit_range(request):
    """error edition"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat', 'ain7-devel'])
    if access:
        return access

    form = ErrorRangeForm()
    if request.method == 'POST':
        form = ErrorRangeForm(request.POST.copy())
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(errors_index))

    return render(
        request, 'manage/edit_form.html',
        {'form': form, 'back': request.META.get('HTTP_REFERER', '/')})

@login_required
def error_swap(request, error_id):
    """swap error fixed status"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat', 'ain7-devel'])
    if access:
        return access

    error = get_object_or_404(PortalError, pk=error_id)
    error.fixed = not(error.fixed)
    error.save()

    return errors_index(request)

@login_required
def payments_index(request):
    """payment index"""

    access = check_access(request, request.user,
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    nb_results_by_page = 25 
    payments = Payment.objects.all().order_by('-id')
    paginator = Paginator(payments, nb_results_by_page)
    try:
        page = int(request.GET.get('page', '1'))
        payments = paginator.page(page).object_list
    except InvalidPage:
        raise Http404

    return render(request, 'manage/payments_index.html',
        {'payments': payments,
         'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page,
         'next_page': page + 1, 'previous_page': page - 1,
         'pages': paginator.num_pages,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits' : paginator.count})

@login_required
def payment_add(request):
    """payment add"""

    access = check_access(request, request.user, 
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    payments_list = Payment.objects.all()

    return render(
        request, 'manage/payments_index.html', {'payment_list': payments_list})

@login_required
def payment_details(request, payment_id):
    """payment details"""

    access = check_access(request, request.user, 
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    payment = get_object_or_404(Payment, pk=payment_id)

    return render(
        request, 'manage/payment_details.html', {'payment': payment})

@login_required
def payment_edit(request, payment_id):
    """payment edit"""

    access = check_access(request, request.user, 
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    payment = get_object_or_404(Payment, pk=payment_id)

    form = PaymentForm(instance=payment)

    if request.method == 'POST':
        form = PaymentForm(request.POST.copy(), instance=payment)
        if form.is_valid():
            form.save()
            request.user.message_set.create(message=_('Payment successfully\
 updated'))
            return HttpResponseRedirect(reverse(payment_details, \
                args=[payment.id]))
        else:
            request.user.message_set.create(message=_('Something was wrong in\
 the form you filled. No modification done.') + str(form.errors))

    back = request.META.get('HTTP_REFERER', '/')

    return render(
        request, 'manage/payment_edit.html', {'payment': payment,
            'form': form, 'back': back})

@login_required
def payments_deposit_index(request):
    """payment deposit index"""

    access = check_access(request, request.user, 
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    return render(
        request, 'manage/payments_deposit_index.html', {})

@login_required
def payments_deposit(request, deposit_id):
    """payment deposit"""

    access = check_access(request, request.user, 
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    deposits = Payment.objects.filter(type=deposit_id, deposited__isnull=True, \
        validated=True).order_by('id')

    try:
        last_deposit_id = Payment.objects.filter(type=deposit_id, \
            deposited__isnull=True, validated=True).latest('id').id
    except Payment.DoesNotExist:
        request.user.message_set.create(message=_('No payment to deposit'))
        return HttpResponseRedirect(reverse(payments_deposit_index))

    return render(
        request, 'manage/payments_deposit.html', 
        {'deposits': deposits, 'deposit_id': int(deposit_id),
         'last_deposit_id': last_deposit_id })

@login_required
def payments_mark_deposited(request, deposit_id, last_deposit_id):
    """payment mark deposited"""

    access = check_access(request, request.user, 
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    for deposit in Payment.objects.filter(type=deposit_id, \
        deposited__isnull=True, validated=True):
        deposit.deposited = datetime.datetime.now()
        deposit.save()

    request.user.message_set.create(message=_('Payments marked as deposited'))
    return HttpResponseRedirect(reverse(payments_deposit_index))

@login_required
def subscriptions_stats(request):
    """have some subscriptions statistics"""

    access = check_access(request, request.user, 
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    from django.db.models import Q, Sum
    from ain7.adhesions.models import Subscription, SubscriptionConfiguration

    from datetime import date
    this_year = date.today().year

    stats_subs = []
    stats_year = {}

    for year in range(this_year, this_year-10, -1):

        last_promo = year-1

        # Cotisations à taux pleins hors élèves:
        diplomees_number = Subscription.objects.filter(\
            member__promos__year__year__lte=last_promo, start_year=year, \
            validated=True).distinct().count()

        # Cotisation à taux plein:
        full_price = SubscriptionConfiguration.objects.get(year=year, \
            type=0).dues_amount
        full_query = Q(member__promos__year__year__lte=last_promo, \
            dues_amount=full_price, start_year=year, validated=True)
        full_queryset = Subscription.objects.filter(full_query).distinct()
        full_number = full_queryset.count()
        full_amount = full_number * full_price

        # Cotisations jeunes promos:
        young_price = SubscriptionConfiguration.objects.get(year=year, \
            type=1).dues_amount
        young_query = Q(member__promos__year__year__lte=last_promo, \
            member__promos__year__year__gte=last_promo-4, \
            dues_amount=young_price, start_year=year, validated=True)
        young_queryset = Subscription.objects.filter(young_query).distinct()
        young_number = young_queryset.count()
        young_amount = young_number * young_price

        # Cotisations retraités:
        retired_price = SubscriptionConfiguration.objects.get(year=year, \
            type=2).dues_amount
        retired_query = Q(member__promos__year__year__lte=last_promo-5, \
            dues_amount=retired_price, start_year=year, validated=True)
        retired_queryset = Subscription.objects.filter(retired_query).distinct()
        retired_number = retired_queryset.count()
        retired_amount = retired_number * retired_price

        # Cotisations bienfaiteurs:
        bienfaiteur_price = SubscriptionConfiguration.objects.get(year=year, \
            type=3).dues_amount
        bienfaiteur_query = Q(member__promos__year__year__lte=last_promo, \
            dues_amount__gte=bienfaiteur_price, start_year=this_year, \
            validated=True)
        bienfaiteur_queryset = Subscription.objects.filter(bienfaiteur_query).distinct()
        bienfaiteur_number = bienfaiteur_queryset.count()
        bienfaiteur_amount = bienfaiteur_number * bienfaiteur_price

        # unemployed
        unemployed_price = SubscriptionConfiguration.objects.get(year=year, \
            type=4).dues_amount
        unemployed_query = Q(member__promos__year__year__lte=last_promo, \
            dues_amount=unemployed_price, start_year=year, validated=True)
        unemployed_queryset = Subscription.objects.filter(unemployed_query).distinct()
        unemployed_number = unemployed_queryset.count()
        unemployed_amount = unemployed_number * unemployed_price

        # students
        students_query = Q(member__promos__year__year__gt=last_promo, \
            start_year=year, validated=True)
        students_queryset = Subscription.objects.filter(students_query).distinct()
        students_number = students_queryset.count()
        students_amount = \
            students_queryset.aggregate(sum=Sum('dues_amount'))['sum']

        # all
        total_query = Q(start_year=year, member__promos__isnull=False, validated=True)
        total_queryset = Subscription.objects.filter(total_query)
        total_number = total_queryset.distinct().count()
        total_amount = total_queryset.distinct().aggregate(sum=Sum('dues_amount'))['sum']

        # other
        other_number = total_number - students_number - unemployed_number - \
            bienfaiteur_number - retired_number - young_number - full_number
        other_amount = total_amount - unemployed_amount - bienfaiteur_amount - \
            retired_amount - young_amount - full_amount

        stats_subs.append({'year': year, 
                           'diplomees': diplomees_number, 
                           'full': full_number, 
                           'young':young_number, 
                           'retired': retired_number, 
                           'bienfaiteur': bienfaiteur_number, 
                           'unemployed': unemployed_number, 
                           'other': other_number, 
                           'students': students_number, 
                           'total': total_number})

        if year == this_year:
            stats_year = {
                'full': { 
                    'number': full_number, 
                    'price': full_price, 
                    'amount': full_amount
                    },
                'young': { 
                    'number': young_number, 
                    'price': young_price, 
                    'amount': young_amount
                    },
                'retired': { 
                    'number': retired_number, 
                    'price': retired_price, 
                    'amount': retired_amount
                    },
                'bienfaiteur': { 
                    'number': bienfaiteur_number,
                    'price': bienfaiteur_price,
                    'amount': bienfaiteur_amount
                    },
                'unemployed': { 
                    'number': unemployed_number, 
                    'price': unemployed_price, 
                    'amount': unemployed_amount 
                    },
                'students': { 
                    'number': students_number,
                    'price': 0,
                    'amount': int(students_amount)
                    },
                'other': { 
                    'number': other_number, 
                    'price': 'n/a', 
                    'amount': int(other_amount)
                    },
                'total': { 
                    'number': total_number, 
                    'diplomees': diplomees_number, 
                    'amount': int(total_amount) 
                    }
            }

    stats_months = []
    for month in range(1, 13):
        first_day = date(this_year, month, 1)
        if month < 12:
            last_day = date(this_year, month+1, 1)
        else:
            last_day = date(this_year+1, 1, 1)
        stats_months.append(Subscription.objects.filter(\
            member__promos__year__year__lt=this_year, start_year=this_year, \
            validated=True, date__gte=first_day, date__lt=last_day).distinct().count())

    total_amount = 0
    for subs in Subscription.objects.filter(\
        member__promos__year__year__lt=this_year, start_year=this_year, \
        validated=True):
        total_amount += subs.dues_amount

    total_publications = 0
    for subs in Subscription.objects.filter(\
        member__promos__year__year__lt=this_year, start_year=this_year, \
        validated=True):
        if subs.newspaper_amount:
            total_publications += subs.newspaper_amount

    return render(
        request, 'manage/subscriptions_stats.html', 
        { 'stats_subs' : stats_subs, 
          'stats_months': stats_months, 
          'stats_year': stats_year, 
          'total_amount': total_amount, 
          'total_publications': total_publications
        })

@login_required
def mailings_index(request):
    """mailing index"""

    access = check_access(request, request.user, 
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    nb_results_by_page = 25

    mailings = Mailing.objects.all().order_by('-id')
    paginator = Paginator(mailings, nb_results_by_page)
    try:
        page = int(request.GET.get('page', '1'))
        payments = paginator.page(page).object_list
    except InvalidPage:
        raise Http404

    return render(request, 'manage/mailings_index.html',
        {'mailings': mailings,
         'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page,
         'next_page': page + 1, 'previous_page': page - 1,
         'pages': paginator.num_pages,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits' : paginator.count})

@login_required
def mailing_ready(request, mailing_id):
    """declare a mailing as ready to send"""

    access = check_access(request, request.user, 
                          ['ain7-secretariat'])
    if access:
        return access

    mailing = get_object_or_404(Mailing, pk=mailing_id)

    if not mailing.approved_at or not mailing.approved_by:
        mailing.approved_at = datetime.datetime.now()
        mailing.approved_by = request.user.person
        mailing.save()
    else:
        request.user.message_set.create(message=_('Mailing already \
 approved by %(person)s on %(date)s') % {'person': mailing.approved_by, 
        'date': mailing.approved_at})

    return HttpResponseRedirect(reverse(mailing_edit, \
         args=[mailing.id]))

@login_required
def mailing_edit(request, mailing_id=None):
    """mailing edit"""

    access = check_access(request, request.user, 
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    news = NewsItem.objects.all().order_by('-id')[:25]

    if mailing_id:
        mailing = get_object_or_404(Mailing, pk=mailing_id)
        form = MailingForm(instance=mailing, news=news)
    else:
        mailing = None
        form = MailingForm(news=news)


    if request.method == 'POST':
        if mailing_id:
            form = MailingForm(request.POST.copy(), instance=mailing, news=news)
        else:
            form = MailingForm(request.POST.copy(), news=news)

        if form.is_valid():
            mailing = form.save(commit=False)

            if not mailing_id:
                mailing.created_by = request.user.person
            mailing.modified_by = request.user.person
            mailing.save()
            request.user.message_set.create(message=_('Mailing successfully\
 updated'))
            return HttpResponseRedirect(reverse(mailing_edit, \
                args=[mailing.id]))
        else:
            request.user.message_set.create(message=_('Something was wrong in\
 the form you filled. No modification done.') + str(form.errors))

    back = request.META.get('HTTP_REFERER', '/')

    return render(
        request, 'manage/mailing_edit.html', {'mailing': mailing,
            'news': news, 'form': form, 'back': back})

@login_required
def mailing_sendteam(request, mailing_id, testing=True, myself=False):
    """send test maling to the team"""
    return mailing_send(request, mailing_id, testing, myself)

@login_required
def mailing_send(request, mailing_id, testing=True, myself=True):
    """ send mailing"""

    access = check_access(request, request.user, 
                          ['ain7-secretariat'])
    if access:
        return access

    mailing = get_object_or_404(Mailing, pk=mailing_id)

    mailing.send(testing, myself, request)

    return HttpResponseRedirect(reverse(mailing_edit, \
        args=[mailing.id]))

def mailing_view(request, mailing_id):
    """ view mailing in a browser"""

    mailing = get_object_or_404(Mailing, pk=mailing_id)

    html = mailing.build_html_body()

    return render(
        request, 'manage/mailing_view.html', {'html': html})

@login_required
def mailing_export(request, mailing_id):
    """output csv of people without mail"""

    import csv
    from django.http import HttpResponse

    access = check_access(request, request.user, 
                          ['ain7-secretariat'])
    if access:
        return access

    mailing = get_object_or_404(Mailing, pk=mailing_id)

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=mailing_'+str(mailing_id)+'.csv'

    writer = csv.writer(response)

    for per in mailing.nomail_export():
        try:
            writer.writerow([per.first_name.encode('utf-8'), per.last_name.encode('utf-8'), per.ain7member.promo(), per.ain7member.track().encode('utf-8'), per.address()['line1'].encode('utf-8'), per.address()['line2'].encode('utf-8'), per.address()['zip_code'], per.address()['city'].encode('utf-8'), per.address()['country'].encode('utf-8')])
        except Exception:
            pass

    return response

