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

from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import get_object_or_404, render_to_response
from django import newforms as forms
from django.newforms import widgets

from ain7.groupes.models import Groupe

def index(request):
    liste_groupes = Groupe.objects.all().order_by('nom')[:5]
    return render_to_response('groupes/index.html', {'liste_groupes': liste_groupes})

def detail(request, groupe_id):
    g = get_object_or_404(Groupe, pk=groupe_id)
    return render_to_response('groupes/detail.html', {'groupe': g})

def edit(request, groupe_id=None):
    groupe = Groupe.objects.get(id=groupe_id)
    GroupeForm = forms.models.form_for_instance(groupe)
#    GroupeForm.fields['page_web'].widget = TinyMCE()
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/")
        else:
            form = GroupeForm()

        t = loader.get_template('groupes/edit.html')

        c = Context({
              'form': form,
          })
        return HttpResponse(t.render(c))

