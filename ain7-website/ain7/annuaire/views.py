# -*- coding: utf-8
#
# annuaire/views.py
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
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django import newforms as forms

from ain7.annuaire.models import Person, AIn7Member
from ain7.annuaire.models import Track
from ain7.annuaire.models import Promo

class SearchPersonForm(forms.Form):
    last_name = forms.CharField(label=_('Last name'), max_length=50, required=False)
    first_name = forms.CharField(label=_('First name'), max_length=50, required=False)
    promo = forms.IntegerField(label=_('Promo'), required=False)
    track = forms.IntegerField(label=_('Track'), required=False)

@login_required
def detail(request, person_id):
    p = get_object_or_404(Person, pk=person_id)
    ain7member = get_object_or_404(AIn7Member, person=p)
    return render_to_response('annuaire/details.html', 
                             {'person': p, 'user': request.user,
                              'ain7member': ain7member}, 
                              context_instance=RequestContext(request))

@login_required
def search(request):
    maxTrackId=Track.objects.order_by('-id')[0].id+1
    trackList=[(maxTrackId,'Toutes')]
    for track in Track.objects.all():
        trackList.append((track.id,track.name))
    SearchPersonForm.base_fields['track'].widget=\
        forms.Select(choices=trackList)

    if request.method == 'POST':
        form = SearchPersonForm(request.POST)
        if form.is_valid():

            # criteres sur le nom et prenom
            criteria={'person__last_name__contains':form.clean_data['last_name'],\
                      'person__first_name__contains':form.clean_data['first_name']}
            # ici on commence par rechercher toutes les promos
            # qui concordent avec l'annee de promotion et la filiere
            # saisis par l'utilisateur.
            promoCriteria={}
            if form.clean_data['promo']!=None:
                promoCriteria['year']=form.clean_data['promo']
            if form.clean_data['track']!=maxTrackId:
                promoCriteria['track']=\
                    Track.objects.get(id=form.clean_data['track'])
                
            # on ajoute ces promos aux critères de recherche
            # si elle ne sont pas vides
            if len(promoCriteria)!=0:
                criteria['promos__in']=Promo.objects.filter(**promoCriteria)
                
            ain7members = AIn7Member.objects.filter(**criteria)

            return render_to_response('annuaire/index.html', 
                                     {'ain7members': ain7members,
                                      'user': request.user},
                                      context_instance=RequestContext(request))

    else:
        f = SearchPersonForm()
        return render_to_response('annuaire/search.html', 
                                 {'form': f , 'user': request.user},
                                 context_instance=RequestContext(request))

@login_required
def edit(request, person_id=None):

    p = get_object_or_404(Person, pk=person_id)
    ain7member = get_object_or_404(AIn7Member, person=p)
    return render_to_response('annuaire/edit.html',
                              {'person': p, 'user': request.user,
                               'ain7member': ain7member},
                              context_instance=RequestContext(request))
#     if person_id is None:
#         PersonForm = forms.models.form_for_model(Person,
#             formfield_callback=form_callback)
#         form = PersonForm()

#     else:
#         person = Person.objects.get(pk=person_id)
#         PersonForm = forms.models.form_for_instance(person,
#             formfield_callback=form_callback)
#         PersonForm.base_fields['sex'].widget=\
#             forms.Select(choices=Person.SEX)
#         form = PersonForm(auto_id=False)

#         if request.method == 'POST':
#              form = PersonForm(request.POST)
#              if form.is_valid():
#                  form.clean_data['user'] = person.user
#                  form.save()
#                  request.user.message_set.create(message=_("Modifications have been successfully saved."))
#                  return HttpResponseRedirect('/annuaire/%s/' % (person.user.id))

#     return render_to_response('annuaire/edit.html', 
#                              {'form': form, 'user': request.user},
#                              context_instance=RequestContext(request))


# une petite fonction pour exclure les champs
# person user ain7member
# des formulaires créés avec form_for_model et form_for_instance
def form_callback(f, **args):
  if f.name == "person" or f.name == "user" or f.name == "ain7member":
    return None
  return f.formfield(**args)
