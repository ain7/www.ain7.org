# -*- coding: utf-8
"""
  ain7/organizations/views.py
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

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from ain7.decorators import confirmation_required
from ain7.organizations.models import Organization, Office
from ain7.organizations.forms import OrganizationForm, OfficeForm, \
                              SearchOrganizationForm, \
                              OrganizationListForm, OfficeListForm
from ain7.utils import ain7_render_to_response
from ain7.utils import check_access


@login_required
def organization_details(request, organization_id):
    """organization details"""

    access = check_access(request, request.user,
        ['ain7-membre', 'ain7-secretariat'])
    if access:
        return access

    organization = get_object_or_404(Organization, pk=organization_id)

    return ain7_render_to_response(request, 
         'organizations/organization_details.html',
        {'organization': organization})

def organization_edit(request, organization_id=None):
    """organization edit data"""

    access = check_access(request, request.user,
        ['ain7-membre', 'ain7-secretariat'])
    if access:
        return access

    if organization_id:
        org = get_object_or_404(Organization, pk=organization_id)
        form = OrganizationForm(instance=org)
    else:
        form = OrganizationForm()


    if request.method == 'POST':
        if organization_id:
            form = OrganizationForm(request.POST.copy(), instance=org)
        else:
            form = OrganizationForm(request.POST.copy())

        if form.is_valid():

            old_org = None
            user_groups = request.user.person.groups.values_list('group__name',
                flat=True)

            if not 'ain7-secretariat' in user_groups and \
                not 'ain7-admin' in user_groups and organization_id:
                org.id = None
                org.is_valid = False
                org.save()
                old_org = org
                org = get_object_or_404(Organization, pk=organization_id)
                form = OrganizationForm(request.POST.copy(), instance=org)

            org = form.save()
            if old_org:
                org.modification_of = old_org
                org.modification_date = datetime.datetime.now()
            org.save()
            return HttpResponseRedirect(reverse(organization_details,
                args=[org.id]))

        else:
            request.user.message_set.create(message=_('Something was wrong\
 in the form you filled. No modification done.'))

    return ain7_render_to_response(request, 
         'organizations/office_edit.html',
        {'form': form, 
         'title':_('Organization modification')})


@login_required
def organization_search(request):
    """organization search"""

    access = check_access(request, request.user,
        ['ain7-membre', 'ain7-secretariat'])
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
                raise Http404

    return ain7_render_to_response(request, 
         'organizations/organizations_search.html',
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
            request, 'organizations/organization_merge.html',
            {'form': form, 'organization': organization})

    # 2e passage : sauvegarde, notification et redirection
    if request.method == 'POST':
        form = OrganizationListForm(request.POST.copy())
        if form.is_valid():
            organization2 = form.search()
            if organization2:
                if organization2 != organization:
                    return HttpResponseRedirect(
                    '/organizations/%s/merge/%s/' %
                    (organization2.id, organization_id))
                else:
                    request.user.message_set.create(message=_('The two\
 organizations are the same. No merging.'))
        request.user.message_set.create(message=_('Something was wrong in the\
 form you filled. No modification done.'))
        return HttpResponseRedirect('/organizations/%s/merge/' %
            organization_id)

@confirmation_required(
    lambda user_id = None, org1_id = None, org2_id = None:
    str(get_object_or_404(Organization, pk=org2_id)) + _(' replaced by ') + \
    str(get_object_or_404(Organization, pk=org1_id)),
    'organizations/base.html',
    _('Do you REALLY want to have'))
def organization_merge_perform(request, org1_id, org2_id):
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
    return HttpResponseRedirect('/organizations/%s/' % org1_id)

@confirmation_required(lambda organization_id:
    str(get_object_or_404(Organization, pk=organization_id)), 
    'organizations/base.html',
    _('Do you really want to delete this organization'))
@login_required
def organization_delete(request, organization_id):
    """organization delete"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    organization = get_object_or_404(Organization, pk=organization_id)
    if organization.is_valid:
        organization.delete()
    else:
        organization.purge() 

    request.user.message_set.create(message=_('Organisation has been\
 marked as deleted.'))
    return HttpResponseRedirect(reverse(organization_search))

@login_required
def organization_undelete(request, organization_id, office_id=None):
    """organization delete"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    organization = get_object_or_404(Organization, pk=organization_id)

    if office_id:
        office = get_object_or_404(Office, pk=office_id, 
           organization__id=organization_id)
        office.is_valid = True
        office.save()
    else:
        organization.is_valid = True
        organization.save()

    request.user.message_set.create(message=_('Organisation has been\
 marked as restaured.'))
    return HttpResponseRedirect(reverse(organization_details, 
        args=[organization_id]))

@login_required
def office_edit(request, organization_id, office_id=None):
    """office edit"""

    access = check_access(request, request.user,
        ['ain7-membre', 'ain7-secretariat'])
    if access:
        return access

    form = OfficeForm()

    organization = get_object_or_404(Organization, id=organization_id)

    if office_id:
        office = get_object_or_404(Office, id=office_id, 
            organization=organization)
        form = OfficeForm(instance=office)

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        form = OfficeForm(request.POST.copy())
        if office_id:
            form = OfficeForm(request.POST.copy(), instance=office)
        if form.is_valid():
            off = form.save(commit=False)
            off.organization = organization
            off.save()
            request.user.message_set.create(message=_('Office has been\
 modified.'))

            return HttpResponseRedirect(reverse(organization_details,
                args=[off.organization.id]))

        else:
            request.user.message_set.create(message=_('Something was wrong in\
 the form you filled. No modification done.'))

    return ain7_render_to_response(request, 
         'organizations/office_edit.html',
        {'form': form, 'title': _('Modify an office')})

@confirmation_required(lambda organization_id, office_id=None:
    str(get_object_or_404(Office,pk=office_id)), 'organizations/base.html',
    _('Do you really want to remove this office'))
@login_required
def office_delete(request, organization_id, office_id=None):
    """office delete"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    office = get_object_or_404(Office, pk=office_id, 
        organization__id=organization_id)

    if office.is_valid:
        office.delete()
    else:
        office.purge()

    request.user.message_set.create(message=_('Office has been marked\
 as deleted.'))
    return HttpResponseRedirect(reverse(organization_details,
         args=[office.organization.id]))

@login_required
def office_merge(request, organization_id, office_id=None):
    """merge offices"""

    access = check_access(request, request.user,
                          ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    office = get_object_or_404(Office, pk=office_id, 
        organization__id=organization_id)

    # 1er passage : on demande la saisie d'une deuxième organisation
    if request.method == 'GET':
        form = OfficeListForm()
        return ain7_render_to_response(
            request, 'organizations/office_merge.html',
            {'form':form, 'office':office})

    # 2e passage : sauvegarde, notification et redirection
    if request.method == 'POST':
        form = OfficeListForm(request.POST.copy())
        if form.is_valid():
            office2 = form.search()
            if office2:
                if office2 != office:
                    return HttpResponseRedirect(
                        '/organizations/%s/offices/%s/merge/%s/'
                        % (office.organization.id, office2.id, office_id))
                else:
                    request.user.message_set.create(message=_('The two offices\
 are the same. No merging.'))
        request.user.message_set.create(message=_('Something was wrong in the\
 form you filled. No modification done.')+str(form.errors))
        return HttpResponseRedirect('/organizations/%s/offices/%s/merge/' % \
            (office.organization.id, office_id))

@confirmation_required(
    lambda user_id = None, organization_id = None, 
        office1_id = None, office2_id = None:
    unicode(get_object_or_404(Office, pk=office2_id)) + _(' replaced by ') + \
    unicode(get_object_or_404(Office, pk=office1_id)),
    'organizations/base.html',
    _('Do you REALLY want to have'))
def office_merge_perform(request, organization_id, office1_id, office2_id):
    """merge offices"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    office1 = get_object_or_404(Office, pk=office1_id, 
        organization__id=organization_id)
    office2 = get_object_or_404(Office, pk=office2_id, 
        organization__id=organization_id)
    office1.merge(office2)
    request.user.message_set.create(message=_('Offices successfully merged'))
    return HttpResponseRedirect('/organizations/%s/' % office1.organization.id)

