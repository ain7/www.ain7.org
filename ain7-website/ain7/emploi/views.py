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

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import ObjectPaginator, InvalidPage
from django import newforms as forms
from django.newforms import widgets
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from datetime import datetime
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person, AIn7Member, Track
from ain7.decorators import confirmation_required
from ain7.emploi.models import *
from ain7.emploi.forms import *
from ain7.manage.models import Notification
from ain7.utils import *
from ain7.fields import AutoCompleteField


@login_required
def index(request):

    p = Person.objects.get(user=request.user.id)
    ain7member = get_object_or_404(AIn7Member, person=p)

    jobs = []
    if ain7member.receive_job_offers_for_tracks.all():
        for track in ain7member.receive_job_offers_for_tracks.all():
            jobs.extend(track.jobs.all())
    else:
        jobs = JobOffer.objects.all()

    proposals = []
    proposals.extend(p.office_proposals.all())
    proposals.extend(p.organization_proposals.all())
    
    return ain7_render_to_response(request, 'emploi/index.html',
                            {'ain7member': ain7member, 'liste_emplois': jobs,
                             'proposals': proposals})

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

def _generic_edit(request, user_id, obj, formPage, redirectPage, msgDone):

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    class GenericForm(forms.ModelForm):
        class Meta:
            model = type(obj)
            exclude = ('ain7member')

    # 1er passage : on propose un formulaire avec les données actuelles
    if request.method == 'GET':
        f = GenericForm(instance=obj)
        return ain7_render_to_response(request, formPage,
            {'form': f, 'action': 'edit', 'ain7member': ain7member})

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        f = GenericForm(request.POST.copy(), instance=obj)
        if f.is_valid():
            f.cleaned_data['ain7member'] = ain7member
            f.save()
            request.user.message_set.create(message=msgDone)
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            return ain7_render_to_response(request, formPage,
                {'form': f, 'action': 'edit','ain7member': ain7member})
            # pour avoir le détail des champs mal remplis :
            # request.user.message_set.create(message=str(f.errors))
        return HttpResponseRedirect(redirectPage)

def _generic_delete(request, user_id, obj, redirectPage, msgDone):

    obj.delete()

    request.user.message_set.create(message=msgDone)

    return HttpResponseRedirect(redirectPage)

def _generic_add(request, user_id, objectType, formPage, redirectPage, msgDone):

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    class GenericForm(forms.ModelForm):
        class Meta:
            model = objectType
            exclude = ('ain7member')

    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        f = GenericForm()
        return ain7_render_to_response(request, formPage,
            {'form': f, 'action': 'create',
             'ain7member':ain7member, 'person': person})

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        f = GenericForm(request.POST.copy())
        if f.is_valid():
            f.cleaned_data['ain7member'] = ain7member
            f.save()
            request.user.message_set.create(message=msgDone)
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            return ain7_render_to_response(request, formPage,{'form': f, 'action': 'create','person': person})
            # TODO pour avoir le détail des champs mal remplis :
            # request.user.message_set.create(message=str(f.errors))
        return HttpResponseRedirect(redirectPage)

@login_required
def position_edit(request, user_id=None, position_id=None):

    return _generic_edit(request, user_id,
                         get_object_or_404(Position, pk=position_id),
                         'emploi/position_edit.html',
                         '/emploi/%s/cv/edit/#prof_exp' % user_id,
                         _('Position informations updated successfully.'))

@confirmation_required(lambda user_id=None, position_id=None: str(get_object_or_404(Position, pk=position_id)), 'emploi/base.html', _('Do you really want to delete your position'))
@login_required
def position_delete(request, user_id=None, position_id=None):

    return _generic_delete(request, user_id,
                           get_object_or_404(Position, pk=position_id),
                           '/emploi/%s/cv/edit/#prof_exp' % user_id,
                           _('Position successfully deleted.'))

@login_required
def position_add(request, user_id=None):

    return _generic_add(request, user_id, Position,
                        'emploi/position_edit.html',
                        '/emploi/%s/cv/edit/#prof_exp' % user_id,
                        _('Position successfully added.'))

@login_required
def education_edit(request, user_id=None, education_id=None):

    return _generic_edit(request, user_id,
                         get_object_or_404(EducationItem, pk=education_id),
                         'emploi/education_edit.html',
                         '/emploi/%s/cv/edit/#education' % user_id,
                         _('Education informations updated successfully.'))

@confirmation_required(lambda user_id=None, education_id=None: str(get_object_or_404(EducationItem, pk=education_id)), 'emploi/base.html', _('Do you really want to delete your education item'))
@login_required
def education_delete(request, user_id=None, education_id=None):

    return _generic_delete(request, user_id,
                           get_object_or_404(EducationItem, pk=education_id),
                           '/emploi/%s/cv/edit/#education' % user_id,
                           _('Education informations deleted successfully.'))

@login_required
def education_add(request, user_id=None):

    return _generic_add(request, user_id, EducationItem,
                        'emploi/education_edit.html',
                        '/emploi/%s/cv/edit/#education' % user_id,
                        _('Education informations successfully added.'))

@login_required
def leisure_edit(request, user_id=None, leisure_id=None):

    return _generic_edit(request, user_id,
                         get_object_or_404(LeisureItem, pk=leisure_id),
                         'emploi/leisure_edit.html',
                         '/emploi/%s/cv/edit/#leisure' % user_id,
                         _('Leisure informations updated successfully.'))

@confirmation_required(lambda user_id=None, leisure_id=None: str(get_object_or_404(LeisureItem, pk=leisure_id)), 'emploi/base.html', _('Do you really want to delete your leisure item'))
@login_required
def leisure_delete(request, user_id=None, leisure_id=None):

    return _generic_delete(request, user_id,
                           get_object_or_404(LeisureItem, pk=leisure_id),
                           '/emploi/%s/cv/edit/#leisure' % user_id,
                           _('Leisure informations successfully deleted.'))

@login_required
def leisure_add(request, user_id=None):

    return _generic_add(request, user_id, LeisureItem,
                        'emploi/leisure_edit.html',
                        '/emploi/%s/cv/edit/#leisure' % user_id,
                        _('Leisure informations successfully added.'))

@login_required
def publication_edit(request, user_id=None, publication_id=None):

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    publi = get_object_or_404(PublicationItem,pk=publication_id)
    return ain7_generic_edit(
        request, publi, PublicationItemForm, {'ain7member': ain7member},
        'emploi/publication_edit.html',
        {'action': 'edit', 'ain7member': ain7member},
        '/emploi/%s/cv/edit/#publications' % user_id, {},
        _('Publication informations updated successfully.'))

@confirmation_required(lambda user_id=None, publication_id=None: str(get_object_or_404(PublicationItem,pk=publication_id)), 'emploi/base.html', _('Do you really want to delete your publication'))
@login_required
def publication_delete(request, user_id=None, publication_id=None):

    return ain7_generic_delete(request,
        get_object_or_404(PublicationItem,pk=publication_id),
        '/emploi/%s/cv/edit/#publications' % user_id,
        _('Publication informations deleted successfully.'))

@login_required
def publication_add(request, user_id=None):

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    return ain7_generic_edit(
        request, None, PublicationItemForm, {'ain7member': ain7member},
        'emploi/publication_edit.html',
        {'action': 'create', 'ain7member': ain7member}, {},
        '/emploi/%s/cv/edit/#publications' % user_id,
        _('Publication informations updated successfully.'))

@login_required
def office_create(request, user_id=None):

    p = get_object_or_404(Person, user=user_id)

    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        f = OfficeForm()
        return ain7_render_to_response(request, 'emploi/office_create.html',
                                {'form': f, 'person': p, 'object': 'office'})

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        f = OfficeForm(request.POST.copy())
        if f.is_valid():
            # create the OfficeProposal
            modifiedOffice = f.save(is_a_proposal=True)
            officeProp = OfficeProposal()
            officeProp.original = None
            officeProp.modified = modifiedOffice
            officeProp.author = p
            officeProp.action = 0
            officeProp.save()
            # create the notification
            notif = Notification()
            notif.title = _('Proposal for adding an office')
            notif.details = ""
            notif.office_proposal = officeProp
            notif.save()
            request.user.message_set.create(message=_('Your proposal for adding an office has been sent to moderators.'))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            return ain7_render_to_response(request,
                'emploi/office_create.html',
                {'form': f, 'person': p, 'object': 'office'})
        ain7member = get_object_or_404(AIn7Member, person=p)
        return ain7_render_to_response(request, 'emploi/cv_edit.html',
                                       {'person': p, 'ain7member': ain7member})

@login_required
def company_create(request, user_id=None):

    p = get_object_or_404(Person, user=user_id)

    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        f = OrganizationForm()
        return ain7_render_to_response(request, 'emploi/office_create.html',
                                {'form': f, 'person': p, 'object': 'company'})

    # 2e passage : sauvegarde, notification et redirection
    if request.method == 'POST':
        f = OrganizationForm(request.POST.copy())
        if f.is_valid():
            # create the OrganizationProposal
            modifiedOrg = f.save(is_a_proposal=True)
            orgprop = OrganizationProposal()
            orgprop.original = None
            orgprop.modified = modifiedOrg
            orgprop.author = p
            orgprop.action = 0
            orgprop.save()
            # create the notification
            notif = Notification()
            notif.title = unicode(_('Proposal for adding an organization'),'utf8')
            notif.details = ""
            notif.organization_proposal = orgprop
            notif.save()
            request.user.message_set.create(message=_('Your proposal for adding an organization has been sent to moderators.'))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            return ain7_render_to_response(request,
                'emploi/office_create.html',
                {'form': f, 'person': p, 'object': 'company'})
        ain7member = get_object_or_404(AIn7Member, person=p)
        return ain7_render_to_response(request, 'emploi/cv_edit.html',
                                       {'person': p, 'ain7member': ain7member})

@login_required
def job_details(request,emploi_id):

    j = get_object_or_404(JobOffer, pk=emploi_id)

    j.nb_views = j.nb_views + 1
    j.save()

    return ain7_render_to_response(request, 'emploi/job_details.html', {'job': j})

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
            f.save(job_offer=j)
            request.user.message_set.create(
                message=_('Job offer successfully modified.'))
            return HttpResponseRedirect('/emploi/job/%s/' % (j.id) )
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
            job_offer = f.save()
            request.user.message_set.create(
                message=_('Job offer successfully created.'))
            return HttpResponseRedirect('/emploi/job/%s/' % (job_offer.id))
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
    paginator = ObjectPaginator(JobOffer.objects.none(),nb_results_by_page)
    page = 1

    if request.method == 'POST':
        form = SearchJobForm(request.POST)
        if form.is_valid():
            list_jobs = form.search()
            paginator = ObjectPaginator(list_jobs, nb_results_by_page)

            try:
                page = int(request.GET.get('page', '1'))
                list_jobs = paginator.get_page(page - 1)

            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'emploi/job_search.html',
                                    {'form': form, 'list_jobs': list_jobs,
                                     'request': request,
                                     'paginator': paginator, 'is_paginated': paginator.pages > 1,
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
def company_details(request, company_id):

    company = get_object_or_404(Company, pk=company_id)
    return ain7_render_to_response(request, 'emploi/company_details.html',
        {'company': company})

