# -*- coding: utf-8
#
# ajax/views.py
#
#   Copyright (C) 2007-2008 AIn7
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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission
from django.db.models import Q

from ain7.annuaire.models import Person, Country, Track, PromoYear
from ain7.emploi.models import ActivityField, Organization, Office
from ain7.utils import ain7_render_to_response

def ajaxed_fields():
    """Links fields for which an autocompletion using Ajax exists,
    and the names of these autocompletion methods."""
    return {Person: 'person',
            Country: 'nationality',
            PromoYear: 'promoyear',
            Track: 'track',
            Organization: 'organization',
            ActivityField: 'activity_field',
            Permission: 'permission',
            Office: 'office'}

def completion_list(objects):
    """Builds and returns the completion list, from the query."""
    elements = []
    for o in objects:
        elements.append({'id': o.pk,
            'displayValue': o.autocomplete_str(),
            'value': o.autocomplete_str()})
    return elements

@login_required
def person(request):
    elements = []

    if request.method == 'POST':
        input = request.POST['text']
        elements = completion_list(
            Person.objects.filter(complete_name__icontains=input))

    return ain7_render_to_response(request, 'ajax/complete.html', {'elements': elements})

@login_required
def nationality(request):
    elements = []

    if request.method == 'POST':
        input = request.POST['text']
        elements = completion_list(
            Country.objects.filter(nationality__icontains=input))

    return ain7_render_to_response(request, 'ajax/complete.html', {'elements': elements})

@login_required
def promoyear(request):
    elements = []

    if request.method == 'POST':
        input = request.POST['text']
        elements = completion_list(
            PromoYear.objects.filter(year__icontains=input))

    return ain7_render_to_response(request, 'ajax/complete.html', {'elements': elements})

@login_required
def track(request):
    elements = []

    if request.method == 'POST':
        input = request.POST['text']
        elements = completion_list(
            Track.objects.filter(name__icontains=input).order_by('name'))

    return ain7_render_to_response(request, 'ajax/complete.html', {'elements': elements})

@login_required
def organization(request):
    elements = []

    if request.method == 'POST':
        input = request.POST['text']
        elements = completion_list(Organization.objects.\
            filter(name__icontains=input).\
            filter(is_a_proposal=False).\
            order_by('name'))

    return ain7_render_to_response(request, 'ajax/complete.html', {'elements': elements})

@login_required
def activity_field(request):
    elements = []

    if request.method == 'POST':
        input = request.POST['text']
        elements = completion_list(
            ActivityField.objects.filter(label__icontains=input))

    return ain7_render_to_response(request, 'ajax/complete.html', {'elements': elements})

@login_required
def activitycode(request):
    elements = []

    if request.method == 'POST':
        input = request.POST['text']
        activitycode = ActivityField.objects.filter(code__icontains=input)
        for cf in activitycode:
            elements.append({'id': cf.id, 'displayValue': cf.code , 'value': cf.code })

    return ain7_render_to_response(request, 'ajax/complete.html', {'elements': elements})

@login_required
def permission(request):
    elements = []

    if request.method == 'POST':
        input = request.POST['text']
        perms = Permission.objects.filter(name__icontains=input)

        for perm in perms:
            elements.append({'id': perm.id, 'displayValue': perm.name, 'value': perm.name})

    return ain7_render_to_response(request, 'ajax/complete.html', {'elements': elements})

@login_required
def office(request):
    elements = []

    if request.method == 'POST':
        input = request.POST['text']
        elements = completion_list(
            Office.objects.filter(Q(name__icontains=input) | Q(organization__name__icontains=input)).order_by('organization__name','name'))

    return ain7_render_to_response(request, 'ajax/complete.html', {'elements': elements})

