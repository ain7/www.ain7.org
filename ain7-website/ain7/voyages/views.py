# -*- coding: utf-8
#
# voyages/views.py
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
from django.template import RequestContext
from django.newforms import widgets
from django.http import HttpResponseRedirect
from datetime import date, datetime, timedelta

from ain7.voyages.models import Travel

def index(request):
    # TODO (marche pas pour l'instant)
    next_travels = Travel.objects.all()[:5]
    # next_travels = Travel.objects.filter(start_date__gte=datetime.now)
    return _render_response(request, 'voyages/index.html',
                            {'next_travels': next_travels})

def detail(request,travel_id):
    t = get_object_or_404(Travel, pk=travel_id)
    return _render_response(request, 'voyages/details.html', {'travel': t})

def edit(request, travel_id=None):
    if travel_id is None:
        TravelForm = forms.models.form_for_model(Travel)
        TravelForm.base_fields['description'].widget = forms.widgets.Textarea(attrs={'rows':10, 'cols':90})
        TravelForm.base_fields['report'].widget = forms.widgets.Textarea(attrs={'rows':15, 'cols':90})
        form = TravelForm()
    else:
        travel = Travel.objects.get(pk=travel_id)
        TravelForm = forms.models.form_for_instance(travel)
        TravelForm.base_fields['description'].widget = forms.widgets.Textarea(attrs={'rows':15, 'cols':90})
        TravelForm.base_fields['report'].widget = forms.widgets.Textarea(attrs={'rows':15, 'cols':90})
        form = TravelForm()
        if request.method == 'POST':
             form = TravelForm(request.POST)
             if form.is_valid():
                 form.save()
                 request.user.message_set.create(message=_("Modifications have been successfully saved."))
                 return HttpResponseRedirect('/voyages/%s/' % (travel.id))
    return _render_response(request, 'voyages/edit.html', {'form': form})

# pour alléger les appels à render_to_response
# http://www.djangosnippets.org/snippets/3/
def _render_response(req, *args, **kwargs):
    kwargs['context_instance'] = RequestContext(req)
    return render_to_response(*args, **kwargs)

