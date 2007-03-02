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

from ain7.annuaire.models import Personne

class SearchPersonForm(forms.Form):
    nom = forms.CharField(max_length=50, required=False)
    prenom = forms.CharField(max_length=50, required=False)
    promo = forms.IntegerField(required=False)
    filiere = forms.IntegerField(required=False)

def index(request):
    liste_personnes = Personne.objects.all().order_by('nom')[:5]
    return render_to_response('annuaire/index.html', {'liste_personnes': liste_personnes, 'user': request.user})

def detail(request, personne_id):
    p = get_object_or_404(Personne, pk=personne_id)
    return render_to_response('annuaire/detail.html', {'personne': p, 'user': request.user})

def search(request):

    if request.method == 'POST':
        form = SearchPersonForm(request.POST)
        if form.is_valid():
		    liste_personnes = Personne.objects.filter(nom__startswith=form.clean_data['nom'])
		    return render_to_response('annuaire/index.html', {'liste_personnes': liste_personnes, 'user': request.user})

    else:
        f = SearchPersonForm()
        return render_to_response('annuaire/search.html', {'form': f , 'user': request.user})

def edit(request, personne_id=None):

    if personne_id is None:
	PersonneForm = forms.models.form_for_model(Personne)
        form = PersonneForm()

    else:
        personne = Personne.objects.get(id=personne_id)
        PersonneForm = forms.models.form_for_instance(personne)
        form = PersonneForm()

        if request.method == 'POST':
             form = PersonneForm(request.POST)
             if form.is_valid():
                 form.save()

    return render_to_response('annuaire/edit.html', {'form': form, 'user': request.user,  })

