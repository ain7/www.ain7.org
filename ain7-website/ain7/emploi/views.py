# -*- coding: utf-8
#
# emploi/views.py
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

from datetime import datetime

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage
from django import forms
from django.forms import widgets
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.forms.util import ValidationError
from django.core.urlresolvers import reverse

from ain7.annuaire.models import Person, AIn7Member, Track
from ain7.decorators import confirmation_required
from ain7.emploi.models import *
from ain7.emploi.forms import *
from ain7.manage.models import Notification
from ain7.utils import ain7_render_to_response, ain7_generic_edit, ain7_generic_delete
from ain7.fields import AutoCompleteField


@login_required
def index(request):

    p = Person.objects.get(user=request.user.id)
    try:
         ain7member = AIn7Member.objects.get(person=p)
         list_emplois =  ain7member.interesting_jobs()
    except AIn7Member.DoesNotExist:
         ain7member = None
         list_emplois = None
    return ain7_render_to_response(request, 'emploi/index.html',
        {'ain7member': ain7member,
         'liste_emplois': list_emplois})

@login_required
def cv_details(request, user_id):

    p = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)
    return ain7_render_to_response(request, 'emploi/cv_details.html',
                            {'person': p, 'ain7member': ain7member})

@login_required
def cv_edit(request, user_id=None):

    p = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)
    return ain7_render_to_response(request, 'emploi/cv_edit.html',
                            {'person': p, 'ain7member': ain7member})

@login_required
def position_edit(request, user_id=None, position_id=None):

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    return ain7_generic_edit(
        request, get_object_or_404(Position, pk=position_id),
        PositionForm, {'ain7member': ain7member},
        'emploi/position_edit.html',
        {'action': 'edit', 'ain7member': ain7member}, {},
        reverse(cv_edit, args=[user_id])+'#prof_exp',
        _('Position informations updated successfully.'))

@confirmation_required(lambda user_id=None, position_id=None: str(get_object_or_404(Position, pk=position_id)), 'emploi/base.html', _('Do you really want to delete your position'))
@login_required
def position_delete(request, user_id=None, position_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(Position, pk=position_id),
        reverse(cv_edit, args=[user_id])+'#prof_exp',
        _('Position successfully deleted.'))

@login_required
def position_add(request, user_id=None):

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    return ain7_generic_edit(
        request, None,
        PositionForm, {'ain7member': ain7member},
        'emploi/position_edit.html',
        {'action': 'create', 'ain7member': ain7member}, {},
        reverse(cv_edit, args=[user_id])+'#prof_exp',
        _('Position successfully added.'))

@login_required
def education_edit(request, user_id=None, education_id=None):

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    return ain7_generic_edit(
        request, get_object_or_404(EducationItem, pk=education_id),
        EducationItemForm, {'ain7member': ain7member},
        'emploi/education_edit.html',
        {'action': 'edit', 'ain7member': ain7member}, {},
        reverse(cv_edit, args=[user_id])+'#education',
        _('Education informations updated successfully.'))

@confirmation_required(lambda user_id=None, education_id=None: str(get_object_or_404(EducationItem, pk=education_id)), 'emploi/base.html', _('Do you really want to delete your education item'))
@login_required
def education_delete(request, user_id=None, education_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(EducationItem, pk=education_id),
        reverse(cv_edit, args=[user_id])+'#education',
        _('Education informations deleted successfully.'))

@login_required
def education_add(request, user_id=None):

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    return ain7_generic_edit(
        request, None,
        EducationItemForm, {'ain7member': ain7member},
        'emploi/education_edit.html',
        {'action': 'create', 'ain7member': ain7member}, {},
        reverse(cv_edit, args=[user_id])+'#education',
        _('Education informations successfully added.'))

@login_required
def leisure_edit(request, user_id=None, leisure_id=None):

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    return ain7_generic_edit(
        request, get_object_or_404(LeisureItem, pk=leisure_id),
        LeisureItemForm, {'ain7member': ain7member},
        'emploi/leisure_edit.html',
        {'action': 'edit', 'ain7member': ain7member}, {},
        reverse(cv_edit, args=[user_id])+'#leisure',
        _('Leisure informations updated successfully.'))

@confirmation_required(lambda user_id=None, leisure_id=None: str(get_object_or_404(LeisureItem, pk=leisure_id)), 'emploi/base.html', _('Do you really want to delete your leisure item'))
@login_required
def leisure_delete(request, user_id=None, leisure_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(LeisureItem, pk=leisure_id),
        reverse(cv_edit, args=[user_id])+'#leisure',
        _('Leisure informations successfully deleted.'))

@login_required
def leisure_add(request, user_id=None):

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    return ain7_generic_edit(
        request, None,
        LeisureItemForm, {'ain7member': ain7member},
        'emploi/leisure_edit.html',
        {'action': 'create', 'ain7member': ain7member}, {},
        reverse(cv_edit, args=[user_id])+'#leisure',
        _('Leisure informations successfully added.'))

@login_required
def publication_edit(request, user_id=None, publication_id=None):

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    publi = get_object_or_404(PublicationItem,pk=publication_id)
    return ain7_generic_edit(
        request, publi, PublicationItemForm, {'ain7member': ain7member},
        'emploi/publication_edit.html',
        {'action': 'edit', 'ain7member': ain7member}, {},
        reverse(cv_edit, args=[user_id])+'#publications',
        _('Publication informations updated successfully.'))

@confirmation_required(lambda user_id=None, publication_id=None: str(get_object_or_404(PublicationItem,pk=publication_id)), 'emploi/base.html', _('Do you really want to delete your publication'))
@login_required
def publication_delete(request, user_id=None, publication_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(PublicationItem,pk=publication_id),
        reverse(cv_edit, args=[user_id])+'#publications',
        _('Publication informations deleted successfully.'))

@login_required
def publication_add(request, user_id=None):

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    return ain7_generic_edit(
        request, None, PublicationItemForm, {'ain7member': ain7member},
        'emploi/publication_edit.html',
        {'action': 'create', 'ain7member': ain7member}, {},
        reverse(cv_edit, args=[user_id])+'#publications',
        _('Publication informations updated successfully.'))

@login_required
def job_details(request,emploi_id):

    j = get_object_or_404(JobOffer, pk=emploi_id)
    j.nb_views = j.nb_views + 1
    j.save()
    return ain7_render_to_response(
        request, 'emploi/job_details.html', {'job': j})

@login_required
def job_edit(request, emploi_id):

    j = get_object_or_404(JobOffer, pk=emploi_id)
    tracks_id = []
    if j.track:
        tracks_id = [ t.id for t in j.track.all() ]
    f = JobOfferForm(
        {'reference': j.reference, 'title': j.title,
         'experience': j.experience, 'contract_type': j.contract_type,
         'is_opened': j.is_opened, 'description': j.description,
         'office': j.office.id, 'contact_name': j.contact_name,
         'contact_email': j.contact_email,
         'track':  tracks_id})

    if request.method == 'POST':
        f = JobOfferForm(request.POST)
        if f.is_valid():
            f.save(request.user, job_offer=j)
            request.user.message_set.create(
                message=_('Job offer successfully modified.'))
            return HttpResponseRedirect(reverse(job_details, args=[j.id]))
        else:
            request.user.message_set.create(
                message=_('Something was wrong in the form you filled. No modification done.'))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 'emploi/job_edit.html', {'form': f, 'job': j, 'back': back})

@login_required
def job_register(request):

    f = JobOfferForm({})

    if request.method == 'POST':
        f = JobOfferForm(request.POST)
        if f.is_valid():
            job_offer = f.save(request.user)
            request.user.message_set.create(
                message=_('Job offer successfully created.'))
            return HttpResponseRedirect(reverse(job_details, args=[job_offer.id]))
        else:
            request.user.message_set.create(
                message=_('Something was wrong in the form you filled. No modification done.'))
            
    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 'emploi/job_register.html', {'form': f, 'back': back})

@login_required
def job_search(request):

    form = SearchJobForm()
    nb_results_by_page = 25
    list_jobs = False
    paginator = Paginator(JobOffer.objects.none(),nb_results_by_page)
    page = 1

    if request.method == 'POST':
        form = SearchJobForm(request.POST)
        if form.is_valid():
            list_jobs = form.search()
            paginator = Paginator(list_jobs, nb_results_by_page)
            try:
                page = int(request.GET.get('page', '1'))
                list_jobs = paginator.page(page).object_list
            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'emploi/job_search.html',
        {'form': form, 'list_jobs': list_jobs,
         'request': request,
         'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page,
         'next_page': page + 1, 'previous_page': page - 1,
         'pages': paginator.num_pages,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits' : paginator.count })

@login_required
def organization_details(request, organization_id):

    organization = get_object_or_404(Organization, pk=organization_id)
    return ain7_render_to_response(request,
        'emploi/organization_details.html', {'organization': organization})

@login_required
def organization_add(request):

    p = get_object_or_404(Person, user=request.user.id)

    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        f = OrganizationForm()
        return ain7_render_to_response(request, 'emploi/office_create.html',
            {'form': f, 'title': _('Propose the creation of an organization')})

    # 2e passage : sauvegarde, notification et redirection
    if request.method == 'POST':
        f = OrganizationForm(request.POST.copy())
        if f.is_valid():
            # create the OrganizationProposal
            modifiedOrg = f.save(request.user,is_a_proposal=True)
            orgprop = OrganizationProposal(original = None,
                modified = modifiedOrg, author = p, action = 0)
            orgprop.logged_save(p)
            # create the notification
            notif = Notification(details="", organization_proposal=orgprop,
                title=_('Proposal for adding an organization'))
            notif.logged_save(p)
            request.user.message_set.create(message=_('Your proposal for adding an organization has been sent to moderators.'))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            return ain7_render_to_response(request,
                'emploi/office_create.html', {'form': f,
                'title': _('Propose the creation of an organization')})
        return HttpResponseRedirect(reverse(index))

@login_required
def organization_choose(request, action=None):

    person = get_object_or_404(Person, pk=request.user.id)

    class ChooseOrganizationForm(forms.Form):
        organization = forms.IntegerField(label=_('Organization'), required=True,widget=AutoCompleteField(url='/ajax/organization/'))

        def clean_organization(self):
            o = self.cleaned_data['organization']

            if o == None:
                raise ValidationError(_('The organization is mandatory.'))

            try:
                Organization.objects.get(id=o)
            except Organization.DoesNotExist:
                raise ValidationError(_('The organization "%s" does not exist.') % o)
            else:
                return self.cleaned_data['organization']


    if request.method == 'GET':
            
        form = ChooseOrganizationForm()
        title = _('Choose an organization for which you want to propose modifications')
        if action == 'delete':
            title = _('Choose an organization to propose for deletion')
        return ain7_render_to_response(request,
            'emploi/office_create.html', {'form': form, 'title': title})
        
    if request.method == 'POST':
        
        form = ChooseOrganizationForm(request.POST.copy())
        if form.is_valid():
            org_id = form.cleaned_data['organization']
            if action == 'edit':
                return HttpResponseRedirect(reverse(organization_edit,args=[org_id]))
            if action == 'delete':
                return HttpResponseRedirect(reverse(organization_delete,args=[org_id]))
        else:
            return HttpResponseRedirect(reverse(organization_edit,args=[org_id]))

@login_required
def organization_edit(request, organization_id=None):
    org = get_object_or_404(Organization, pk=organization_id)
    return ain7_render_to_response(request,
        'emploi/organization_edit.html', {'organization': org})

@login_required
def organization_edit_data(request, organization_id=None):
    org = get_object_or_404(Organization, pk=organization_id)
    p = get_object_or_404(Person, user=request.user.id)

    if request.method == 'GET':
        f = OrganizationForm(
            {'name':org.name, 'size':org.size,
             'activity_field':org.activity_field,
             'short_description':org.short_description,
             'long_description':org.long_description})
        return ain7_render_to_response(request, 'emploi/office_create.html',
            {'form': f, 'title':_('Proposition of organization modification')})

    if request.method == 'POST':
        f = OrganizationForm(request.POST.copy())
        if f.is_valid():
            # create the OrganizationProposal
            modifiedOrg = f.save(request.user, is_a_proposal=True)
            orgprop = OrganizationProposal(original = org,
                modified = modifiedOrg, author = p, action = 1)
            orgprop.logged_save(p)
            # create the notification
            notif = Notification(details="", organization_proposal=orgprop,
                title=_('Proposal for modifying an organization'))
            notif.logged_save(p)
            request.user.message_set.create(message=_('Your proposal for modifying an organization has been sent to moderators.'))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            return ain7_render_to_response(request,
                'emploi/office_create.html',
                {'form': f, 'title': _('Proposition of organization modification')})
        return HttpResponseRedirect(reverse(index))

@confirmation_required(lambda organization_id=None: str(get_object_or_404(Organization, pk=organization_id)), 'emploi/base.html', _('Do you really want to propose the deletion of this organization'))
@login_required
def organization_delete(request, organization_id=None):

    org = get_object_or_404(Organization, pk=organization_id)
    p = get_object_or_404(Person, user=request.user.id)
    orgprop = OrganizationProposal(original = org,
        modified = None, author = p, action = 2)
    orgprop.logged_save(p)
    # create the notification
    notif = Notification(details="", organization_proposal=orgprop,
                         title=_('Proposal for deleting an organization'))
    notif.logged_save(p)
    request.user.message_set.create(message=_('Your proposal for deleting an organization has been sent to moderators.'))
    return HttpResponseRedirect(reverse(index))

@login_required
def office_edit(request, office_id=None):

    office = get_object_or_404(Office, pk=office_id)
    p = get_object_or_404(Person, user=request.user.id)

    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        f = OfficeFormNoOrg(instance = office)
        return ain7_render_to_response(request, 'emploi/office_create.html',
            {'form': f, 'title': _('Modify an office')})

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        f = OfficeFormNoOrg(request.POST.copy(), instance = office)
        if f.is_valid():
            f.cleaned_data['is_a_proposal'] = True
            f.cleaned_data['is_valid'] = True
            f.cleaned_data['organization'] = office.organization
            # create the OfficeProposal
            modifiedOffice = f.save()
            modifiedOffice.logged_save(p)
            officeProp = OfficeProposal(original = office.organization,
                modified = modifiedOffice, author = p, action = 1)
            officeProp.logged_save(p)
            # create the notification
            notif = Notification(title = _('Proposal for modifying an office'),
                details = "", office_proposal = officeProp)
            notif.logged_save(p)
            request.user.message_set.create(message=_('Your proposal for modifying an office has been sent to moderators.'))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            return ain7_render_to_response(request,
                'emploi/office_create.html',
                {'form': f, 'title': _('Modify an office')})
        return HttpResponseRedirect(reverse(index))

@confirmation_required(lambda office_id=None: str(get_object_or_404(Office,pk=office_id)), 'emploi/base.html', _('Do you really want to propose the office for removal'))
@login_required
def office_delete(request, office_id=None):

    p = get_object_or_404(Person, user=request.user.id)
    officeProp = OfficeProposal(
        original = get_object_or_404(Office,pk=office_id),
        modified = None, author = p, action = 2)
    officeProp.logged_save(p)
    # create the notification
    notif = Notification(title = _('Proposal for removing an office'),
        details = "", office_proposal = officeProp)
    notif.logged_save(p)
    request.user.message_set.create(message=_('Your proposal for deleting an office has been sent to moderators.'))
    return HttpResponseRedirect(reverse(index))

@login_required
def office_add(request, organization_id=None):

    org = get_object_or_404(Organization, pk=organization_id)
    p = get_object_or_404(Person, user=request.user.id)

    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        f = OfficeFormNoOrg()
        return ain7_render_to_response(request, 'emploi/office_create.html',
            {'form': f, 'title': _('Create an office')})

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        f = OfficeFormNoOrg(request.POST.copy())
        if f.is_valid():
            f.cleaned_data['is_a_proposal'] = True
            f.cleaned_data['is_valid'] = True
            f.cleaned_data['organization'] = org
            # create the OfficeProposal
            modifiedOffice = f.save()
            modifiedOffice.logged_save(p)
            officeProp = OfficeProposal(original = None,
                modified = modifiedOffice, author = p, action = 0)
            officeProp.logged_save(p)
            # create the notification
            notif = Notification(title = _('Proposal for adding an office'),
                details = "", office_proposal = officeProp)
            notif.logged_save(p)
            request.user.message_set.create(message=_('Your proposal for adding an office has been sent to moderators.'))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            return ain7_render_to_response(request,
                'emploi/office_create.html',
                {'form': f, 'title': _('Create an office')})
        return HttpResponseRedirect(reverse(index))
