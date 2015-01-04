# -*- coding: utf-8
"""
 ain7/emploi/views.py
"""
#
#   Copyright © 2007-2015 AIn7 Devel Team
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

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _

from ain7.pages.models import Text
from ain7.annuaire.models import Person, AIn7Member
from ain7.decorators import access_required, confirmation_required
from ain7.emploi.filters import JobOfferFilter
from ain7.emploi.models import (
    JobOffer, Position, EducationItem, LeisureItem,
    PublicationItem, JobOfferView
    )
from ain7.utils import ain7_generic_delete, check_access


@access_required(groups=['ain7-membre', 'ain7-secretariat'])
@login_required
def index(request):
    """index page"""

    job_offers = JobOfferFilter(
        request.GET,
        queryset=JobOffer.objects.filter(obsolete=False),
    )

    text = Text.objects.get(textblock__shortname='emploi')

    return render(request, 'emploi/index.html', {
        'job_offers': job_offers,
        'text': text,
        }
    )


@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def position_edit(request, user_id=None, position_id=None):
    """position edit"""

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    position = None
    if position_id:
        position = get_object_or_404(Position, pk=position_id)

    PositionForm = modelform_factory(Position, exclude=('ain7member',))
    form = PositionForm(request.POST or None, instance=position)

    if request.method == 'POST' and form.is_valid():
        pos = form.save(commit=False)
        pos.ain7member = ain7member
        pos.save()
        messages.success(
            request,
            _('Modifications have been successfully saved.')
        )

        return redirect('cv-edit', user_id)

    return render(request, 'emploi/position_edit.html', {
        'form': form,
        'action_title': _("Position edit"),
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@confirmation_required(lambda user_id=None, position_id=None:
    str(get_object_or_404(Position, pk=position_id)), 'emploi/base.html',
     _('Do you really want to delete your position'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def position_delete(request, user_id=None, position_id=None):
    """position delete"""

    return ain7_generic_delete(
        request,
        get_object_or_404(Position, pk=position_id),
        reverse(cv_edit, args=[user_id])+'#prof_exp',
        _('Position successfully deleted.')
    )


@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def education_edit(request, user_id=None, education_id=None):
    """education edit"""

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    educationitem = None
    if education_id:
        educationitem = get_object_or_404(EducationItem, pk=education_id)

    EducationItemForm = modelform_factory(
        EducationItem,
        exclude=('ain7member',)
    )
    form = EducationItemForm(request.POST or None, instance=educationitem)

    if request.method == 'POST' and form.is_valid():
        editem = form.save(commit=False)
        editem.ain7member = ain7member
        editem.save()
        messages.success(
            request,
            _('Modifications have been successfully saved.')
        )

        return redirect('cv-edit', user_id)

    return render(request, 'emploi/education_edit.html', {
        'form': form,
        'action_title': _("Position edit"),
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@confirmation_required(lambda user_id=None, education_id=None: 
    str(get_object_or_404(EducationItem, pk=education_id)), 'emploi/base.html',
     _('Do you really want to delete your education item'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def education_delete(request, user_id=None, education_id=None):
    """education delete"""

    return ain7_generic_delete(
        request,
        get_object_or_404(EducationItem, pk=education_id),
        reverse(cv_edit, args=[user_id])+'#education',
        _('Education informations deleted successfully.')
    )


@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def leisure_edit(request, user_id=None, leisure_id=None):
    """leisure edit"""

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    leisureitem = None
    if leisure_id:
        leisureitem = get_object_or_404(LeisureItem, pk=leisure_id)

    LeisureItemForm = modelform_factory(LeisureItem, exclude=('ain7member',))
    form = LeisureItemForm(request.POST or None, instance=leisureitem)

    if request.method == 'POST' and form.is_valid():
        leitem = form.save(commit=False)
        leitem.ain7member = ain7member
        leitem.save()
        messages.success(
            request,
            _('Modifications have been successfully saved.')
        )

        return redirect('cv-edit', user_id)

    return render(request, 'emploi/leisure_edit.html', {
        'form': form,
        'action_title': _("Position edit"),
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@confirmation_required(lambda user_id=None, leisure_id=None:
    str(get_object_or_404(LeisureItem, pk=leisure_id)), 'emploi/base.html', 
    _('Do you really want to delete your leisure item'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def leisure_delete(request, user_id=None, leisure_id=None):
    """leisure delete"""

    return ain7_generic_delete(
        request,
        get_object_or_404(LeisureItem, pk=leisure_id),
        reverse(cv_edit, args=[user_id])+'#leisure',
        _('Leisure informations successfully deleted.')
    )


@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def publication_edit(request, user_id=None, publication_id=None):
    """publication edit"""

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    publi = None
    if publication_id:
        publi = get_object_or_404(PublicationItem, pk=publication_id)

    PublicationItemForm = modelform_factory(
        PublicationItem,
        exclude=('ain7member',)
    )
    form = PublicationItemForm(request.POST or None, instance=publi)

    if request.method == 'POST' and form.is_valid():
        publication = form.save(commit=False)
        publication.ain7member = ain7member
        publication.save()
        messages.success(
            request,
            _('Modifications have been successfully saved.')
        )

        return redirect('cv-edit', user_id)

    return render(request, 'emploi/publication_edit.html', {
        'form': form,
        'action_title': _("Position edit"),
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@confirmation_required(lambda user_id=None, publication_id=None:
     str(get_object_or_404(PublicationItem,pk=publication_id)), 
     'emploi/base.html', 
     _('Do you really want to delete your publication'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'], allow_myself=True)
def publication_delete(request, user_id=None, publication_id=None):
    """publication delete"""

    return ain7_generic_delete(
        request,
        get_object_or_404(PublicationItem, pk=publication_id),
        reverse(cv_edit, args=[user_id])+'#publications',
        _('Publication informations deleted successfully.')
    )


@access_required(groups=['ain7-membre', 'ain7-secretariat'])
def job_details(request, job_id):
    """job details"""

    job_offer = get_object_or_404(JobOffer, pk=job_id)
    role = check_access(request, request.user, ['ain7-secretariat'])
    if not job_offer.checked_by_secretariat and role:
        messages.info(
            request,
            _('This job offer has to be checked by the secretariat.')
        )
        return redirect('job-index')

    views = JobOfferView.objects.filter(job_offer=job_offer).count()

    job_offer_view = JobOfferView()
    job_offer_view.job_offer = job_offer
    job_offer_view.person = request.user.person
    job_offer_view.save()
    return render(request, 'emploi/job_details.html', {
        'job': job_offer,
        'views': views,
        }
    )


@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def job_edit(request, job_id=None):
    """job edit"""

    job = None
    if job_id:
        job = get_object_or_404(JobOffer, pk=job_id)

    JobOfferForm = modelform_factory(JobOffer, exclude=())
    form = JobOfferForm(request.POST or None, instance=job)

    if request.method == 'POST' and form.is_valid():
        job = form.save()
        messages.success(request, _('Job offer successfully modified.'))

        return redirect('job-details', job.id)

    return render(request, 'emploi/job_edit.html', {
        'form': form,
        'job': job,
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@access_required(groups=['ain7-membre', 'ain7-secretariat'])
def job_search(request):
    """job search"""

    filter = JobOfferFilter(
        request.GET,
        queryset=JobOffer.objects.filter(obsolete=False)
    )

    return render(request, 'emploi/job_search.html', {
        'filter': filter,
        }
    )


@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def jobs_proposals(request):
    """job proposal lists"""

    return render(request, 'emploi/job_proposals.html', {
        'proposals': JobOffer.objects.filter(checked_by_secretariat=False),
        }
    )


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
    messages.success(request, _("Job proposal validated."))
    return redirect('jobs-proposals')


@confirmation_required(lambda job_id=None:
     str(get_object_or_404(JobOffer, pk=job_id)), 'emploi/base.html',
     _('Do you really want to delete this job proposal'))
@access_required(groups=['ain7-secretariat'])
def job_delete(request, job_id=None):
    """job delete"""

    job = get_object_or_404(JobOffer, pk=job_id)
    job.delete()
    messages.success(request, _("Job proposal removed."))
    return redirect('jobs-proposals')
