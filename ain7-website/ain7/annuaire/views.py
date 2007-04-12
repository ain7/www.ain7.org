# -*- coding: utf-8
#
# views.py
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
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django import newforms as forms
from django.db import models

from ain7.annuaire.models import Personne

class SearchPersonForm(forms.Form):
    nom = forms.CharField(max_length=50, required=False)
    prenom = forms.CharField(max_length=50, required=False)
    promo = forms.IntegerField(required=False)
    filiere = forms.IntegerField(required=False)

def detail(request, personne_id):

    if not request.user.is_authenticated():
         return render_to_response('annuaire/authentification_needed.html', {'user': request.user})

    p = get_object_or_404(Personne, pk=personne_id)
    return render_to_response('annuaire/details.html', {'personne': p, 'user': request.user})

def search(request):

    if not request.user.is_authenticated():
         return render_to_response('annuaire/authentification_needed.html', {'user': request.user})

    SearchPersonForm.base_fields['prenom'].label=u'Prénom'
    SearchPersonForm.base_fields['filiere'].label=u'Filière'
    SearchPersonForm.base_fields['filiere'].widget=\
        forms.Select(choices=Personne.FILIERES)
    SearchPersonForm.base_fields['promo'].label=u'Promotion'
    SearchPersonForm.base_fields['promo'].widget=\
        forms.Select(choices=Personne.CHOIX_PROMO)
    if request.method == 'POST':
        form = SearchPersonForm(request.POST)
        if form.is_valid():
		    liste_personnes = Personne.objects.filter(nom__startswith=form.clean_data['nom'])
		    return render_to_response('annuaire/index.html', {'liste_personnes': liste_personnes, 'user': request.user})

    else:
        f = SearchPersonForm()
        return render_to_response('annuaire/search.html', {'form': f , 'user': request.user})

def edit(request, personne_id=None):

    if not request.user.is_authenticated():
         return render_to_response('annuaire/authentification_needed.html', {'user': request.user})

    if personne_id is None:
	PersonneForm = forms.models.form_for_model(Personne)
        form = PersonneForm()

    else:
        personne = Personne.objects.get(pk=personne_id)
        PersonneForm = forms.models.form_for_instance(personne)
        PersonneForm.base_fields['user'].label=u'Utilisateur'
        PersonneForm.base_fields['prenom'].label=u'Prénom'
        PersonneForm.base_fields['nom_jeune_fille'].label=u'Nom de jeune fille'
        PersonneForm.base_fields['filiere'].label=u'Filière'
        PersonneForm.base_fields['filiere'].widget=\
            forms.Select(choices=Personne.FILIERES)
        PersonneForm.base_fields['promo'].label=u'Promotion'
        PersonneForm.base_fields['promo'].widget=\
            forms.Select(choices=Personne.CHOIX_PROMO)
        PersonneForm.base_fields['date_naissance'].label=u'Date de naissance'
        PersonneForm.base_fields['date_deces'].label=u'Date de décès'
        PersonneForm.base_fields['nationalite'].label=u'Nationalité'
        PersonneForm.base_fields['nationalite'].widget=\
            forms.Select(choices=Personne.CHOIX_NATIONALITES)        
        PersonneForm.base_fields['nombre_enfants'].label=u'Nombre d\'enfants'
        PersonneForm.base_fields['avatar'].widget=\
            forms.FileInput()        
        PersonneForm.base_fields['blog_agrege_sur_le_planet'].label=u'Blog agrégé sur le Planet'
        form = PersonneForm(auto_id=False)

        if request.method == 'POST':
             form = PersonneForm(request.POST)
             if form.is_valid():
                 form.save()

    return render_to_response('annuaire/edit.html', {'form': form, 'user': request.user,  })

