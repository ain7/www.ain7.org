# -*- coding: utf-8
"""
 ain7/emploi/views.py
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

from ain7.annuaire.models import Person, AIn7Member
from ain7.decorators import confirmation_required
from ain7.emploi.models import JobOffer, Position, EducationItem, DiplomaItem, \
                               LeisureItem, PublicationItem, JobOfferView
from ain7.emploi.forms import PositionForm, EducationItemForm, \
                              LeisureItemForm, \
                              PublicationItemForm, JobOfferForm, SearchJobForm
from ain7.utils import ain7_render_to_response
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
    return ain7_render_to_response(request, 'emploi/index.html',
        {'ain7member': ain7member,
         'liste_emplois': liste_emplois})

@login_required
def cv_details(request, user_id):
    """cvs details"""

    is_myself = int(request.user.id) == int(user_id)

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access and not is_myself:
        return access

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    return ain7_render_to_response(request, 'emploi/cv_details.html',
        {'person': person, 'ain7member': ain7member})

@login_required
def cv_edit(request, user_id=None):
    """cv edit"""

    is_myself = int(request.user.id) == int(user_id)

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access and not is_myself:
        return access

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    return ain7_render_to_response(request, 'emploi/cv_edit.html',
        {'person': person, 'ain7member': ain7member})

@login_required
def position_edit(request, user_id=None, position_id=None):
    """position edit"""

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access and not is_myself:
        return access

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

    return ain7_render_to_response(
        request, 'emploi/position_edit.html',
        {'form': form, 'action_title': _("Position edit"),
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda user_id=None, position_id=None: 
    str(get_object_or_404(Position, pk=position_id)), 'emploi/base.html',
     _('Do you really want to delete your position'))
@login_required
def position_delete(request, user_id=None, position_id=None):
    """position delete"""

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access and not is_myself:
        return access

    return ain7_generic_delete(request,
        get_object_or_404(Position, pk=position_id),
        reverse(cv_edit, args=[user_id])+'#prof_exp',
        _('Position successfully deleted.'))

@login_required
def education_edit(request, user_id=None, education_id=None):
    """education edit"""

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access and not is_myself:
        return access

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

    return ain7_render_to_response(
        request, 'emploi/education_edit.html',
        {'form': form, 'action_title': _("Position edit"),
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda user_id=None, education_id=None: 
    str(get_object_or_404(EducationItem, pk=education_id)), 'emploi/base.html',
     _('Do you really want to delete your education item'))
@login_required
def education_delete(request, user_id=None, education_id=None):
    """education delete"""

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access and not is_myself:
        return access

    return ain7_generic_delete(request,
        get_object_or_404(EducationItem, pk=education_id),
        reverse(cv_edit, args=[user_id])+'#education',
        _('Education informations deleted successfully.'))

@confirmation_required(lambda user_id=None, diploma_id=None:
    str(get_object_or_404(DiplomaItem, pk=diploma_id)), 'emploi/base.html',
    _('Do you really want to delete your diploma item'))
@login_required
def diploma_delete(request, user_id=None, diploma_id=None):
    """diploma delete"""

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user,
        ['ain7-ca','ain7-secretariat'])
    if access and not is_myself:
        return access

    return ain7_generic_delete(request,
        get_object_or_404(DiplomaItem, pk=diploma_id),
        reverse(cv_edit, args=[user_id])+'#diploma',
        _('Diploma informations deleted successfully.'))

@login_required
def leisure_edit(request, user_id=None, leisure_id=None):
    """leisure edit"""

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user,
        ['ain7-ca','ain7-secretariat'])
    if access and not is_myself:
        return access

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

    return ain7_render_to_response(
        request, 'emploi/leisure_edit.html',
        {'form': form, 'action_title': _("Position edit"),
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda user_id=None, leisure_id=None:
    str(get_object_or_404(LeisureItem, pk=leisure_id)), 'emploi/base.html', 
    _('Do you really want to delete your leisure item'))
@login_required
def leisure_delete(request, user_id=None, leisure_id=None):
    """leisure delete"""

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user,
        ['ain7-ca',  'ain7-secretariat'])
    if access and not is_myself:
        return access

    return ain7_generic_delete(request,
        get_object_or_404(LeisureItem, pk=leisure_id),
        reverse(cv_edit, args=[user_id])+'#leisure',
        _('Leisure informations successfully deleted.'))

@login_required
def publication_edit(request, user_id=None, publication_id=None):
    """publication edit"""

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access and not is_myself:
        return access

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

    return ain7_render_to_response(
        request, 'emploi/publication_edit.html',
        {'form': form, 'action_title': _("Position edit"),
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda user_id=None, publication_id=None:
     str(get_object_or_404(PublicationItem,pk=publication_id)), 
     'emploi/base.html', 
     _('Do you really want to delete your publication'))
@login_required
def publication_delete(request, user_id=None, publication_id=None):
    """publication delete"""

    is_myself = int(request.user.id) == int(user_id)
    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access and not is_myself:
        return access

    return ain7_generic_delete(request,
        get_object_or_404(PublicationItem,pk=publication_id),
        reverse(cv_edit, args=[user_id])+'#publications',
        _('Publication informations deleted successfully.'))

@login_required
def job_details(request, emploi_id):
    """job details"""

    access = check_access(request, request.user,
        ['ain7-membre','ain7-secretariat'])
    if access:
        return access

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
    return ain7_render_to_response(
        request, 'emploi/job_details.html', {'job': job_offer, 'views': views })

@login_required
def job_edit(request, emploi_id):
    """job edit"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

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
    return ain7_render_to_response(request, 'emploi/job_edit.html', 
        {'form': form, 'job': job, 'back': back})

@login_required
def job_register(request):
    """job register"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    form = JobOfferForm()

    if request.method == 'POST':
        form = JobOfferForm(request.POST)
        if form.is_valid():
            job_offer = form.save(request.user)

            user_groups = request.user.person.groups.values_list('group__name', flat=True)
            if not 'ain7-secretariat' in user_groups and \
               not 'ain7-admin' in user_groups:

                # create the notification
                notif = Notification(details='',
                    title=_('Proposal for job offer'),
                    job_proposal = job_offer)
                notif.logged_save(request.user.person)
                request.user.message_set.create(
                    message=_('Job offer successfully created. It will now be\
 checked by the secretariat.'))
            return HttpResponseRedirect('/emploi/')
        else:
            request.user.message_set.create(
                message=_('Something was wrong in the form you filled.\
 No modification done.'))
            
    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 'emploi/job_register.html',
        {'form': form, 'back': back})

@login_required
def job_search(request):
    """job search"""

    access = check_access(request, request.user,
        ['ain7-membre', 'ain7-secretariat'])
    if access:
        return access

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

    return ain7_render_to_response(request, 'emploi/job_search.html',
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

@login_required
def jobs_proposals(request):
    """job proposal lists"""

    access = check_access(request, request.user,
        ['ain7-ca', 'ain7-secretariat'])
    if access:
        return access

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access
    return ain7_render_to_response(request, 'emploi/job_proposals.html',
        {'proposals': JobOffer.objects.filter(checked_by_secretariat=False)})

@confirmation_required(lambda job_id=None: 
     str(get_object_or_404(JobOffer, pk=job_id)), 'emploi/base.html', 
     _('Do you confirm the validation of this job proposal'))
@login_required
def job_validate(request, job_id=None):
    """job validate"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access
    job = get_object_or_404(JobOffer, pk=job_id)
    # validate
    job.checked_by_secretariat = True
    job.save()
    request.user.message_set.create(
        message=_("Job proposal validated."))
    # remove notification
    notif = job.notification.all()
    if notif:
        notif[0].delete()
        request.user.message_set.create(
            message=_("Corresponding notification removed."))
    return HttpResponseRedirect('/emploi/job/proposals/')

@confirmation_required(lambda job_id=None:
     str(get_object_or_404(JobOffer, pk=job_id)), 'emploi/base.html',
     _('Do you really want to delete this job proposal'))
@login_required
def job_delete(request, job_id=None):
    """job delete"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access
    job = get_object_or_404(JobOffer, pk=job_id)
    # remove notification
    notif = job.notification.all()
    if notif:
        notif[0].delete()
        request.user.message_set.create(
            message=_("Corresponding notification removed."))
    # validate
    job.delete()
    request.user.message_set.create(
        message=_("Job proposal removed."))
    return HttpResponseRedirect('/emploi/job/proposals/')

