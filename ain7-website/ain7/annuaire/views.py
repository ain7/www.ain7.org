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

from ain7.annuaire.models import Person

class SearchPersonForm(forms.Form):
    last_name = forms.CharField(label=_('last name').capitalize(), max_length=50, required=False)
    first_name = forms.CharField(label=_('first name').capitalize(), max_length=50, required=False)
    promo = forms.IntegerField(label=_('promo').capitalize(), required=False)
    filiere = forms.IntegerField(label=_('track').capitalize(), required=False)

def detail(request, person_id):

    if not request.user.is_authenticated():
         return render_to_response('annuaire/authentification_needed.html', {'user': request.user})

    p = get_object_or_404(Person, pk=person_id)
    return render_to_response('annuaire/details.html', {'person': p, 'user': request.user})

def search(request):

    if not request.user.is_authenticated():
         return render_to_response('annuaire/authentification_needed.html', {'user': request.user})


    JokerFilieres=(0,'Toutes')
    ListeFilieres=[JokerFilieres]#+list(Track.all)
    SearchPersonForm.base_fields['filiere'].widget=\
        forms.Select(choices=ListeFilieres)
    
    JokerPromos=(0,'Toutes')
    ListePromos=[JokerPromos]#+list(Promo.all)
    SearchPersonForm.base_fields['promo'].widget=\
        forms.Select(choices=tuple(ListePromos))

    if request.method == 'POST':
        form = SearchPersonForm(request.POST)
        if form.is_valid():
            criteres={'last_name__contains':form.clean_data['last_name'],\
                      'first_name__contains':form.clean_data['first_name']}
            if form.clean_data['promo']!=0:
                criteres['promo']=form.clean_data['promo']
            if form.clean_data['filiere']!=0:               
                criteres['filiere']=form.clean_data['filiere']
            persons = Person.objects.filter(**criteres)
            return render_to_response('annuaire/index.html', {'persons': persons, 'user': request.user})

    else:
        f = SearchPersonForm()
        return render_to_response('annuaire/search.html', {'form': f , 'user': request.user})

def edit(request, person_id=None):

    if not request.user.is_authenticated():
         return render_to_response('annuaire/authentification_needed.html', {'user': request.user})

    if person_id is None:
        PersonForm = forms.models.form_for_model(Person)
        form = PersonForm()

    else:
        person = Person.objects.get(pk=person_id)
        PersonForm = forms.models.form_for_instance(person)
        PersonForm.base_fields['sex'].widget=\
            forms.Select(choices=Person.SEX)
        PersonForm.base_fields['avatar'].widget=\
            forms.FileInput()
        avatarFile = person.get_avatar_url()
        form = PersonForm(auto_id=False)

        if request.method == 'POST':
             form = PersonForm(request.POST)
             if form.is_valid():
                 if form.clean_data['avatar']=='':
                     form.clean_data['avatar']=avatarFile
                 form.save()

    return render_to_response('annuaire/edit.html', {'form': form, 'user': request.user,  })

