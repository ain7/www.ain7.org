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
from django.contrib.auth.decorators import login_required
from django import newforms as forms
from django.newforms import widgets
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect

from ain7.annuaire.models import Person, AIn7Member, Track
from ain7.decorators import confirmation_required
from ain7.emploi.models import JobOffer, Position, EducationItem, LeisureItem
from ain7.emploi.models import Office, Company, PublicationItem

class JobOfferForm(forms.Form):
    reference = forms.CharField(label=_('reference'),max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))
    title = forms.CharField(label=_('title'),max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))
    experience = forms.CharField(label=_('experience'),max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))
    contract_type = forms.IntegerField(label=_('contract type'),required=False)
    contract_type.widget = forms.Select(choices=JobOffer.JOB_TYPES)
    is_opened = forms.BooleanField(label=_('is opened'),required=False)
    description = forms.CharField(label=_('description'),max_length=500, required=False, widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':125}))

class SearchJobForm(forms.Form):
    title = forms.CharField(label=_('title'),max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))
    allTracks = forms.BooleanField(label=_('all tracks'), required=False)
    track = forms.ModelMultipleChoiceField(
        label=_('track'), queryset=Track.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super(SearchJobForm, self).__init__(*args, **kwargs)

    def clean_track(self):
        return self.clean_data['track']

    def search(self):
        maxTrackId = Track.objects.latest('id').id + 1
        # si des filières sont sélectionnées mais pas le joker
        # on filtre par rapport à ces filières
        jobsMatchingTracks = []
        if (not self.clean_data['allTracks'])\
               and len(self.clean_data['track'])>0:
            for track in self.clean_data['track']:
                jobsMatchingTracks.extend(track.jobs.all())
        else:
            jobsMatchingTracks = JobOffer.objects.all()
        # maintenant on filtre ces jobs par rapport au titre saisi
        matchingJobs = []
        if self.clean_data['title']:
            for job in jobsMatchingTracks:
                if str(self.clean_data['title']) in job.title:
                    matchingJobs.append(job)
        else:
            matchingJobs = jobsMatchingTracks
        return matchingJobs


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
    return _render_response(request, 'emploi/index.html',
                            {'ain7member': ain7member, 'liste_emplois': jobs})

@login_required
def cv_details(request, user_id):

    p = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)
    return _render_response(request, 'emploi/cv_details.html',
                            {'person': p, 'ain7member': ain7member})

@login_required
def cv_edit(request, user_id=None):

    p = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)
    return _render_response(request, 'emploi/cv_edit.html',
                            {'person': p, 'ain7member': ain7member})

def _generic_edit(request, user_id, obj, redirectPage, msgDone):

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    # 1er passage : on propose un formulaire avec les données actuelles
    if request.method == 'GET':
        PosForm = forms.models.form_for_instance(obj,
            formfield_callback=_form_callback)
        f = PosForm()
        return _render_response(request, redirectPage,
                                {'form': f, 'action': 'edit',
                                 'ain7member': ain7member})

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        PosForm = forms.models.form_for_instance(obj,
            formfield_callback=_form_callback)
        f = PosForm(request.POST.copy())
        if f.is_valid():
            f.clean_data['ain7member'] = ain7member
            f.save()
            request.user.message_set.create(message=msgDone)
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            # pour avoir le détail des champs mal remplis :
            # request.user.message_set.create(message=str(f.errors))
        return HttpResponseRedirect('/emploi/%s/cv/edit/' % user_id)

def _generic_delete(request, user_id, obj, msgDone):

    obj.delete()

    request.user.message_set.create(message=msgDone)

    return HttpResponseRedirect('/emploi/%s/cv/edit/' % user_id)

def _generic_add(request, user_id, objectType, redirectPage, msgDone):

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        PosForm = forms.models.form_for_model(objectType,
            formfield_callback=_form_callback)
        f = PosForm()
        return _render_response(request, redirectPage,
                                {'form': f, 'action': 'create',
                                 'ain7member':ain7member, 'person': person})

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        PosForm = forms.models.form_for_model(objectType,
            formfield_callback=_form_callback)
        f = PosForm(request.POST.copy())
        if f.is_valid():
            f.clean_data['ain7member'] = ain7member
            f.save()
            request.user.message_set.create(message=msgDone)
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            # TODO pour avoir le détail des champs mal remplis :
            # request.user.message_set.create(message=str(f.errors))
        return HttpResponseRedirect('/emploi/%s/cv/edit/' % user_id)

@login_required
def position_edit(request, user_id=None, position_id=None):

    return _generic_edit(request, user_id,
                         get_object_or_404(Position, pk=position_id),
                         'emploi/position_edit.html',
                         _('Position informations updated successfully.'))

@confirmation_required(lambda user_id=None, position_id=None: str(get_object_or_404(Position, pk=position_id)), 'emploi/base.html', _('Do you really want to delete your position'))
@login_required
def position_delete(request, user_id=None, position_id=None):

    return _generic_delete(request, user_id,
                           get_object_or_404(Position, pk=position_id),
                           _('Position successfully deleted.'))

@login_required
def position_add(request, user_id=None):

    return _generic_add(request, user_id, Position, 'emploi/position_edit.html',
                        _('Position successfully added.'))

@login_required
def education_edit(request, user_id=None, education_id=None):

    return _generic_edit(request, user_id,
                         get_object_or_404(EducationItem, pk=education_id),
                         'emploi/education_edit.html',
                         _('Education informations updated successfully.'))

@confirmation_required(lambda user_id=None, education_id=None: str(get_object_or_404(EducationItem, pk=education_id)), 'emploi/base.html', _('Do you really want to delete your education item'))
@login_required
def education_delete(request, user_id=None, education_id=None):

    return _generic_delete(request, user_id,
                           get_object_or_404(EducationItem, pk=education_id),
                           _('Education informations deleted successfully.'))

@login_required
def education_add(request, user_id=None):

    return _generic_add(request, user_id, EducationItem,
                        'emploi/education_edit.html',
                        _('Education informations successfully added.'))

@login_required
def leisure_edit(request, user_id=None, leisure_id=None):

    return _generic_edit(request, user_id,
                         get_object_or_404(LeisureItem, pk=leisure_id),
                         'emploi/leisure_edit.html',
                         _('Leisure informations updated successfully.'))

@confirmation_required(lambda user_id=None, leisure_id=None: str(get_object_or_404(LeisureItem, pk=leisure_id)), 'emploi/base.html', _('Do you really want to delete your leisure item'))
@login_required
def leisure_delete(request, user_id=None, leisure_id=None):

    return _generic_delete(request, user_id,
                           get_object_or_404(LeisureItem, pk=leisure_id),
                           _('Leisure informations successfully deleted.'))

@login_required
def leisure_add(request, user_id=None):

    return _generic_add(request, user_id, LeisureItem,
                        'emploi/leisure_edit.html',
                        _('Leisure informations successfully added.'))

@login_required
def publication_edit(request, user_id=None, publication_id=None):

    return _generic_edit(request, user_id,
                         get_object_or_404(PublicationItem, pk=publication_id),
                         'emploi/publication_edit.html',
                         _('Publication informations updated successfully.'))

@confirmation_required(lambda user_id=None, publication_id=None: str(get_object_or_404(PublicationItem,pk=publication_id)), 'emploi/base.html', _('Do you really want to delete your publication'))
@login_required
def publication_delete(request, user_id=None, publication_id=None):

    return _generic_delete(request, user_id,
                           get_object_or_404(PublicationItem,pk=publication_id),
                           _('Publication informations deleted successfully.'))

@login_required
def publication_add(request, user_id=None):

    return _generic_add(request, user_id, PublicationItem,
                        'emploi/publication_edit.html',
                        _('Publication informations successfully added.'))

@login_required
def office_create(request, user_id=None):

    p = get_object_or_404(Person, user=user_id)

    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        OfficeForm = forms.models.form_for_model(Office)
        f = OfficeForm()
        return _render_response(request, 'emploi/office_create.html',
                                {'form': f, 'person': p, 'object': 'office'})

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        OfficeForm = forms.models.form_for_model(Office)
        f = OfficeForm(request.POST.copy())
        if f.is_valid():
            f.save()
        return _render_response(request, 'emploi/cv_edit.html', {'person': p})

@login_required
def company_create(request, user_id=None):

    p = get_object_or_404(Person, user=user_id)

    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        CompanyForm = forms.models.form_for_model(Company)
        CompanyForm.base_fields['size'].widget =\
            forms.Select(choices=Company.COMPANY_SIZE)
        f = CompanyForm()
        return _render_response(request, 'emploi/office_create.html',
                                {'form': f, 'person': p, 'object': 'company'})

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        CompanyForm = forms.models.form_for_model(Company)
        f = CompanyForm(request.POST.copy())
        if f.is_valid():
            f.save()
        return _render_response(request, 'emploi/cv_edit.html', {'person': p})

@login_required
def job_details(request,emploi_id):

    j = get_object_or_404(JobOffer, pk=emploi_id)

    j.nb_views = j.nb_views + 1
    j.save()

    return _render_response(request, 'emploi/job_details.html', {'job': j})

@login_required
def job_edit(request, emploi_id):

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

            return HttpResponseRedirect('/emploi/job/%s/' % (j.id) )

    f = JobOfferForm({'reference': j.reference, 'title': j.title, 'description': j.description, 
        'experience': j.experience, 'contract_type': j.contract_type})

    return _render_response(request, 'emploi/job_edit.html', {'form': f})

@login_required
def job_register(request):

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

            return HttpResponseRedirect('/emploi/job/%s/' % (job_offer.id))

    f = JobOfferForm({})
    return _render_response(request, 'emploi/job_register.html', {'form': f})

@login_required
def job_search(request):

    if request.method == 'POST':
        form = SearchJobForm(request.POST)
        if form.is_valid():
            list_jobs = form.search()
            return _render_response(request, 'emploi/job_search.html', 
                                    {'form': form, 'list_jobs': list_jobs,
                                     'request': request})
        
    else:
        form = SearchJobForm()
        return _render_response(request, 'emploi/job_search.html',
                                {'form': form})

@login_required
def company_details(request, company_id):

    company = get_object_or_404(Company, pk=company_id)
    offices = Office.objects.filter(company=company)

    return _render_response(request, 'emploi/company_details.html',
                            {'company': company, 'offices': offices})

# une petite fonction pour exclure les champs
# person user ain7member
# des formulaires créés avec form_for_model et form_for_instance
def _form_callback(f, **args):
    exclude_fields = ('person', 'user', 'ain7member')
    if f.name in exclude_fields:
        return None
    return f.formfield(**args)

# pour alléger les appels à render_to_response
# http://www.djangosnippets.org/snippets/3/
def _render_response(req, *args, **kwargs):
    kwargs['context_instance'] = RequestContext(req)
    return render_to_response(*args, **kwargs)

