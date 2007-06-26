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
from datetime import datetime
from django.contrib.auth.decorators import login_required

from ain7.voyages.models import Travel, Subscription

def index(request):
    next_travels = Travel.objects.filter(start_date__gte=datetime.now())
    prev_travels = Travel.objects.filter(start_date__lt=datetime.now())
    return _render_response(request, 'voyages/index.html',
                            {'next_travels': next_travels,
                             'previous_travels': prev_travels})

def detail(request,travel_id):
    t = get_object_or_404(Travel, pk=travel_id)
    past = t in Travel.objects.filter(start_date__lt=datetime.now())
    return _render_response(request, 'voyages/details.html',
                            {'travel': t, 'past': past})

@login_required
def edit(request, travel_id=None):
    if travel_id is None:
        TravelForm = forms.models.form_for_model(Travel)
        TravelForm.base_fields['description'].widget = \
            forms.widgets.Textarea(attrs={'rows':10, 'cols':90})
        TravelForm.base_fields['report'].widget = \
            forms.widgets.Textarea(attrs={'rows':15, 'cols':90})
        form = TravelForm()
    else:
        travel = Travel.objects.get(pk=travel_id)
        TravelForm = forms.models.form_for_instance(travel)
        TravelForm.base_fields['description'].widget = \
            forms.widgets.Textarea(attrs={'rows':15, 'cols':90})
        TravelForm.base_fields['report'].widget = \
            forms.widgets.Textarea(attrs={'rows':15, 'cols':90})
        form = TravelForm()
        if request.method == 'POST':
             form = TravelForm(request.POST)
             if form.is_valid():
                 form.save()
                 request.user.message_set.create(
                     message=_("Modifications have been successfully saved."))
                 return HttpResponseRedirect('/voyages/%s/' % (travel.id))
    return _render_response(request, 'voyages/edit.html', {'form': form})

@login_required
def join(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)

    if request.method == 'GET':
        JoinTravelForm = forms.models.form_for_model(Subscription,
            formfield_callback=_form_callback)
        f = JoinTravelForm()
        return _render_response(request, "voyages/join.html",
                                {'form': f, 'travel': travel})
    
    if request.method == 'POST':
        JoinTravelForm = forms.models.form_for_model(Subscription,
            formfield_callback=_form_callback)
        f = JoinTravelForm(request.POST.copy())
        if f.is_valid():
            f.clean_data['subscriber'] = request.user.person
            f.clean_data['travel'] = travel
            f.save()
            request.user.message_set.create(message=_('You have been successfully subscribed to this travel.'))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
        return HttpResponseRedirect('/voyages/%s/' % (travel.id))


@login_required
def subscribe(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)
    # TODO
    return HttpResponseRedirect('/voyages/%s/' % (travel.id))

@login_required
def participants(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)
    # TODO
    return HttpResponseRedirect('/voyages/%s/' % (travel.id))

# pour alléger les appels à render_to_response
# http://www.djangosnippets.org/snippets/3/
def _render_response(req, *args, **kwargs):
    kwargs['context_instance'] = RequestContext(req)
    return render_to_response(*args, **kwargs)

# une petite fonction pour exclure les champs
# subscriber travel
# des formulaires créés avec form_for_model et form_for_instance
def _form_callback(f, **args):
    exclude_fields = ('subscriber', 'travel')
    if f.name in exclude_fields:
        return None
    return f.formfield(**args)

