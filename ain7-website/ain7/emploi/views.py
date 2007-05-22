# -*- coding: utf-8
#
# emploi/views.py
#
#   Copyright (C) 2007 AIn7
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

from django.shortcuts import get_object_or_404, render_to_response
from django import newforms as forms
from django.newforms import widgets
from django.core.exceptions import ObjectDoesNotExist

from ain7.annuaire.models import Person
from ain7.annuaire.models import AIn7Member
from ain7.emploi.models import JobOffer

class JobOfferForm(forms.Form):
    reference = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))
    title = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))
    experience = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))
    contract_type = forms.IntegerField(required=False)
    contract_type.widget = forms.Select(choices=JobOffer.JOB_TYPES)
    is_opened = forms.BooleanField(required=False)
    description = forms.CharField(max_length=50, required=False, widget=forms.widgets.Textarea(attrs={'rows':10, 'cols':90}))

class SearchJobForm(forms.Form):
    title = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))

def index(request):
    if not request.user.is_authenticated():
        return render_to_response('annuaire/authentification_needed.html',
                                  {'user': request.user})
    # TODO : renseigner liste_emploiss avec la liste des emplois
    # correspondant aux filières qui intéressent la personne
    p = Person.objects.get(user=request.user.id)
    try:
        ain7member = AIn7Member.objects.get(person=p)
    except ObjectDoesNotExist:
        ain7member = None
    return render_to_response('emploi/index.html', {'user': request.user, 'AIn7Member': ain7member})


def cv_details(request, user_id):

    if not request.user.is_authenticated():
        return render_to_response('annuaire/authentification_needed.html',
                                  {'user': request.user})
    
    p = get_object_or_404(Person, user=user_id)
    return render_to_response('emploi/cv_details.html',
                              {'person': p, 'user': request.user})


def cv_edit(request, user_id=None):

    if not request.user.is_authenticated():
        return render_to_response('annuaire/authentification_needed.html',
                                  {'user': request.user})
    # TODO : un joli formulaire...
    # return render_to_response('emploi/cv_edit.html',
    #                           {'form': form, 'user': request.user,  })
    return render_to_response('emploi/cv_edit.html', {'user': request.user,  })

def job_details(request,emploi_id):

    if not request.user.is_authenticated():
        return render_to_response('annuaire/authentification_needed.html',
                                  {'user': request.user})

    j = get_object_or_404(JobOffer, pk=emploi_id)

    return render_to_response('emploi/job_details.html',{'job': j, 'user': request.user})


def job_edit(request, emploi_id):

    if not request.user.is_authenticated():
        return render_to_response('annuaire/authentification_needed.html',
                                  {'user': request.user})

    j = get_object_or_404(JobOffer, pk=emploi_id)

    if request.method == 'POST':
        f = JobOfferForm(request.POST)
        if f.is_valid():
            j.reference = request.POST['reference']
            j.title = request.POST['title']
            j.description = request.POST['description']
            j.experience = request.POST['experience']
            j.contract_type = request.POST['contract_type']
            j.save()

    f = JobOfferForm({'reference': j.reference, 'title': j.title, 'description': j.description, 
        'experience': j.experience, 'contract_type': j.contract_type})
    return render_to_response('emploi/job_edit.html',{'form': f, 'user': request.user})

def job_register(request):

    if not request.user.is_authenticated():
        return render_to_response('annuaire/authentification_needed.html',
                                  {'user': request.user})

    if request.method == 'POST':
        f = JobOfferForm(request.POST)
        if f.is_valid():
            job_offer = JobOffer()
            job_offer.reference = request.POST['reference']
            job_offer.title = request.POST['title']
            job_offer.description = request.POST['description']
            job_offer.experience = request.POST['experience']
            job_offer.contract_type = request.POST['contract_type']
            job_offer.save()

            return render_to_response('emploi/job_register.html',{'user': request.user})

    f = JobOfferForm({})
    return render_to_response('emploi/job_register.html',{'form': f, 'user': request.user})

def job_search(request):

    if not request.user.is_authenticated():
        return render_to_response('annuaire/authentification_needed.html',
                                  {'user': request.user})

    if request.method == 'POST':
        form = SearchJobForm(request.POST)
        if form.is_valid():
                    list_jobs = JobOffer.objects.filter(title__icontains=form.clean_data['title'])
                    return render_to_response('emploi/job_search.html', {'form': form, 'list_jobs': list_jobs, 'request': request, 'user': request.user})

    else:
        f = SearchJobForm()
        return render_to_response('emploi/job_search.html', {'form': f , 'user': request.user})

