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
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect

from ain7.annuaire.models import Person, AIn7Member
from ain7.emploi.models import JobOffer, Position, EducationItem, LeisureItem, PublicationItem
from ain7.emploi.models import Office, Company

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

def index(request):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"},
                                  context_instance=RequestContext(request))
    p = Person.objects.get(user=request.user.id)
    # TODO : quand le modèle sera ok il faudra filtrer par filière souhaitée
    jobs = JobOffer.objects.all()
    return render_to_response('emploi/index.html',
                              {'user': request.user,
                               'liste_emplois': jobs},
                               context_instance=RequestContext(request))


def cv_details(request, user_id):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"},
                                   context_instance=RequestContext(request))
    p = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)
    return render_to_response('emploi/cv_details.html',
                              {'person': p, 'user': request.user,
                               'AIn7Member': ain7member},
                              context_instance=RequestContext(request))


def cv_edit(request, user_id=None):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"},
                                  context_instance=RequestContext(request))
    p = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)
    return render_to_response('emploi/cv_edit.html',
                              {'person': p, 'user': request.user,
                               'AIn7Member': ain7member},
                              context_instance=RequestContext(request))

# une petite fonction pour exclure les champs person et user des formulaires
# créés avec form_for_model et form_for_instance
def form_callback(f, **args):
  if f.name == "person" or f.name == "user":
    return None
  return f.formfield(**args)

def position_edit(request, user_id=None, position_id=None):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"},
                                   context_instance=RequestContext(request))

    p = get_object_or_404(Person, user=user_id)
    position = get_object_or_404(Position, pk=position_id)
    # 1er passage : on propose un formulaire avec les données actuelles
    if request.method == 'GET':
        PosForm = forms.models.form_for_instance(position,
            formfield_callback=form_callback)
        f = PosForm()
        return render_to_response('emploi/position_edit.html',
                                 {'form': f, 'user': request.user, 
                                  'action': "edit"},
                                  context_instance=RequestContext(request))

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        PosForm = forms.models.form_for_instance(position,
            formfield_callback=form_callback)
        f = PosForm(request.POST.copy())
        if f.is_valid():
            f.clean_data['person'] = p
            f.save()

        request.user.message_set.create(message=_("Position informations updated successfully."))

        return HttpResponseRedirect('/emploi/%s/cv/edit/' % (request.user.id))

def position_delete(request, user_id=None, position_id=None):
    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"},
                                   context_instance=RequestContext(request))

    p = get_object_or_404(Person, user=user_id)
    position = get_object_or_404(Position, pk=position_id)

    # 1er passage: on demande confirmation
    if request.method != 'POST':
        msg = _("Do you really want to delete this professional experience?")
        description = position.fonction + " " + _("for")
        description+= str(position.office) + " ("
        description+= str(position.office.company) + ")"
        return render_to_response('pages/confirm.html',
                                 {'message': msg, 'description': description,
                                  'section': "emploi/base.html", 
                                  'user': request.user},
                                  context_instance=RequestContext(request))

    # 2eme passage: on supprime si c'est confirmé
    else:
        if request.POST['choice']=="1":
            position.delete()
            request.user.message_set.create(message=_("Position successfully deleted."))

        return HttpResponseRedirect('/emploi/%s/cv/edit/' % (request.user.id))

def position_add(request, user_id=None):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"},
                                   context_instance=RequestContext(request))

    p = get_object_or_404(Person, user=user_id)

    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        PosForm = forms.models.form_for_model(Position,
            formfield_callback=form_callback)
        f = PosForm()
        return render_to_response('emploi/position_edit.html',
                                 {'form': f, 'person': p, 'user': request.user,
                                  'action': "create"},
                                  context_instance=RequestContext(request))

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        PosForm = forms.models.form_for_model(Position,
            formfield_callback=form_callback)
        f = PosForm(request.POST.copy())
        if f.is_valid():
            f.clean_data['person'] = p
            f.save()

        request.user.message_set.create(message=_("Position successfully added."))

        return HttpResponseRedirect('/emploi/%s/cv/edit/' % (request.user.id))

def education_edit(request, user_id=None, education_id=None):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"},
                                   context_instance=RequestContext(request))

    p = get_object_or_404(Person, user=user_id)
    education = get_object_or_404(EducationItem, pk=education_id)

    # 1er passage : on propose un formulaire avec les données actuelles
    if request.method == 'GET':
        EducForm = forms.models.form_for_instance(education,
            formfield_callback=form_callback)
        f = EducForm()
        return render_to_response('emploi/education_edit.html',
                                 {'form': f, 'user': request.user,
                                  'action': "edit"},
                                  context_instance=RequestContext(request))

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        EducForm = forms.models.form_for_instance(education,
            formfield_callback=form_callback)
        f = EducForm(request.POST.copy())
        if f.is_valid():
            f.clean_data['person'] = p
            f.save()

            request.user.message_set.create(message=_("Education informations updated successfully."))

        return HttpResponseRedirect('/emploi/%s/cv/edit/' % (request.user.id))

def education_delete(request, user_id=None, education_id=None):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"})

    p = get_object_or_404(Person, user=user_id)
    education = get_object_or_404(EducationItem, pk=education_id)

    # 1er passage: on demande confirmation
    if request.method != 'POST':
        msg = _("Do you really want to delete this education item?")
        description = education.school + " : "
        description+= education.diploma
        return render_to_response('pages/confirm.html',
                                 {'message': msg, 'description': description,
                                  'section': "emploi/base.html"},
                                  context_instance=RequestContext(request))

    # 2eme passage: on supprime si c'est confirmé
    else:
        if request.POST['choice']=="1":
            education.delete()
            request.user.message_set.create(message=_("Education informations deleted successfully."))
        return HttpResponseRedirect('/emploi/%s/cv/edit/' % (request.user.id))

def education_add(request, user_id=None):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"},
                                   context_instance=RequestContext(request))

    p = get_object_or_404(Person, user=user_id)

    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        EducForm = forms.models.form_for_model(EducationItem,
            formfield_callback=form_callback)
        f = EducForm()
        return render_to_response('emploi/education_edit.html',
                                 {'form': f, 'person': p, 'user': request.user,
                                  'action': "create"},
                                  context_instance=RequestContext(request))

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        EducForm = forms.models.form_for_model(EducationItem,
            formfield_callback=form_callback)
        f = EducForm(request.POST.copy())
        if f.is_valid():
            f.clean_data['person'] = p
            f.save()

            request.user.message_set.create(message=_("Education informations successfully added."))

        return HttpResponseRedirect('/emploi/%s/cv/edit/' % (request.user.id))

def leisure_edit(request, user_id=None, leisure_id=None):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"},
                                   context_instance=RequestContext(request))

    p = get_object_or_404(Person, user=user_id)
    leisure = get_object_or_404(LeisureItem, pk=leisure_id)

    # 1er passage : on propose un formulaire avec les données actuelles
    if request.method == 'GET':
        LeisureForm = forms.models.form_for_instance(leisure,
            formfield_callback=form_callback)
        f = LeisureForm()
        return render_to_response('emploi/leisure_edit.html',
                                 {'form': f, 'user': request.user, 
                                  'action': "edit"},
                                  context_instance=RequestContext(request))

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        LeisureForm = forms.models.form_for_instance(leisure,
            formfield_callback=form_callback)
        f = LeisureForm(request.POST.copy())
        if f.is_valid():
            f.clean_data['person'] = p
            f.save()

            request.user.message_set.create(message=_("Leisure informations updated successfully."))

            return HttpResponseRedirect('/emploi/%s/cv/edit/' % (request.user.id))

        return render_to_response('emploi/cv_edit.html',
                                 {'person': p, 'user': request.user},
                                  context_instance=RequestContext(request))

def leisure_delete(request, user_id=None, leisure_id=None):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"},
                                   context_instance=RequestContext(request))

    p = get_object_or_404(Person, user=user_id)
    leisure = get_object_or_404(LeisureItem, pk=leisure_id)

    # 1er passage: on demande confirmation
    if request.method != 'POST':
        msg = _("Do you really want to delete this leisure item?")
        description = leisure.title + " - "
        description+= leisure.detail
        return render_to_response('pages/confirm.html',
                   {'message': msg, 'description': description,
                    'section': "emploi/base.html"},
                    context_instance=RequestContext(request))

    # 2eme passage: on supprime si c'est confirmé
    else:
        if request.POST['choice']=="1":
            leisure.delete()

            request.user.message_set.create(message=_("Leisure informations successfully deleted."))

        return HttpResponseRedirect('/emploi/%s/cv/edit/' % (request.user.id))

def leisure_add(request, user_id=None):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"},
                                   context_instance=RequestContext(request))

    p = get_object_or_404(Person, user=user_id)

    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        LeisureForm = forms.models.form_for_model(LeisureItem,
            formfield_callback=form_callback)
        f = LeisureForm()
        return render_to_response('emploi/leisure_edit.html',
                                 {'form': f, 'person': p, 'user': request.user,
                                  'action': "create"},
                                  context_instance=RequestContext(request))

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        LeisureForm = forms.models.form_for_model(LeisureItem,
            formfield_callback=form_callback)
        f = LeisureForm(request.POST.copy())
        if f.is_valid():
            f.clean_data['person'] = p
            f.save()

            request.user.message_set.create(message=_("Leisure informations successfully added."))

        return HttpResponseRedirect('/emploi/%s/cv/edit/' % (request.user.id))

def publication_edit(request, user_id=None, publication_id=None):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': 'emploi/base.html'},
                                   context_instance=RequestContext(request))

    p = get_object_or_404(Person, user=user_id)
    publication = get_object_or_404(PublicationItem, pk=publication_id)

    # 1er passage : on propose un formulaire avec les données actuelles
    if request.method == 'GET':
        PubForm = forms.models.form_for_instance(publication,
            formfield_callback=form_callback)
        f = PubForm()
        return render_to_response('emploi/publication_edit.html',
                                 {'form': f, 'user': request.user,
                                  'action': 'edit'},
                                  context_instance=RequestContext(request))

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        PubForm = forms.models.form_for_instance(publication,
            formfield_callback=form_callback)
        f = PubForm(request.POST.copy())
        if f.is_valid():
            f.clean_data['person'] = p
            f.save()

            request.user.message_set.create(message=_("Publication informations updated successfully."))

        return HttpResponseRedirect('/emploi/%s/cv/edit/' % (request.user.id))

def publication_delete(request, user_id=None, publication_id=None):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': 'emploi/base.html'})

    p = get_object_or_404(Person, user=user_id)
    publication = get_object_or_404(PublicationItem, pk=publication_id)

    # 1er passage: on demande confirmation
    if request.method != 'POST':
        msg = _('Do you really want to delete this publication item?')
        description = ''
        return render_to_response('pages/confirm.html',
                                 {'message': msg, 'description': description,
                                  'section': 'emploi/base.html'},
                                  context_instance=RequestContext(request))

    # 2eme passage: on supprime si c'est confirmé
    else:
        if request.POST['choice']=="1":
            publication.delete()
            request.user.message_set.create(message=_("Publication informations deleted successfully."))

        return HttpResponseRedirect('/emploi/%s/cv/edit/' % (request.user.id))

def publication_add(request, user_id=None):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': 'emploi/base.html'},
                                   context_instance=RequestContext(request))

    p = get_object_or_404(Person, user=user_id)

    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        PubForm = forms.models.form_for_model(PublicationItem,
            formfield_callback=form_callback)
        f = PubForm()
        return render_to_response('emploi/education_edit.html',
                                 {'form': f, 'person': p, 'user': request.user,
                                  'action': 'create'},
                                  context_instance=RequestContext(request))

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        PubForm = forms.models.form_for_model(PublicationItem,
            formfield_callback=form_callback)
        f = PubForm(request.POST.copy())
        if f.is_valid():
            f.clean_data['person'] = p
            f.save()

            request.user.message_set.create(message=_("Publication informations successfully added."))

        return HttpResponseRedirect('/emploi/%s/cv/edit/' % (request.user.id))


def office_create(request, user_id=None):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"},
                                   context_instance=RequestContext(request))

    p = get_object_or_404(Person, user=user_id)

    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        OfficeForm = forms.models.form_for_model(Office)
        f = OfficeForm()
        return render_to_response('emploi/office_create.html',
                                 {'form': f, 'person': p, 
                                  'user': request.user, 'object': "office"},
                                  context_instance=RequestContext(request))

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        OfficeForm = forms.models.form_for_model(Office)
        f = OfficeForm(request.POST.copy())
        if f.is_valid():
            f.save()
        return render_to_response('emploi/cv_edit.html',
                                 {'person': p, 'user': request.user},
                                 context_instance=RequestContext(request))

def company_create(request, user_id=None):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"},
                                   context_instance=RequestContext(request))

    p = get_object_or_404(Person, user=user_id)

    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        CompanyForm = forms.models.form_for_model(Company)
        CompanyForm.base_fields['size'].widget =\
            forms.Select(choices=Company.COMPANY_SIZE)
        f = CompanyForm()
        return render_to_response('emploi/office_create.html',
                                 {'form': f, 'person': p, 'user': request.user,
                                  'object': "company"},
                                  context_instance=RequestContext(request))

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        CompanyForm = forms.models.form_for_model(Company)
        f = CompanyForm(request.POST.copy())
        if f.is_valid():
            f.save()
        return render_to_response('emploi/cv_edit.html',
                                 {'person': p, 'user': request.user},
                                  context_instance=RequestContext(request))

def job_details(request,emploi_id):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"},
                                   context_instance=RequestContext(request))

    j = get_object_or_404(JobOffer, pk=emploi_id)

    j.nb_views = j.nb_views + 1
    j.save()

    return render_to_response('emploi/job_details.html',
                             {'job': j, 'user': request.user}, 
                             context_instance=RequestContext(request))

def job_edit(request, emploi_id):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"},
                                  context_instance=RequestContext(request))

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

    return render_to_response('emploi/job_edit.html',
                             {'form': f, 'user': request.user}, 
                              context_instance=RequestContext(request))

def job_register(request):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"},
                                   context_instance=RequestContext(request))

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
    return render_to_response('emploi/job_register.html',
                             {'form': f, 'user': request.user}, 
                             context_instance=RequestContext(request))

def job_search(request):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"},
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        form = SearchJobForm(request.POST)
        if form.is_valid():
                    list_jobs = JobOffer.objects.filter(title__icontains=form.clean_data['title'])
                    return render_to_response('emploi/job_search.html', 
                                             {'form': form, 
                                              'list_jobs': list_jobs, 
                                              'request': request, 
                                              'user': request.user},
                                              context_instance=RequestContext(request))

    else:
        f = SearchJobForm()
        return render_to_response('emploi/job_search.html', 
                                 {'form': f , 'user': request.user}, 
                                 context_instance=RequestContext(request))

def company_details(request, company_id):

    if not request.user.is_authenticated():
        return render_to_response('pages/authentification_needed.html',
                                  {'user': request.user,
                                   'section': "emploi/base.html"},
                                   context_instance=RequestContext(request))

    company = get_object_or_404(Company, pk=company_id)
    offices = Office.objects.filter(company=company)

    return render_to_response('emploi/company_details.html',
                              {'company': company, 'user': request.user,
                               'offices': offices},
                              context_instance=RequestContext(request))

