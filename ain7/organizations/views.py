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

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from ain7.decorators import confirmation_required
from ain7.annuaire.models import Person
from ain7.emploi.models import Organization, OrganizationProposal, Office, \
                               OfficeProposal
from ain7.organizations.forms import OrganizationForm, OfficeForm, \
                              OfficeFormNoOrg, SearchOrganizationForm, \
                              OrganizationListForm, OfficeListForm
from ain7.manage.models import Notification
from ain7.utils import ain7_render_to_response
from ain7.utils import ain7_generic_delete, check_access


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
            return HttpResponseRedirect('/organizations/%s/' % org.id)
        else:
            request.user.message_set.create(message=_('Something was wrong in\
 the form you filled. No organization registered.'))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request,
        'organizations/organization_edit.html',
        {'action_title': action_title, 'form': form, 
         'organization': organization, 'back': back})

def organization_edit_data(request, organization_id=None):
    """organization edit data"""

    access = check_access(request, request.user,
        ['ain7-membre', 'ain7-secretariat'])
    if access:
        return access

    org = get_object_or_404(Organization, pk=organization_id)
    person = get_object_or_404(Person, user=request.user.id)

    if request.method == 'GET':
        activity_field = None
        if org.activity_field:
            activity_field = org.activity_field.pk
        form = OrganizationForm(
            {'name':org.name, 'size':org.size,
             'employment_agency':org.employment_agency,
             'activity_field': activity_field,
             'short_description':org.short_description,
             'long_description':org.long_description})
        return ain7_render_to_response(request, 'organizations/office_edit.html',
            {'form': form, 
             'title':_('Proposition of organization modification')})

    if request.method == 'POST':
        form = OrganizationForm(request.POST.copy())
        if form.is_valid():
            # create the OrganizationProposal
            modified_org = form.save(request.user, is_a_proposal=True)
            orgprop = OrganizationProposal(original = org,
                modified = modified_org, author = person, action = 1)
            orgprop.logged_save(person)
            # create the notification
            notif = Notification(details="", organization_proposal=orgprop,
                title=_('Proposal for modifying an organization'))
            notif.logged_save(person)
            request.user.message_set.create(message=_('Your proposal for\
 modifying an organization has been sent to moderators.'))
        else:
            request.user.message_set.create(message=_('Something was wrong\
 in the form you filled. No modification done.'))
            return ain7_render_to_response(request,
                'organizations/office_edit.html',
                {'form': form,
                 'title': _('Proposition of organization modification')})
        return HttpResponseRedirect('/organizations/%s/edit/' % org.id)

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

    return ain7_render_to_response(request, 'organizations/organizations_search.html',
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
    return HttpResponseRedirect('/manage/organizations/%s/' % org1_id)

@login_required
def organization_proposal_register(request, proposal_id=None):
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
            org.activity_field = form.cleaned_data['activity_field']
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
        'organizations/proposal_register.html',
        {'action_title': _('Validate a new organization'),
         'form': form, 'back': back})

@login_required
def organization_proposal_edit(request, proposal_id=None):
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
        'organizations/proposal_edit_organization.html',
        {'form': form, 'original': proposal.original, 'back': back})

@login_required
def organization_proposal_delete(request, proposal_id=None):
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
    return ain7_render_to_response(request, 'organizations/organization_details.html',
        {'organization': org, 'back': back, 'action': 'propose_deletion'})

#@confirmation_required(lambda organization_id:
#    str(get_object_or_404(Organization, pk=organization_id)), 
#    'organizations/base.html',
#    _('Do you really want to propose the deletion of this organization'))
@login_required
def organization_delete(request, organization_id):
    """organization delete"""

    access = check_access(request, request.user,
        ['ain7-membre', 'ain7-secretariat'])
    if access:
        return access

    org = get_object_or_404(Organization, pk=organization_id)
    person = get_object_or_404(Person, user=request.user.id)
    orgprop = OrganizationProposal(original = org,
        modified = None, author = person, action = 2)
    orgprop.logged_save(person)
    # create the notification
    notif = Notification(details="", organization_proposal=orgprop,
                         title=_('Proposal for deleting an organization'))
    notif.logged_save(person)
    request.user.message_set.create(message=_('Your proposal for deleting an\
 organization has been sent to moderators.'))
    return HttpResponseRedirect(reverse(index))

@login_required
def organization_add(request):
    """organization add"""

    access = check_access(request, request.user,
        ['ain7-membre', 'ain7-secretariat'])
    if access:
        return access

    person = get_object_or_404(Person, user=request.user.id)

    header_msg = _('An organization (for instance EDF) is composed by offices\
 (for instance EDF Cornouaille). If you just want to add an office, then <a\
 href=\"%s\">modify the organization</a>.') % '/emploi/organization/edit/'

    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        form = OrganizationForm()
        return ain7_render_to_response(request, 'organizations/office_edit.html',
            {'form': form, 'title': _('Creation of an organization'),
             'header_msg': header_msg})

    # 2e passage : sauvegarde, notification et redirection
    if request.method == 'POST':
        form = OrganizationForm(request.POST.copy())
        if form.is_valid():
            # create the OrganizationProposal
            modified_org = form.save(request.user, is_a_proposal=True)
            orgprop = OrganizationProposal(original = None,
                modified = modified_org, author = person, action = 0)
            orgprop.logged_save(person)
            # create the notification
            notif = Notification(details="", organization_proposal=orgprop,
                title=_('Organization added'))
            notif.logged_save(person)
            request.user.message_set.create(message=_('Organization\
 successfully created. To add an office to it, modify it.'))
            return HttpResponseRedirect(reverse(organization_details,
                args=[modified_org.id]))
        else:
            request.user.message_set.create(message=_('Something was wrong\
 in the form you filled. No modification done.'))
            return ain7_render_to_response(request,
                'organizations/office_edit.html', {'form': form,
                'title': _('Creation of an organization'),
                'header_msg': header_msg})
        return HttpResponseRedirect(reverse(index))

@login_required
def office_details(request, office_id):
    """office details"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    office = get_object_or_404(Office, pk=office_id)
    return ain7_render_to_response(request, 'organizations/office_details.html',
        {'office': office})

login_required
def office_edit(request, organization_id, office_id=None):
    """office edit"""

    access = check_access(request, request.user,
        ['ain7-membre', 'ain7-secretariat'])
    if access:
        return access

    form = OfficeFormNoOrg()

    person = get_object_or_404(Person, user=request.user.id)

    if office_id:
        office = get_object_or_404(Office, pk=office_id)
        form = OfficeFormNoOrg(instance = office)

    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        return ain7_render_to_response(request, 'organizations/office_edit.html',
            {'form': form, 'title': _('Modify an office')})

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        form = OfficeFormNoOrg(request.POST.copy())
        if form.is_valid():
            modified_office = Office()
            modified_office.organization = office.organization
            modified_office.name = form.cleaned_data['name']
            modified_office.line1 = form.cleaned_data['line1']
            modified_office.line2 = form.cleaned_data['line2']
            modified_office.zip_code = form.cleaned_data['zip_code']
            modified_office.city = form.cleaned_data['city']
            modified_office.phone_number = form.cleaned_data['phone_number']
            modified_office.web_site = form.cleaned_data['web_site']
            modified_office.country = office.country #Country.objects.get(f.cleaned_data['country'])
            modified_office.is_a_proposal = True
            modified_office.is_valid = True
            modified_office.save()
            # create the OfficeProposal
            #modifiedOffice = f.save()
            modified_office.logged_save(person)
            office_prop = OfficeProposal(original = office,
                modified = modified_office, author = person, action = 1)
            office_prop.logged_save(person)
            # create the notification
            notif = Notification(title = _('Proposal for modifying an office'),
                details = "", office_proposal = office_prop)
            notif.logged_save(person)
            request.user.message_set.create(message=_('Your proposal for\
 modifying an office has been sent to moderators.'))
        else:
            request.user.message_set.create(message=_('Something was wrong in\
 the form you filled. No modification done.'))
            return ain7_render_to_response(request,
                'organizations/office_edit.html',
                {'form': form, 'title': _('Modify an office')})
        return HttpResponseRedirect(reverse(organization_edit,
            args=[modified_office.organization.id]))

@confirmation_required(lambda office_id=None:
    str(get_object_or_404(Office,pk=office_id)), 'organizations/base.html',
    _('Do you really want to propose the office for removal'))
@login_required
def office_delete(request, office_id=None):
    """office delete"""

    access = check_access(request, request.user,
        ['ain7-membre', 'ain7-secretariat'])
    if access:
        return access

    person = get_object_or_404(Person, user=request.user.id)
    office_prop = OfficeProposal(
        original = get_object_or_404(Office,pk=office_id),
        modified = None, author = person, action = 2)
    office_prop.logged_save(person)
    # create the notification
    notif = Notification(title = _('Proposal for removing an office'),
        details = "", office_proposal = office_prop)
    notif.logged_save(person)
    request.user.message_set.create(message=_('Your proposal for deleting an\
 office has been sent to moderators.'))
    return HttpResponseRedirect(reverse(organization_edit,
         args=[office_prod.organization.id]))

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
            request, 'organizations/office_merge.html',
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
    'organizations/base.html',
    _('Do you REALLY want to have'))
def office_merge_perform(request, office1_id, office2_id):
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
def office_proposal_register(request, organization_id, proposal_id=None):
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
        'organizations/proposal_register.html',
        {'action_title': _('Validate a new office'),
         'form': form, 'back': back})

@login_required
def office_proposal_edit(request, organization_id, proposal_id=None):
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
        'organizations/proposal_edit_office.html',
        {'form': form, 'original': proposal.original, 'back': back})

@login_required
def office_proposal_delete(request, proposal_id=None):
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
    return ain7_render_to_response(request, 'organizations/office_details.html',
        {'office': office, 'back': back, 'action': 'propose_deletion'})


