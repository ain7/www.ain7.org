# -*- coding: utf-8
#
# manage/views.py
#
#   Copyright (C) 2007-2008 AIn7
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

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission, User
from django.core.paginator import ObjectPaginator, InvalidPage
from django import newforms as forms
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _

from ain7.utils import ain7_render_to_response, ain7_generic_edit
from ain7.decorators import confirmation_required
from ain7.annuaire.models import Person, UserContribution
from ain7.emploi.models import Organization, Office, ActivityField
from ain7.emploi.models import OrganizationProposal, OfficeProposal
from ain7.manage.models import *
from ain7.manage.forms import *
from ain7.emploi.forms import OrganizationForm, OfficeForm

@login_required
def index(request):
    return ain7_render_to_response(request, 'manage/default.html',
        {'notifications': Notification.objects.all()})

@login_required
def users_search(request):

    form = SearchPersonForm()
    nb_results_by_page = 25
    persons = False
    paginator = ObjectPaginator(Group.objects.none(),nb_results_by_page)
    page = 1

    if request.method == 'POST':
        form = SearchPersonForm(request.POST)
        if form.is_valid():
            persons = form.search()
            paginator = ObjectPaginator(persons, nb_results_by_page)
            try:
                page = int(request.GET.get('page', '1'))
                persons = paginator.get_page(page - 1)
            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'manage/users_search.html',
        {'form': form, 'persons': persons,
         'paginator': paginator, 'is_paginated': paginator.pages > 1,
         'has_next': paginator.has_next_page(page - 1),
         'has_previous': paginator.has_previous_page(page - 1),
         'current_page': page,
         'next_page': page + 1, 'previous_page': page - 1,
         'pages': paginator.pages,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.hits),
         'hits' : paginator.hits,})

@login_required
def user_details(request, user_id):

    u = get_object_or_404(User, pk=user_id)
    return ain7_render_to_response(
        request, 'manage/user_details.html', {'this_user': u})

@login_required
def user_register(request):

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
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 'manage/edit_form.html',
        {'action_title': _('Register new user'), 'back': back, 'form': form})

@login_required
def organizations_search(request):

    form = SearchOrganizationForm()
    nb_results_by_page = 25
    organizations = False
    paginator = ObjectPaginator(Organization.objects.none(),nb_results_by_page)
    page = 1
    if request.method == 'POST':
        form = SearchOrganizationForm(request.POST)
        if form.is_valid():
            organizations = form.search()
            paginator = ObjectPaginator(organizations, nb_results_by_page)
            try:
                page = int(request.GET.get('page', '1'))
                organizations = paginator.get_page(page - 1)
            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'manage/organizations_search.html',
        {'form': form, 'organizations': organizations,
         'nb_org': Organization.objects.valid_organizations().count(),
         'nb_offices': Office.objects.valid_offices().count(),
         'paginator': paginator, 'is_paginated': paginator.pages > 1,
         'has_next': paginator.has_next_page(page - 1),
         'has_previous': paginator.has_previous_page(page - 1),
         'current_page': page, 'pages': paginator.pages,
         'next_page': page + 1, 'previous_page': page - 1,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.hits),
         'hits' : paginator.hits,})

@login_required
def organization_edit(request, organization_id=None):

    organization = None
    if organization_id:
        organization = get_object_or_404(Organization, pk=organization_id)
        form = OrganizationForm(
            {'name': organization.name, 'size': organization.size,
             'activity_field': organization.activity_field,
             'short_description': organization.short_description,
             'long_description': organization.long_description })
        action_title = _('Edit an organization')
    else:
        form = OrganizationForm()
        action_title = _('Register an organization')

    if request.method == 'POST':
        form = OrganizationForm(request.POST.copy())
        if form.is_valid():
            org = form.save(is_a_proposal=False, organization=organization)
            if organization:
                msg = _('Organization successfully modified')
            else:
                msg = _('Organization successfully created')
            request.user.message_set.create(message=msg)
            return HttpResponseRedirect('/manage/organizations/%s/' % org.id)
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No organization registered.')+str(form.errors))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request,
        'manage/organization_edit.html',
        {'action_title': action_title, 'form': form, 'back': back})


@login_required
def organization_details(request, organization_id):
    c = get_object_or_404(Organization, pk=organization_id)
    return ain7_render_to_response(request, 'manage/organization_details.html',
                                   {'organization': c})


@confirmation_required(
    lambda user_id=None,
    organization_id=None: str(get_object_or_404(Organization, pk=organization_id)),
    'manage/base.html',
    _('Do you REALLY want to delete this organization'))
def organization_delete(request, organization_id):

    organization = get_object_or_404(Organization, pk=organization_id)
    organization.delete()
    request.user.message_set.create(
        message=_('Organization successfully removed'))
    return HttpResponseRedirect('/manage/')


@login_required
def organization_merge(request, organization_id=None):

    organization = get_object_or_404(Organization, pk=organization_id)

    # comme on ne peut définir le queryset qu'à la déclaration du champ,
    # je dois créer le formulaire ici
    class OrganizationListForm(forms.Form):        
        org = forms.ModelChoiceField(
            label=_('organization'), required=True,
            queryset=Organization.objects.valid_organizations().exclude(id=organization_id))

    # 1er passage : on demande la saisie d'une deuxième organisation
    if request.method == 'GET':
        f = OrganizationListForm()
        return ain7_render_to_response(
            request, 'manage/organization_merge.html',
            {'form': f, 'organization': organization})

    # 2e passage : sauvegarde, notification et redirection
    if request.method == 'POST':
        f = OrganizationListForm(request.POST.copy())
        if f.is_valid():
            organization2 = f.cleaned_data['org']
            return HttpResponseRedirect('/manage/organizations/%s/merge/%s/' %
                (organization2.id, organization_id))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            return HttpResponseRedirect('/manage/organizations/%s/merge/' %
                organization_id)
        

@confirmation_required(
    lambda user_id=None, org1_id=None, org2_id=None:
    str(get_object_or_404(Organization, pk=org2_id)) + _(' replaced by ') + \
    str(get_object_or_404(Organization, pk=org1_id)),
    'manage/base.html',
    _('Do you REALLY want to have'))
def organization_do_merge(request, org1_id, org2_id):

    org1 = get_object_or_404(Organization, pk=org1_id)
    org2 = get_object_or_404(Organization, pk=org2_id)
    org1.merge(org2)
    request.user.message_set.create(
        message=_('Organizations successfully merged'))
    return HttpResponseRedirect('/manage/organizations/%s/' % org1_id)

@login_required
def organization_register_proposal(request, proposal_id=None):

    if not proposal_id:
        return HttpResponseRedirect('/manage/')
    
    proposal = get_object_or_404(OrganizationProposal, pk=proposal_id)
    form = OrganizationForm(
        {'name': proposal.modified.name,
         'size': proposal.modified.size,
         'activity_field': str(proposal.modified.activity_field),
         'short_description': proposal.modified.short_description, 
         'long_description': proposal.modified.long_description })

    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save(is_a_proposal=False)
            # on supprime la notification et la proposition
            notification = Notification.objects.get(
                organization_proposal=proposal )
            notification.delete()
            proposal.delete()
            request.user.message_set.create(message=_('Organization successfully created'))
            return HttpResponseRedirect('/manage/')
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No organization registered.') + str(form.errors))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request,
        'manage/proposal_register.html',
        {'action_title': _('Proposal for adding an organization'),
         'form': form, 'back': back})

@login_required
def organization_edit_proposal(request, proposal_id=None):

    if not proposal_id:
        return HttpResponseRedirect('/manage/')
    
    proposal = get_object_or_404(OrganizationProposal, pk=proposal_id)
    form = OrganizationForm(
        {'name': proposal.modified.name,
         'size': proposal.modified.size,
         'activity_field': str(proposal.modified.activity_field),
         'short_description': proposal.modified.short_description, 
         'long_description': proposal.modified.long_description })

    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save(is_a_proposal=False,
                                     organization=proposal.original)
            # on supprime la notification et la proposition
            notification = Notification.objects.get(
                organization_proposal=proposal )
            notification.delete()
            proposal.modified.delete()
            proposal.delete()
            request.user.message_set.create(message=_('Organization successfully modified'))
            return HttpResponseRedirect('/manage/')
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            
    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request,
        'manage/proposal_edit_organization.html',
        {'form': form, 'original': proposal.original, 'back': back})

@login_required
def organization_delete_proposal(request, proposal_id=None):

    proposal = get_object_or_404(OrganizationProposal, pk=proposal_id)
    org = proposal.original
    back = request.META.get('HTTP_REFERER', '/')
    if request.method == 'POST':
        return HttpResponseRedirect('/manage/organizations/%d/delete/'% org.id)
    return ain7_render_to_response(request, 'manage/organization_details.html',
        {'organization': org, 'back': back, 'action': 'propose_deletion'})

@login_required
def office_edit(request, office_id=None, organization_id=None):

    office = None
    if office_id:
        return ain7_generic_edit(
            request, get_object_or_404(Office, pk=office_id),
            OfficeForm, {'is_a_proposal': False},
            'manage/organization_edit.html',
            {'action_title': _('Edit an office'),
             'back': request.META.get('HTTP_REFERER', '/')}, {},
            '/manage/offices/%s/' % office_id,
            _('Office successfully modified'))
    else:
        return ain7_generic_edit(
            request, None, OfficeForm, {'is_a_proposal': False},
            'manage/organization_edit.html',
            {'action_title': _('Register an office'),
             'back': request.META.get('HTTP_REFERER', '/')}, {},
            '/manage/offices/$objid/', _('Office successfully created'))

@login_required
def office_details(request, office_id):
    office = get_object_or_404(Office, pk=office_id)
    return ain7_render_to_response(request, 'manage/office_details.html',
        {'office': office})


@confirmation_required(
    lambda user_id=None,
    office_id=None: str(get_object_or_404(Office, pk=office_id)),
    'manage/base.html',
    _('Do you REALLY want to delete this office'))
def office_delete(request, office_id):

    organization_id = office.organization.id
    return ain7_generic_delete(request,
        get_object_or_404(Office, pk=office_id),
        '/manage/organizations/%s/' % organization_id,
        _('Office successfully removed'))


@login_required
def office_merge(request, office_id=None):

    office = get_object_or_404(Office, pk=office_id)

    # comme on ne peut définir le queryset qu'à la déclaration du champ,
    # je dois créer le formulaire ici
    class OfficeListForm(forms.Form):        
        bureau = forms.ModelChoiceField(
            label=_('office'), required=True,
            queryset=Office.objects.valid_offices().exclude(id=office_id))

    # 1er passage : on demande la saisie d'une deuxième organisation
    if request.method == 'GET':
        f = OfficeListForm()
        return ain7_render_to_response(
            request, 'manage/office_merge.html', {'form':f, 'office':office})

    # 2e passage : sauvegarde, notification et redirection
    if request.method == 'POST':
        f = OfficeListForm(request.POST.copy())
        if f.is_valid():
            office2 = f.cleaned_data['bureau']
            return HttpResponseRedirect('/manage/offices/%s/merge/%s/' %
                (office2.id, office_id))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.')+str(f.errors))
            return HttpResponseRedirect('/manage/offices/%s/merge/' %
                office_id)
        

@confirmation_required(
    lambda user_id=None, office1_id=None, office2_id=None:
    str(get_object_or_404(Office, pk=office2_id)) + _(' replaced by ') + \
    str(get_object_or_404(Office, pk=office1_id)),
    'manage/base.html',
    _('Do you REALLY want to have'))
def office_do_merge(request, office1_id, office2_id):

    office1 = get_object_or_404(Office, pk=office1_id)
    office2 = get_object_or_404(Office, pk=office2_id)
    office1.merge(office2)
    request.user.message_set.create(message=_('Offices successfully merged'))
    return HttpResponseRedirect('/manage/offices/%s/' % office1_id)


@login_required
def office_register_proposal(request, proposal_id=None):

    if not proposal_id:
        return HttpResponseRedirect('/manage/')
    
    proposal = get_object_or_404(OfficeProposal, pk=proposal_id)
    form = OfficeForm(instance=proposal.modified)

    if request.method == 'POST':
        form = OfficeForm(request.POST.copy(), instance=proposal.modified)
        if form.is_valid():
            form.cleaned_data['is_a_proposal'] = False
            office = form.save()
            # on supprime la notification et la proposition
            notification = Notification.objects.get(office_proposal=proposal)
            notification.delete()
            proposal.delete()
            request.user.message_set.create(message=_('Office successfully created'))
            return HttpResponseRedirect('/manage/')
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.') + str(form.errors))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request,
        'manage/proposal_register.html',
        {'action_title': _('Proposal for adding an office'),
         'form': form, 'back': back})

@login_required
def groups_search(request):

    form = SearchGroupForm()
    nb_results_by_page = 25
    groups = False
    paginator = ObjectPaginator(Group.objects.none(),nb_results_by_page)
    page = 1

    if request.method == 'POST':
        form = SearchGroupForm(request.POST)
        if form.is_valid():
            groups = form.search()
            paginator = ObjectPaginator(groups, nb_results_by_page)
            try:
                page = int(request.GET.get('page', '1'))
                groups = paginator.get_page(page - 1)
            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'manage/groups_search.html',
        {'form': form, 'groups': groups,'paginator': paginator,
         'is_paginated': paginator.pages > 1,
         'has_next': paginator.has_next_page(page - 1),
         'has_previous': paginator.has_previous_page(page - 1),
         'current_page': page,
         'next_page': page + 1,  'previous_page': page - 1,
         'pages': paginator.pages,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.hits),
         'hits' : paginator.hits,})

@login_required
def group_details(request, group_id):
    g = get_object_or_404(Group, pk=group_id)
    return ain7_render_to_response(request, 'manage/group_details.html', {'group': g})

@login_required
def perm_add(request, group_id):
    g = get_object_or_404(Group, pk=group_id)

    form = PermGroupForm()

    if request.method == 'POST':
        form = PermGroupForm(request.POST)
        if form.is_valid():
            p = Permission.objects.filter(name=form.cleaned_data['perm'])[0]
            g.permissions.add(p)
            request.user.message_set.create(message=_('Permission added to group'))
            return HttpResponseRedirect('/manage/groups/%s/' % group_id)
        else:
            request.user.message_set.create(message=_('Permission is not correct'))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request, 'manage/groups_perm_add.html',
                            {'form': form, 'group': g, 'back': back})

@login_required
def perm_delete(request, group_id, perm_id):
    group = get_object_or_404(Group, pk=group_id)
    perm = get_object_or_404(Permission, pk=perm_id)

    group.permissions.remove(perm)

    request.user.message_set.create(message=_('Permission removed from group'))

    return HttpResponseRedirect('/manage/groups/%s/' % group_id)

@login_required
def member_add(request, group_id):

    g = get_object_or_404(Group, pk=group_id)

    form = MemberGroupForm()

    if request.method == 'POST':
        form = MemberGroupForm(request.POST)
        if form.is_valid():
            u = User.objects.get(id=form.cleaned_data['username'])
            u.groups.add(g)
            request.user.message_set.create(message=_('User added to group'))
            return HttpResponseRedirect('/manage/groups/%s/' % group_id)
        else:
            request.user.message_set.create(message=_('User is not correct'))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request, 'manage/groups_user_add.html',
                            {'form': form, 'group': g, 'back': back})

@login_required
def member_delete(request, group_id, member_id):
    group = get_object_or_404(Group, pk=group_id)
    member = get_object_or_404(User, pk=member_id)

    member.groups.remove(group)

    request.user.message_set.create(message=_('Member removed from group'))

    return HttpResponseRedirect('/manage/groups/%s/' % group_id)

@login_required
def permissions(request):

    nb_results_by_page = 25

    permissions = Permission.objects.all()
    paginator = ObjectPaginator(Permission.objects.all(), nb_results_by_page)

    try:
        page = int(request.GET.get('page', '1'))
        permissions = paginator.get_page(page - 1)

    except InvalidPage:
        raise http.Http404

    return ain7_render_to_response(request, 'manage/permissions.html', {'permissions': permissions, 'paginator': paginator, 'is_paginated': paginator.pages > 1,
            'has_next': paginator.has_next_page(page - 1),
            'has_previous': paginator.has_previous_page(page - 1),
            'current_page': page,
            'next_page': page + 1,
            'previous_page': page - 1,
            'pages': paginator.pages,
            'first_result': (page - 1) * nb_results_by_page +1,
            'last_result': min((page) * nb_results_by_page, paginator.hits),
            'hits' : paginator.hits,})

@login_required
def permission_details(request, perm_id):

    permission = get_object_or_404(Permission, pk=perm_id)

    return ain7_render_to_response(request, 'manage/permission_details.html', {'permission': permission})

@login_required
def contributions(request):

    form = SearchContributionForm()
    nb_results_by_page = 25
    contributions = False
    paginator = ObjectPaginator(UserContribution.objects.none(),nb_results_by_page)
    page = 1

    if request.method == 'POST':
        form = SearchContributionForm(request.POST)
        if form.is_valid():

            # criteres sur le nom et prenom
            #criteria={'user__contains':form.cleaned_data['user'].encode('utf8')}
            criteria={}

            contributions = UserContribution.objects.filter(**criteria)
            paginator = ObjectPaginator(contributions, nb_results_by_page)

            try:
                page = int(request.GET.get('page', '1'))
                contributions = paginator.get_page(page - 1)

            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'manage/contributions.html',
                            {'form': form, 'contributions': contributions,'paginator': paginator, 'is_paginated': paginator.pages > 1,
                    'has_next': paginator.has_next_page(page - 1),
                    'has_previous': paginator.has_previous_page(page - 1),
                    'current_page': page,
                    'next_page': page + 1,
                    'previous_page': page - 1,
                    'pages': paginator.pages,
                    'first_result': (page - 1) * nb_results_by_page +1,
                    'last_result': min((page) * nb_results_by_page, paginator.hits),
                    'hits' : paginator.hits,})

@login_required
def perm_add(request, group_id):
    g = get_object_or_404(Group, pk=group_id)

    form = PermGroupForm()

    if request.method == 'POST':
        form = PermGroupForm(request.POST)
        if form.is_valid():
            p = Permission.objects.filter(name=form.cleaned_data['perm'])[0]
            g.permissions.add(p)
            request.user.message_set.create(message=_('Permission added to group'))
            return HttpResponseRedirect('/manage/groups/%s/' % group_id)
        else:
            request.user.message_set.create(message=_('Permission is not correct'))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request, 'manage/groups_perm_add.html',
                            {'form': form, 'group': g, 'back': back})

@login_required
def notification_add(request):

    return ain7_generic_edit(
        request, None, NotificationForm,
        {'organization_proposal': None, 'office_proposal': None},
        'manage/notification.html',
        {'action_title': _('Add a new notification'),
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/manage/', _('Notification successfully created'))

@login_required
def notification_edit(request, notif_id):

    return ain7_generic_edit(
        request, get_object_or_404(Notification, pk=notif_id),
        NotificationForm,
        {'organization_proposal': None, 'office_proposal': None},
        'manage/notification.html',
        {'action_title': _("Modification of the notification"),
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/manage/', _("Modifications have been successfully saved."))

@confirmation_required(
    lambda user_id=None,
    notif_id=None: str(get_object_or_404(Notification, pk=notif_id)),
    'manage/base.html',
    _('Do you REALLY want to delete the notification'))
def notification_delete(request, notif_id):

    notif = get_object_or_404(Notification, pk=notif_id)
    if notif.organization_proposal:
        notif.organization_proposal.delete()
    if notif.office_proposal:
        notif.office_proposal.delete()
    notif.delete()
    request.user.message_set.create(
        message=_("The notification has been successfully removed."))
    return HttpResponseRedirect('/manage/')
