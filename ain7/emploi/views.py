# -*- coding: utf-8
"""
 ain7/emploi/views.py
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

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person, AIn7Member
from ain7.decorators import access_required, confirmation_required
from ain7.emploi.models import JobOffer, Position, EducationItem, \
                               LeisureItem, PublicationItem, JobOfferView
from ain7.emploi.forms import PositionForm, EducationItemForm, \
                              LeisureItemForm, \
                              PublicationItemForm, JobOfferForm, SearchJobForm
from ain7.utils import ain7_generic_delete, check_access


@login_required
def index(request):
    """index page"""

    person = Person.objects.get(user=request.user.id)
    try:
        ain7member = AIn7Member.objects.get(person=person)
    except AIn7Member.DoesNotExist:
        ain7member = None
    liste_emplois = JobOffer.objects.filter(checked_by_secretariat=True, \
        obsolete=False).order_by('-id')[:20]
    return render(request, 'emploi/index.html',
        {'ain7member': ain7member,
         'liste_emplois': liste_emplois})

@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def cv_details(request, user_id):
    """cvs details"""

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    return render(request, 'emploi/cv_details.html',
        {'person': person, 'ain7member': ain7member})

@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def cv_edit(request, user_id=None):
    """cv edit"""

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    return render(request, 'emploi/cv_edit.html',
        {'person': person, 'ain7member': ain7member})

@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def position_edit(request, user_id=None, position_id=None):
    """position edit"""

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    form = PositionForm()

    if position_id:
        position = get_object_or_404(Position, pk=position_id)
        form = PositionForm(instance=position)

    if request.method == 'POST':
        if position_id:
            form = PositionForm(request.POST, instance=position)
        else:
            form = PositionForm(request.POST)

        if form.is_valid():
            pos = form.save(commit=False)
            pos.ain7member = ain7member
            pos.save()
            request.user.message_set.create(message=_('Modifications have been\
 successfully saved.'))

        return HttpResponseRedirect(reverse(cv_edit, 
            args=[user_id])+'#prof_exp')

    return render(
        request, 'emploi/position_edit.html',
        {'form': form, 'action_title': _("Position edit"),
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda user_id=None, position_id=None: 
    str(get_object_or_404(Position, pk=position_id)), 'emploi/base.html',
     _('Do you really want to delete your position'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def position_delete(request, user_id=None, position_id=None):
    """position delete"""

    return ain7_generic_delete(request,
        get_object_or_404(Position, pk=position_id),
        reverse(cv_edit, args=[user_id])+'#prof_exp',
        _('Position successfully deleted.'))

@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def education_edit(request, user_id=None, education_id=None):
    """education edit"""

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    form = EducationItemForm()

    if education_id:
        educationitem = get_object_or_404(EducationItem, pk=education_id)
        form = EducationItemForm(instance=educationitem)

    if request.method == 'POST':
        if education_id:
            form = EducationItemForm(request.POST, instance=educationitem)
        else:
            form = EducationItemForm(request.POST)

        if form.is_valid():
            editem = form.save(commit=False)
            editem.ain7member = ain7member
            editem.save()
            request.user.message_set.create(message=_('Modifications have been\
 successfully saved.'))

        return HttpResponseRedirect(reverse(cv_edit, 
             args=[user_id])+'#education')

    return render(
        request, 'emploi/education_edit.html',
        {'form': form, 'action_title': _("Position edit"),
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda user_id=None, education_id=None: 
    str(get_object_or_404(EducationItem, pk=education_id)), 'emploi/base.html',
     _('Do you really want to delete your education item'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def education_delete(request, user_id=None, education_id=None):
    """education delete"""

    return ain7_generic_delete(request,
        get_object_or_404(EducationItem, pk=education_id),
        reverse(cv_edit, args=[user_id])+'#education',
        _('Education informations deleted successfully.'))

@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def leisure_edit(request, user_id=None, leisure_id=None):
    """leisure edit"""

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    form = LeisureItemForm()

    if leisure_id:
        leisureitem = get_object_or_404(LeisureItem, pk=leisure_id)
        form = LeisureItemForm(instance=leisureitem)

    if request.method == 'POST':
        if leisure_id:
            form = LeisureItemForm(request.POST, instance=leisureitem)
        else:
            form = LeisureItemForm(request.POST)

        if form.is_valid():
            leitem = form.save(commit=False)
            leitem.ain7member = ain7member
            leitem.save()
            request.user.message_set.create(message=_('Modifications have been\
 successfully saved.'))

        return HttpResponseRedirect(reverse(cv_edit, args=[user_id])+'#leisure')

    return render(
        request, 'emploi/leisure_edit.html',
        {'form': form, 'action_title': _("Position edit"),
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda user_id=None, leisure_id=None:
    str(get_object_or_404(LeisureItem, pk=leisure_id)), 'emploi/base.html', 
    _('Do you really want to delete your leisure item'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def leisure_delete(request, user_id=None, leisure_id=None):
    """leisure delete"""

    return ain7_generic_delete(request,
        get_object_or_404(LeisureItem, pk=leisure_id),
        reverse(cv_edit, args=[user_id])+'#leisure',
        _('Leisure informations successfully deleted.'))

@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def publication_edit(request, user_id=None, publication_id=None):
    """publication edit"""

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    form = PublicationItemForm()

    if publication_id:
        publi = get_object_or_404(PublicationItem, pk=publication_id)
        form = PublicationItemForm(instance=publi)

    if request.method == 'POST':
        if publication_id:
            form = PublicationItemForm(request.POST, instance=publi)
        else:
            form = PublicationItemForm(request.POST)

        if form.is_valid():
            publication = form.save(commit=False)
            publication.ain7member = ain7member
            publication.save()
            request.user.message_set.create(message=_('Modifications have been\
 successfully saved.'))

        return HttpResponseRedirect(reverse(cv_edit, 
            args=[user_id])+'#publications')

    return render(
        request, 'emploi/publication_edit.html',
        {'form': form, 'action_title': _("Position edit"),
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda user_id=None, publication_id=None:
     str(get_object_or_404(PublicationItem,pk=publication_id)), 
     'emploi/base.html', 
     _('Do you really want to delete your publication'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def publication_delete(request, user_id=None, publication_id=None):
    """publication delete"""

    return ain7_generic_delete(request,
        get_object_or_404(PublicationItem,pk=publication_id),
        reverse(cv_edit, args=[user_id])+'#publications',
        _('Publication informations deleted successfully.'))

@access_required(groups=['ain7-membre', 'ain7-secretariat'])
def job_details(request, emploi_id):
    """job details"""

    job_offer = get_object_or_404(JobOffer, pk=emploi_id)
    role = check_access(request, request.user, ['ain7-secretariat'])
    if not job_offer.checked_by_secretariat and role:
        request.user.message_set.create(
            message=_('This job offer has to be checked by the secretariat.'))
        return HttpResponseRedirect('/emploi/')

    views = JobOfferView.objects.filter(job_offer=job_offer).count()

    job_offer_view = JobOfferView()
    job_offer_view.job_offer = job_offer
    job_offer_view.person = request.user.person
    job_offer_view.save()
    return render(
        request, 'emploi/job_details.html', {'job': job_offer, 'views': views })

@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def job_edit(request, emploi_id):
    """job edit"""

    job = get_object_or_404(JobOffer, pk=emploi_id)
    role = check_access(request, request.user, ['ain7-secretariat'])
    if not job.checked_by_secretariat and role:
        request.user.message_set.create(
            message=_('This job offer has to be checked by the secretariat.'))
        return HttpResponseRedirect('/emploi/')
    afid = None
    if job.activity_field:
        afid = job.activity_field.pk
    form = JobOfferForm(
        {'reference': job.reference, 'title': job.title,
         'experience': job.experience, 'contract_type': job.contract_type,
         'obsolete': job.obsolete, 'description': job.description,
         'office': job.office.id, 'contact_name': job.contact_name,
         'contact_email': job.contact_email,
         'activity_field': afid })

    if request.method == 'POST':
        form = JobOfferForm(request.POST)
        if form.is_valid():
            form.save(request.user, job_offer=job)
            request.user.message_set.create(
                message=_('Job offer successfully modified.'))
            return HttpResponseRedirect(reverse(job_details, args=[job.id]))

    back = request.META.get('HTTP_REFERER', '/')
    return render(request, 'emploi/job_edit.html', 
        {'form': form, 'job': job, 'back': back})

@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def job_register(request):
    """job register"""

    form = JobOfferForm()

    if request.method == 'POST':
        form = JobOfferForm(request.POST)
        if form.is_valid():
            job_offer = form.save(request.user)

            user_groups = request.user.person.groups.values_list('group__name', flat=True)
            if not 'ain7-secretariat' in user_groups and \
               not 'ain7-admin' in user_groups:

                request.user.message_set.create(
                    message=_('Job offer successfully created. It will now be\
 checked by the secretariat.'))
            return HttpResponseRedirect('/emploi/')
        else:
            request.user.message_set.create(
                message=_('Something was wrong in the form you filled.\
 No modification done.'))
            
    back = request.META.get('HTTP_REFERER', '/')
    return render(request, 'emploi/job_register.html',
        {'form': form, 'back': back})

@access_required(groups=['ain7-membre', 'ain7-secretariat'])
def job_search(request):
    """job search"""

    form = SearchJobForm()
    nb_results_by_page = 25
    list_jobs = False
    paginator = Paginator(JobOffer.objects.none(), nb_results_by_page)
    dosearch = False
    page = 1

    if request.GET.has_key('title') or \
       request.GET.has_key('activity_field') or \
       request.GET.has_key('experience') or \
       request.GET.has_key('contract_type'):
        form = SearchJobForm(request.GET)
        if form.is_valid():
            dosearch = True
            list_jobs = form.search()
            paginator = Paginator(list_jobs, nb_results_by_page)
            try:
                page = int(request.GET.get('page', '1'))
                list_jobs = paginator.page(page).object_list
            except InvalidPage:
                raise Http404

    return render(request, 'emploi/job_search.html',
        {'form': form, 'list_jobs': list_jobs,
         'dosearch': dosearch,
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

@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def jobs_proposals(request):
    """job proposal lists"""

    return render(request, 'emploi/job_proposals.html',
        {'proposals': JobOffer.objects.filter(checked_by_secretariat=False)})

@confirmation_required(lambda job_id=None: 
     str(get_object_or_404(JobOffer, pk=job_id)), 'emploi/base.html', 
     _('Do you confirm the validation of this job proposal'))
@access_required(groups=['ain7-secretariat'])
def job_validate(request, job_id=None):
    """job validate"""

    job = get_object_or_404(JobOffer, pk=job_id)
    # validate
    job.checked_by_secretariat = True
    job.save()
    request.user.message_set.create(
        message=_("Job proposal validated."))
    return HttpResponseRedirect('/emploi/job/proposals/')

@confirmation_required(lambda job_id=None:
     str(get_object_or_404(JobOffer, pk=job_id)), 'emploi/base.html',
     _('Do you really want to delete this job proposal'))
@access_required(groups=['ain7-secretariat'])
def job_delete(request, job_id=None):
    """job delete"""

    job = get_object_or_404(JobOffer, pk=job_id)
    job.delete()
    request.user.message_set.create(
        message=_("Job proposal removed."))
    return HttpResponseRedirect('/emploi/job/proposals/')

