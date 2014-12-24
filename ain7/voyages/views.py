# -*- coding: utf-8
"""
 ain7/voyages/views.py
"""
#
#   Copyright © 2007-2015 AIn7
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

from datetime import datetime

from django.contrib import messages
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person
from ain7.decorators import access_required, confirmation_required
from ain7.pages.models import Text
from ain7.utils import ain7_generic_delete
from ain7.voyages.models import Travel, Subscription, TravelResponsible
from ain7.voyages.forms import SearchTravelForm


def index(request):
    """index"""
    next_travels = Travel.objects.filter(
        start_date__gte=datetime.now()).order_by('-start_date')
    prev_travels = Travel.objects.filter(
        start_date__lt=datetime.now()).order_by('-start_date')[:5]
    text = Text.objects.get(textblock__shortname='voyages')
    return render(request, 'voyages/index.html',
        {'next_travels': next_travels, 'previous_travels': prev_travels,
         'text': text})

@confirmation_required(
    lambda user_id = None,
    travel_id = None: str(get_object_or_404(Travel, pk=travel_id)),
    'voyages/base.html',
    _('Do you REALLY want to delete this travel'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def delete(request, travel_id):
    """delete travel"""

    return ain7_generic_delete(request,
        get_object_or_404(Travel, pk=travel_id),
        '/voyages/', _('Travel successfully deleted.'))

def details(request, travel_id):
    """travel details"""
    travel = get_object_or_404(Travel, pk=travel_id)
    return render(request, 'voyages/details.html',
        {'travel': travel})

def list(request):
    """upcoming travels list"""
    return render(request, 'voyages/list.html',
        {'travels': Travel.objects.exclude(end_date__lte=datetime.now())})

def search(request):
    """search travels form"""

    form = SearchTravelForm()
    nb_results_by_page = 25
    travels = False
    paginator = Paginator(Travel.objects.none(), nb_results_by_page)
    page = 1

    if request.method == 'POST':
        form = SearchTravelForm(request.POST)
        if form.is_valid():
            travels = form.search()
            paginator = Paginator(travels, nb_results_by_page)
            try:
                page =  int(request.GET.get('page', '1'))
                travels = paginator.page(page).object_list
            except InvalidPage:
                raise Http404
    return render(request, 'voyages/search.html',
        {
            'travels': travels, 'form': form, 'request': request,
            'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
            'has_next': paginator.page(page).has_next(),
            'has_previous': paginator.page(page).has_previous(),
            'current_page': page,
            'next_page': page + 1, 'previous_page': page - 1,
            'pages': paginator.num_pages,
            'first_result': (page - 1) * nb_results_by_page +1,
            'last_result': min((page) * nb_results_by_page, paginator.count),
            'hits' : paginator.count,
        }
    )

@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def edit(request, travel_id=None):
    """edit travel"""

    travel = None
    if travel_id:
        travel = Travel.objects.get(pk=travel_id)

    TravelForm = modelform_factory(Travel, exclude=())
    form = TravelForm(request.POST or None, request.FILES or None, instance=travel)

    if request.method == 'POST' and form.is_valid():
        trav = form.save()
        messages.success(request, _('Modifications have been successfully saved.'))

        redirect('travel-details', trav.id)

    return render(request, 'voyages/edit.html',
        {
            'form': form,
            'action_title': _("Modification of personal data for"),
            'back': request.META.get('HTTP_REFERER', '/'),
        }
    )

