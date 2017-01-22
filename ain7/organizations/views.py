# -*- coding: utf-8
"""
  ain7/organizations/views.py
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

import datetime

from autocomplete_light import shortcuts as autocomplete_light

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _

from ain7.decorators import access_required, confirmation_required
from ain7.organizations.filters import OrganizationFilter
from ain7.organizations.models import Organization, Office
from ain7.organizations.forms import (
    OrganizationListForm, OfficeListForm,
    )


@access_required(groups=['ain7-membre', 'ain7-secretariat'])
def organization_details(request, organization_id):
    """organization details"""

    organization = get_object_or_404(Organization, pk=organization_id)

    return render(request, 'organizations/organization_details.html', {
        'organization': organization
        }
    )


@access_required(groups=['ain7-membre', 'ain7-secretariat'])
def organization_edit(request, organization_id=None):
    """organization edit data"""

    org = None
    if organization_id:
        org = get_object_or_404(Organization, pk=organization_id)

    OrganizationForm = autocomplete_light.modelform_factory(
        Organization,
        exclude=('modification_of', 'modification_date', 'is_valid')
    )
    form = OrganizationForm(request.POST or None, instance=org)

    if request.method == 'POST' and form.is_valid():

            old_org = None
            user_groups = request.user.person.groups.values_list('group__name',
                flat=True)

            if 'ain7-secretariat' not in user_groups and \
                'ain7-admin' not in user_groups and organization_id:
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
            return redirect(org)

    return render(request, 'organizations/organization_edit.html', {
        'form': form,
        'organization': org,
        'title': _('Organization modification'),
        }
    )


@access_required(groups=['ain7-membre', 'ain7-secretariat'])
def organization_search(request):
    """organization search"""

    organizations = OrganizationFilter(
        request.GET,
        queryset=Organization.objects.all(),
    )

    return render(request, 'organizations/organizations_search.html', {
        'organizations': organizations,
        'nb_org': Organization.objects.valid_organizations().count(),
        'nb_offices': Office.objects.valid_offices().count(),
        }
    )


@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def organization_merge(request, organization_id=None):
    """merge organizations"""

    organization = get_object_or_404(Organization, pk=organization_id)

    # 1er passage : on demande la saisie d'une deuxième organisation
    if request.method == 'GET':
        form = OrganizationListForm()
        return render(request, 'organizations/organization_merge.html', {
            'form': form,
            'organization': organization,
            }
        )

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
                    messages.info(request, message=_('The two\
 organizations are the same. No merging.'))
        messages.error(request, _('Something was wrong in the\
 form you filled. No modification done.'))
        return HttpResponseRedirect('/organizations/%s/merge/' %
            organization_id)


@confirmation_required(
    lambda user_id = None, org1_id = None, org2_id = None:
    str(get_object_or_404(Organization, pk=org2_id)) + _(' replaced by ') + \
    str(get_object_or_404(Organization, pk=org1_id)),
    'organizations/base.html',
    _('Do you REALLY want to have'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def organization_merge_perform(request, org1_id, org2_id):
    """organization effective merge"""

    org1 = get_object_or_404(Organization, pk=org1_id)
    org2 = get_object_or_404(Organization, pk=org2_id)
    org1.merge(org2)
    messages.success(request, message=_('Organizations successfully merged'))
    return redirect(org1)


@confirmation_required(lambda organization_id:
    str(get_object_or_404(Organization, pk=organization_id)), 
    'organizations/base.html',
    _('Do you really want to delete this organization'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def organization_delete(request, organization_id):
    """organization delete"""

    organization = get_object_or_404(Organization, pk=organization_id)
    if organization.is_valid:
        organization.delete()
    else:
        organization.purge()

    messages.success(request, _('Organisation has beenmarked as deleted.'))
    return HttpResponseRedirect(reverse(organization_search))


@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def organization_undelete(request, organization_id, office_id=None):
    """organization delete"""

    organization = get_object_or_404(Organization, pk=organization_id)

    if office_id:
        office = get_object_or_404(
            Office, pk=office_id,
            organization__id=organization_id,
        )
        office.is_valid = True
        office.save()
    else:
        organization.is_valid = True
        organization.save()

    messages.success(request, _('Organisation has beenmarked as restaured.'))
    return redirect(organization)


@access_required(groups=['ain7-ca', 'ain7-secretariat', 'ain7-membre'])
def office_edit(request, organization_id, office_id=None):
    """office edit"""

    organization = get_object_or_404(Organization, id=organization_id)

    office = None
    if office_id:
        office = get_object_or_404(
            Office, id=office_id, organization=organization,
        )

    OfficeForm = autocomplete_light.modelform_factory(
        Office,
        exclude=('old_id','is_valid','is_a_proposal', 'modification_of', 'modification_date', 'organization'),
    )
    form = OfficeForm(request.POST or None, instance=office)

    if request.method == 'POST' and form.is_valid():

        old_office = None
        user_groups = request.user.person.groups.values_list('group__name',
            flat=True)

        if (
            'ain7-secretariat' not in user_groups and
            'ain7-admin' not in user_groups and office_id
        ):
            office.id = None
            office.is_valid = False
            office.save()
            old_office = office
            office = get_object_or_404(Office, pk=office_id)
            form = OfficeForm(request.POST.copy(), instance=office)

        office = form.save(commit=False)
        office.organization = organization
        office.save()

        if old_office:
            office.modification_of = old_office
            office.modification_date = datetime.datetime.now()
            office.save()

        messages.success(request, message=_('Office has been modified.'))

        return redirect(office.organization)

    return render(request, 'organizations/office_edit.html', {
        'form': form,
        'organization': organization,
        'office': office,
        'title': _('Modify an office'),
        }
    )


@confirmation_required(lambda organization_id, office_id=None:
    str(get_object_or_404(Office,pk=office_id)), 'organizations/base.html',
    _('Do you really want to remove this office'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def office_delete(request, organization_id, office_id=None):
    """office delete"""

    office = get_object_or_404(
        Office, pk=office_id,
        organization__id=organization_id,
    )

    if office.is_valid:
        office.delete()
    else:
        office.purge()

    messages.success(request, message=_('Office has marked as deleted.'))
    return redirect(office.organization)


@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def office_merge(request, organization_id, office_id=None):
    """merge offices"""

    office = get_object_or_404(
        Office, pk=office_id,
        organization__id=organization_id
    )

    # 1er passage : on demande la saisie d'une deuxième organisation
    if request.method == 'GET':
        form = OfficeListForm()
        return render(request, 'organizations/office_merge.html', {
            'form': form,
            'office': office,
            }
        )

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
                    messages.error(request, message=_('The two offices\
 are the same. No merging.'))
        messages.error(request, message=_('Something was wrong in the\
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
@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def office_merge_perform(request, organization_id, office1_id, office2_id):
    """merge offices"""

    office1 = get_object_or_404(
        Office, pk=office1_id, organization__id=organization_id,
    )
    office2 = get_object_or_404(
        Office, pk=office2_id, organization__id=organization_id,
    )
    office1.merge(office2)
    messages.success(request, message=_('Office successfully merged'))
    return redirect(office.organization)
