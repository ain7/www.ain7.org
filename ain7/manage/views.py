# -*- coding: utf-8
"""
  ain7/manage/views.py
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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.core.paginator import Paginator, InvalidPage
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from ain7.utils import ain7_render_to_response, ain7_generic_edit
from ain7.utils import ain7_generic_delete, check_access
from ain7.decorators import confirmation_required
from ain7.emploi.models import Organization, Office, ActivityField
from ain7.emploi.models import OrganizationProposal, OfficeProposal
from ain7.emploi.forms import OrganizationForm, OfficeForm, OfficeFormNoOrg
from ain7.manage.models import *
from ain7.manage.forms import *
from ain7.annuaire.forms import PersonForm, PhoneNumberForm
from ain7.annuaire.forms import AddressForm, EmailForm
from ain7.annuaire.models import Person
from ain7.search_engine.models import *
from ain7.search_engine.utils import *
from ain7.search_engine.views import *


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

    return ain7_render_to_response(request, 'manage/default.html',
        {'notifications': Notification.objects.all()})

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
    paginator = Paginator(Group.objects.none(), nb_results_by_page)
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
                raise http.Http404

    return ain7_render_to_response(request, 'manage/users_search.html',
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
def user_details(request, user_id):
    """user details"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    user = get_object_or_404(User, pk=user_id)
    return ain7_render_to_response(
        request, 'manage/user_details.html', {'this_user': user})

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
    return ain7_render_to_response(request, 'manage/edit_form.html',
        {'action_title': _('Register new user'), 'back': back, 'form': form})

@login_required 
def user_edit(request, user_id=None): 
    """edit user"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access
 
    person = get_object_or_404(Person, pk=user_id) 
    return ain7_render_to_response(request, 'manage/user_edit.html',
                                   {'person': person}) 

@login_required
def user_person_edit(request, user_id=None):
    """edit person"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access
 
    person = None
    if user_id:
        person = Person.objects.get(user=user_id)
    return ain7_generic_edit(
        request, person, PersonForm, {'user': person.user},
        'manage/edit_form.html',
        {'action_title': _("Modification of personal data for"),
         'person': person, 
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/manage/users/%s/edit/' % (person.user.id),
        _("Modifications have been successfully saved."))

@login_required
def organizations_search(request):
    """organization search"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access
 
    form = SearchOrganizationForm()
    nb_results_by_page = 25
    organizations = False
    paginator = Paginator(Organization.objects.none(), nb_results_by_page)
    page = 1
    if request.GET.has_key('name') or \
       request.GET.has_key('activity_field') or \
       request.GET.has_key('activity_code'):
        form = SearchOrganizationForm(request.GET)
        if form.is_valid():
            criteria = form.criteria()
            organizations = form.search(criteria)
            request.session['filter'] = criteria
            paginator = Paginator(organizations, nb_results_by_page)
            try:
                page = int(request.GET.get('page', '1'))
                organizations = paginator.page(page).object_list
            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'manage/organizations_search.html',
        {'form': form, 'organizations': organizations,
         'nb_org': Organization.objects.valid_organizations().count(),
         'nb_offices': Office.objects.valid_offices().count(),
         'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page, 'pages': paginator.num_pages,
         'next_page': page + 1, 'previous_page': page - 1,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits' : paginator.count})

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
        return ain7_render_to_response(request,
            'manage/organizations_adv_search.html',
            dict_for_filter(request, filtr.id))
    else:
        return ain7_render_to_response(request,
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
            raise http.Http404

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

    return ain7_render_to_response(request,
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
        return ain7_render_to_response(request,
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
    return ain7_render_to_response(
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
def organization_edit(request, organization_id=None):
    """edit organization"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    organization = None
    if organization_id:
        organization = get_object_or_404(Organization, pk=organization_id)
        activity_field = organization.activity_field
        if activity_field:
            activity_field = organization.activity_field.pk
        form = OrganizationForm(
            {'name': organization.name, 'size': organization.size,
             'employment_agency': organization.employment_agency,
             'activity_field': activity_field,
             'short_description': organization.short_description,
             'long_description': organization.long_description })
        action_title = _('Edit an organization')
    else:
        form = OrganizationForm()
        action_title = _('Register an organization')

    if request.method == 'POST':
        form = OrganizationForm(request.POST.copy())
        if form.is_valid():
            org = form.save(request.user, is_a_proposal=False, \
                            organization=organization)
            if organization:
                msg = _('Organization successfully modified')
            else:
                msg = _('Organization successfully validated')
            request.user.message_set.create(message=msg)
            return HttpResponseRedirect('/manage/organizations/%s/' % org.id)
        else:
            request.user.message_set.create(message=_('Something was wrong in\
 the form you filled. No organization registered.'))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request,
        'manage/organization_edit.html',
        {'action_title': action_title, 'form': form, 'back': back})


@login_required
def organization_details(request, organization_id):
    """organization details"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    organization = get_object_or_404(Organization, pk=organization_id)
    return ain7_render_to_response(request, 'manage/organization_details.html',
        {'organization': organization})

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
    if not filter_id and not se.unregistered_filters(request.user.person):
        request.user.message_set.create(message=
            _("You have to make a search before using csv export."))
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    if filter_id:
        search_filter = get_object_or_404(SearchFilter, id=filter_id)
    else:
        search_filter = se.unregistered_filters(request.user.person)
    return se_export_csv(request, search_filter.search(), search_engine,
        'manage/edit_form.html')

@confirmation_required(
    lambda user_id = None,
    organization_id = None: str(get_object_or_404(Organization,
                                 pk=organization_id)),
    'manage/base.html',
    _('Do you REALLY want to delete this organization'))
def organization_delete(request, organization_id):
    """delete organization"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    organization = get_object_or_404(Organization, pk=organization_id)
    organization.delete()
    request.user.message_set.create(
        message=_('Organization successfully removed'))
    return HttpResponseRedirect('/manage/')


@login_required
def organization_merge(request, organization_id=None):
    """merge organizations"""

    access = check_access(request, request.user,
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    organization = get_object_or_404(Organization, pk=organization_id)

    # 1er passage : on demande la saisie d'une deuxième organisation
    if request.method == 'GET':
        form = OrganizationListForm()
        return ain7_render_to_response(
            request, 'manage/organization_merge.html',
            {'form': form, 'organization': organization})

    # 2e passage : sauvegarde, notification et redirection
    if request.method == 'POST':
        form = OrganizationListForm(request.POST.copy())
        if form.is_valid():
            organization2 = form.search()
            if organization2:
                if organization2 != organization:
                    return HttpResponseRedirect(
                    '/manage/organizations/%s/merge/%s/' % 
                    (organization2.id, organization_id))
                else:
                    request.user.message_set.create(message=_('The two\
 organizations are the same. No merging.'))
        request.user.message_set.create(message=_('Something was wrong in the\
 form you filled. No modification done.'))
        return HttpResponseRedirect('/manage/organizations/%s/merge/' %
            organization_id)
        

@confirmation_required(
    lambda user_id = None, org1_id = None, org2_id = None:
    str(get_object_or_404(Organization, pk=org2_id)) + _(' replaced by ') + \
    str(get_object_or_404(Organization, pk=org1_id)),
    'manage/base.html',
    _('Do you REALLY want to have'))
def organization_do_merge(request, org1_id, org2_id):
    """organization effective merge"""

    access = check_access(request, request.user, 
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    org1 = get_object_or_404(Organization, pk=org1_id)
    org2 = get_object_or_404(Organization, pk=org2_id)
    org1.merge(org2)
    request.user.message_set.create(
        message=_('Organizations successfully merged'))
    return HttpResponseRedirect('/manage/organizations/%s/' % org1_id)

@login_required
def organization_register_proposal(request, proposal_id=None):
    """register an organization proposal"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    if not proposal_id:
        return HttpResponseRedirect('/manage/')
    
    proposal = get_object_or_404(OrganizationProposal, pk=proposal_id)
    form = OrganizationForm(
        {'name': proposal.modified.name,
         'size': proposal.modified.size,
         'employment_agency': proposal.modified.employment_agency,
         'short_description': proposal.modified.short_description, 
         'long_description': proposal.modified.long_description })
    
    if proposal.modified.activity_field:
        form = OrganizationForm(
        {'name': proposal.modified.name,
         'size': proposal.modified.size,
         'employment_agency': proposal.modified.employment_agency,
         'short_description': proposal.modified.short_description, 
         'activity_field': proposal.modified.activity_field.pk,
         'long_description': proposal.modified.long_description })

    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            org = proposal.modified
            org.name = form.cleaned_data['name']
            org.employment_agency = form.cleaned_data['employment_agency']
            org.size = form.cleaned_data['size']
            if form.cleaned_data['activity_field']:
                org.activity_field = ActivityField.objects.get(
                     pk=form.cleaned_data['activity_field'])
            org.short_description = form.cleaned_data['short_description']
            org.long_description = form.cleaned_data['long_description']
            org.is_a_proposal = False
            org.is_valid = True
            org.logged_save(request.user.person)
            # on supprime la notification et la proposition
            notification = Notification.objects.get(
                organization_proposal=proposal )
            if notification:
                notification.delete()
            proposal.delete()
            request.user.message_set.create(
                    message=_('Organization successfully validated'))
            return HttpResponseRedirect('/manage/')
        else:
            request.user.message_set.create(message=_('Something was wrong in\
 the form you filled. No organization registered.') \
                    + str(form.errors))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request,
        'manage/proposal_register.html',
        {'action_title': _('Validate a new organization'),
         'form': form, 'back': back})

@login_required
def organization_edit_proposal(request, proposal_id=None):
    """edit organization proposal"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    if not proposal_id:
        return HttpResponseRedirect('/manage/')
    
    proposal = get_object_or_404(OrganizationProposal, pk=proposal_id)
    activity_field = proposal.modified.activity_field
    if activity_field:
        activity_field = proposal.modified.activity_field.pk
    form = OrganizationForm(
        {'name': proposal.modified.name,
         'size': proposal.modified.size,
         'employment_agency': proposal.modified.employment_agency,
         'activity_field': activity_field,
         'short_description': proposal.modified.short_description, 
         'long_description': proposal.modified.long_description })

    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save(user=request.user,
                                     is_a_proposal=False,
                                     organization=proposal.original)
            # on supprime la notification et la proposition
            notification = Notification.objects.get(
                organization_proposal=proposal )
            notification.delete()
            proposal.modified.really_delete()
            proposal.delete()
            request.user.message_set.create(message=_('Organization\
 successfully modified'))
            return HttpResponseRedirect('/manage/')
        else:
            request.user.message_set.create(message=_('Something was wrong\
 in the form you filled. No modification done.'))
            
    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request,
        'manage/proposal_edit_organization.html',
        {'form': form, 'original': proposal.original, 'back': back})

@login_required
def organization_delete_proposal(request, proposal_id=None):
    """organization proposal delete"""

    access = check_access(request, request.user,
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    proposal = get_object_or_404(OrganizationProposal, pk=proposal_id)
    org = proposal.original
    back = request.META.get('HTTP_REFERER', '/')
    if request.method == 'POST':
        org.delete()
        notification = Notification.objects.get(organization_proposal=proposal)
        notification.delete()
        request.user.message_set.create(
            message=_('Organization successfully removed'))
        return HttpResponseRedirect('/manage/')
    return ain7_render_to_response(request, 'manage/organization_details.html',
        {'organization': org, 'back': back, 'action': 'propose_deletion'})

@login_required
def office_edit(request, office_id=None, organization_id=None):
    """edit office"""

    access = check_access(request, request.user,
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    if office_id:
        return ain7_generic_edit(
            request, get_object_or_404(Office, pk=office_id),
            OfficeForm, {'is_a_proposal': False, 'is_valid': True},
            'manage/organization_edit.html',
            {'action_title': _('Edit an office'),
             'back': request.META.get('HTTP_REFERER', '/')}, {},
            '/manage/offices/%s/' % office_id,
            _('Office successfully modified'))
    else:
        return ain7_generic_edit(
            request, None, OfficeForm,
            {'is_a_proposal': False, 'is_valid': True},
            'manage/organization_edit.html',
            {'action_title': _('Register an office'),
             'back': request.META.get('HTTP_REFERER', '/')}, {},
            '/manage/offices/$objid/', _('Office successfully created'))

@login_required
def office_details(request, office_id):
    """office details"""

    access = check_access(request, request.user,
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    office = get_object_or_404(Office, pk=office_id)
    return ain7_render_to_response(request, 'manage/office_details.html',
        {'office': office})


@confirmation_required(
    lambda user_id=None,
    office_id = None: str(get_object_or_404(Office, pk = office_id)),
    'manage/base.html', _('Do you REALLY want to delete this office'))
@login_required
def office_delete(request, office_id):
    """office delete"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    office = get_object_or_404(Office, pk=office_id)
    organization_id = office.organization.id
    return ain7_generic_delete(request,
        get_object_or_404(Office, pk=office_id),
        '/manage/organizations/%s/' % organization_id,
        _('Office successfully removed'))


@login_required
def office_merge(request, office_id=None):
    """merge offices"""

    access = check_access(request, request.user,
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    office = get_object_or_404(Office, pk=office_id)

    # 1er passage : on demande la saisie d'une deuxième organisation
    if request.method == 'GET':
        form = OfficeListForm()
        return ain7_render_to_response(
            request, 'manage/office_merge.html',
            {'form':form, 'office':office})

    # 2e passage : sauvegarde, notification et redirection
    if request.method == 'POST':
        form = OfficeListForm(request.POST.copy())
        if form.is_valid():
            office2 = form.search()
            if office2:
                if office2 != office:
                    return HttpResponseRedirect('/manage/offices/%s/merge/%s/'
                            % (office2.id, office_id))
                else:
                    request.user.message_set.create(message=_('The two offices\
 are the same. No merging.'))
        request.user.message_set.create(message=_('Something was wrong in the\
 form you filled. No modification done.')+str(form.errors))
        return HttpResponseRedirect('/manage/offices/%s/merge/' % office_id)

@confirmation_required(
    lambda user_id = None, office1_id = None, office2_id = None:
    unicode(get_object_or_404(Office, pk=office2_id)) + _(' replaced by ') + \
    unicode(get_object_or_404(Office, pk=office1_id)),
    'manage/base.html',
    _('Do you REALLY want to have'))
def office_do_merge(request, office1_id, office2_id):
    """merge offices"""

    access = check_access(request, request.user, 
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    office1 = get_object_or_404(Office, pk=office1_id)
    office2 = get_object_or_404(Office, pk=office2_id)
    office1.merge(office2)
    request.user.message_set.create(message=_('Offices successfully merged'))
    return HttpResponseRedirect('/manage/offices/%s/' % office1_id)


@login_required
def office_register_proposal(request, proposal_id=None):
    """register office proposal"""

    access = check_access(request, request.user, 
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    if not proposal_id:
        return HttpResponseRedirect('/manage/')
    
    proposal = get_object_or_404(OfficeProposal, pk=proposal_id)
    form = OfficeForm(instance=proposal.modified)

    if request.method == 'POST':
        form = OfficeForm(request.POST.copy(), instance=proposal.modified)
        if form.is_valid():
            office = proposal.modified
            office.organization = form.cleaned_data['organization']
            office.name = form.cleaned_data['name']
            office.line1 = form.cleaned_data['line1']
            office.line2 = form.cleaned_data['line2']
            office.zip_code = form.cleaned_data['zip_code']
            office.city = form.cleaned_data['city']
            office.country = form.cleaned_data['country']
            office.phone_number = form.cleaned_data['phone_number']
            office.web_site = form.cleaned_data['web_site']
            office.is_a_proposal = False
            office.is_valid = True
            office = form.save()
            # on supprime la notification et la proposition
            notification = Notification.objects.get(office_proposal=proposal)
            if notification:
                notification.delete()
            proposal.delete()
            request.user.message_set.create(message=_('Office successfully\
 validated'))
            return HttpResponseRedirect('/manage/')
        else:
            request.user.message_set.create(message=_('Something was wrong in\
 the form you filled. No modification done.') + str(form.errors))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request,
        'manage/proposal_register.html',
        {'action_title': _('Validate a new office'),
         'form': form, 'back': back})

@login_required
def office_edit_proposal(request, proposal_id=None):
    """office edit proposal"""

    access = check_access(request, request.user, 
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    if not proposal_id:
        return HttpResponseRedirect('/manage/')
    
    proposal = get_object_or_404(OfficeProposal, pk=proposal_id)
    init_dict = {'name': proposal.modified.name,
                'line1': proposal.modified.line1,
                'line2': proposal.modified.line2,
                'zip_code': proposal.modified.zip_code,
                'city': proposal.modified.city,
                'country': proposal.modified.country,
                'phone_number': proposal.modified.phone_number,
                'web_site': proposal.modified.web_site }
    form = OfficeFormNoOrg(init_dict)

    if request.method == 'POST':
        form = OfficeFormNoOrg(request.POST)
        if form.is_valid():
            proposal.original.name = form.cleaned_data['name']
            proposal.original.line1 = form.cleaned_data['line1']
            proposal.original.line2 = form.cleaned_data['line2']
            proposal.original.zip_code = form.cleaned_data['zip_code']
            proposal.original.city = form.cleaned_data['city']
            proposal.original.country = form.cleaned_data['country']
            proposal.original.phone_number = form.cleaned_data['phone_number']
            proposal.original.web_site = form.cleaned_data['web_site']
            proposal.original.save()
            # on supprime la notification et la proposition
            notification = Notification.objects.get( office_proposal=proposal )
            notification.delete()
            proposal.modified.really_delete()
            proposal.delete()
            request.user.message_set.create(message=_('Office successfully\
 modified'))
            return HttpResponseRedirect('/manage/')
        else:
            request.user.message_set.create(message=_('Something was wrong in\
 the form you filled. No modification done.'))
            
    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request,
        'manage/proposal_edit_office.html',
        {'form': form, 'original': proposal.original, 'back': back})

@login_required
def office_delete_proposal(request, proposal_id=None):
    """office delete proposal"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    proposal = get_object_or_404(OfficeProposal, pk=proposal_id)
    office = proposal.original
    back = request.META.get('HTTP_REFERER', '/')
    if request.method == 'POST':
        return HttpResponseRedirect('/manage/offices/%d/delete/'% office.id)
    return ain7_render_to_response(request, 'manage/office_details.html',
        {'office': office, 'back': back, 'action': 'propose_deletion'})

@login_required
def roles_index(request):
    """roles index"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access

    roles = Group.objects.all()

    return ain7_render_to_response(request, 'manage/role_index.html',
        {'roles': roles, 'request': request})

@login_required
def role_register(request):
    """new role register"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access

    form = NewRoleForm()

    if request.method == 'POST':
        form = NewRoleForm(request.POST)
        if form.is_valid():

            if not Group.objects.filter(\
                name=form.cleaned_data['name']).count() == 0:
                request.user.message_set.create(message=_("Several roles have\
 the same name. Please choose another one"))

            else:
                new_role = form.save()
                request.user.message_set.create(
                    message=_("New role successfully created"))
                return HttpResponseRedirect(
                    '/manage/roles/%s/' % (new_role.name))
        else:
            request.user.message_set.create(message=_("Something was wrong in\
 the form you filled. No modification done."))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 'manage/edit_form.html',
        {'action_title': _('Register new role'), 'back': back, 'form': form})


@login_required
def role_details(request, role_id):
    """role details"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access

    group = get_object_or_404(Group, name=role_id)
    return ain7_render_to_response(request, 'manage/role_details.html',
                                   {'role': group})

@login_required
def role_member_add(request, role_id):
    """add a new member to the role"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access

    group = get_object_or_404(Group, name=role_id)

    form = MemberRoleForm()

    if request.method == 'POST':
        form = MemberRoleForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=form.cleaned_data['username'])
            user.groups.add(group)
            request.user.message_set.create(message=_('User added to role'))
            return HttpResponseRedirect('/manage/roles/%s/' % role_id)
        else:
            request.user.message_set.create(message=_('User is not correct'))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request, 'manage/role_user_add.html',
                            {'form': form, 'role': group, 'back': back})

@login_required
def role_member_delete(request, role_id, member_id):
    """delete member role"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access

    group = get_object_or_404(Group, name=role_id)
    member = get_object_or_404(User, pk=member_id)

    member.groups.remove(group)

    request.user.message_set.create(message=_('Member removed from role'))

    return HttpResponseRedirect('/manage/roles/%s/' % role_id)

@login_required
def notification_add(request):
    """add a notification"""

    access = check_access(request, request.user, 
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    return ain7_generic_edit(
        request, None, NotificationForm,
        {'organization_proposal': None, 'office_proposal': None,
         'job_proposal': None},
        'manage/notification.html',
        {'action_title': _('Add a new notification'),
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/manage/', _('Notification successfully created'))

@login_required
def notification_edit(request, notif_id):
    """edit notification"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    return ain7_generic_edit(
        request, get_object_or_404(Notification, pk=notif_id),
        NotificationForm,
        {'organization_proposal': None, 'office_proposal': None,
         'job_proposal': None},
        'manage/notification.html',
        {'action_title': _("Modification of the notification"),
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/manage/', _("Modifications have been successfully saved."))

@confirmation_required(
    lambda user_id = None,
    notif_id = None: str(get_object_or_404(Notification, pk = notif_id)),
    'manage/base.html',
    _('Do you REALLY want to delete the notification'))
def notification_delete(request, notif_id):
    """delete notification"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    notif = get_object_or_404(Notification, pk=notif_id)
    notif.delete()
    request.user.message_set.create(
        message=_("The notification has been successfully removed."))
    return HttpResponseRedirect('/manage/')

# Adresses
@login_required
def user_address_edit(request, user_id=None, address_id=None):
    """edit user address"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
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
        'manage/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/manage/users/%s/edit/#address' % user_id, msg_done)

@confirmation_required(lambda user_id=None, address_id=None : 
    str(get_object_or_404(Address, pk=address_id)), 
    'manage/base.html', _('Do you really want to delete your address'))
@login_required
def user_address_delete(request, user_id=None, address_id=None):
    """delete user address"""

    access = check_access(request, request.user, 
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    return ain7_generic_delete(request,
        get_object_or_404(Address, pk=address_id),
        '/manage/users/%s/edit/#address' % user_id,
        _('Address successfully deleted.'))

# Numeros de telephone
@login_required
def user_phone_edit(request, user_id=None, phone_id=None):
    """user phone edit"""

    access = check_access(request, request.user, 
        ['ain7-ca', 'ain7-secretariat'])
    if access:
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
        'manage/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/manage/users/%s/edit/#phone' % user_id, msg_done)

@confirmation_required(lambda user_id=None, phone_id=None : 
     str(get_object_or_404(PhoneNumber, pk=phone_id)), 'manage/base.html', 
     _('Do you really want to delete your phone number'))
@login_required
def user_phone_delete(request, user_id=None, phone_id=None):
    """user phone delete"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    return ain7_generic_delete(request,
        get_object_or_404(PhoneNumber, pk=phone_id),
        '/manage/users/%s/edit/#phone' % user_id,
        _('Phone number successfully deleted.'))

# Adresses de courriel
@login_required
def user_email_edit(request, user_id=None, email_id=None):
    """user email edit"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
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
        'manage/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/manage/users/%s/edit/#email' % user_id, msgDone)

@confirmation_required(lambda user_id=None, email_id=None : 
    str(get_object_or_404(Email, pk=email_id)), 'manage/base.html', 
    _('Do you really want to delete your email address'))
@login_required
def user_email_delete(request, user_id=None, email_id=None):
    """user email delete"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    return ain7_generic_delete(request, get_object_or_404(Email, pk=email_id),
                               '/manage/users/%s/edit/#email' % user_id,
                               _('Email address successfully deleted.'))

@login_required
def nationality_add(request):
    """add nationality"""

    access = check_access(request, request.user, 
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    form = NewCountryForm()

    if request.method == 'POST':
        form = NewCountryForm(request.POST)
        if form.is_valid():

            if not Country.objects.filter(\
                name=form.cleaned_data['name']).count() == 0:
                request.user.message_set.create(message=_("Several countries\
 have the same name. Please choose another one"))

            else:
                new_role = form.save()
                request.user.message_set.create(
                    message=_("New country successfully created"))
                return ain7_render_to_response(request, 
                       'pages/frame_message.html', {})

        else:
            request.user.message_set.create(message=_("Something was wrong in\
 the form you filled. No modification done."))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 'pages/frame_edit_form.html',
        {'action_title': _('Register new country'), 'back': back, 'form': form})

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
        raise http.Http404

    return ain7_render_to_response(request, 'manage/errors_index.html',
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
    """error details"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat', 'ain7-devel'])
    if access:
        return access

    error = get_object_or_404(PortalError, pk=error_id)
    return ain7_render_to_response(
        request, 'manage/error_details.html', {'error': error})

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
        raise http.Http404

    return ain7_render_to_response(request, 'manage/payments_index.html',
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

    return ain7_render_to_response(
        request, 'manage/payments_index.html', {'payment_list': payments_list})

@login_required
def payment_details(request, payment_id):
    """payment details"""

    access = check_access(request, request.user, 
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    payment = get_object_or_404(Payment, pk=payment_id)

    return ain7_render_to_response(
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
            return HttpResponseRedirect(reverse(payment_details, args=[payment.id]))
        else:
            request.user.message_set.create(message=_('Something was wrong in\
 the form you filled. No modification done.') + str(form.errors))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(
        request, 'manage/payment_edit.html', {'payment': payment,
            'form': form, 'back': back})

@login_required
def payments_deposit_index(request):
    """payment deposit index"""

    access = check_access(request, request.user, 
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    return ain7_render_to_response(
        request, 'manage/payments_deposit_index.html', {})

@login_required
def payments_deposit(request, deposit_id):
    """payment deposit"""

    access = check_access(request, request.user, 
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    deposits = Payment.objects.filter(type=deposit_id, deposited__isnull=True,\
        validated=True).order_by('id')

    try:
        last_deposit_id = Payment.objects.filter(type=deposit_id, \
            deposited__isnull=True, validated=True).latest('id').id
    except Payment.DoesNotExist:
        request.user.message_set.create(message=_('No payment to deposit'))
        return HttpResponseRedirect(reverse(payments_deposit_index))

    return ain7_render_to_response(
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

    for deposit in Payment.objects.filter(type=deposit_id,\
        deposited__isnull=True, validated=True):
        deposit.deposited = datetime.datetime.now()
        deposit.save()

    request.user.message_set.create(message=_('Payments marked as deposited'))
    return HttpResponseRedirect(reverse(payments_deposit_index))

