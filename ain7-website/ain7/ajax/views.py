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

from ain7.annuaire.models import *
from ain7.emploi.models import ActivityField
from ain7.utils import ain7_render_to_response

def person(request):
    elements = []

    if request.method == 'POST':
        input = request.POST['text']
        persons = Person.objects.filter(complete_name__icontains=input)
        for person in persons:
            value = person.complete_name
            if person.ain7member:
                promo = person.ain7member.promos.all()[person.ain7member.promos.all().count()-1]
                value = '<a href="javascript:showContactDetails(\'/annuaire/'+str(person.user.id)+'/frame/ \', \''+person.complete_name+'\');">'+person.complete_name+'</a>'
                value += ' ('+str(promo)+')'
            elements.append({'id': person.user.id, 'displayValue': person.complete_name, 'value': value})

    return ain7_render_to_response(request, 'pages/complete.html', {'elements': elements})

def nationality(request):
    elements = []

    if request.method == 'POST':
        input = request.POST['text']
        nationalities = Country.objects.filter(nationality__icontains=input)
        for nationality in nationalities:
            elements.append({'id': nationality.id, 'displayValue': nationality.nationality , 'value': nationality.nationality})

    return ain7_render_to_response(request, 'pages/complete.html', {'elements': elements})


def promo(request):
    elements = []

    if request.method == 'POST':
        input = request.POST['text']
        promos = Promo.objects.filter(year__istartswith=input).values('year').distinct()
        for promo in promos:
            elements.append({'id': promo['year'], 'displayValue': promo['year'], 'value': promo['year']})

    return ain7_render_to_response(request, 'pages/complete.html', {'elements': elements})

def track(request):
    elements = []

    if request.method == 'POST':
        input = request.POST['text']
        tracks = Track.objects.filter(name__icontains=input)
        for track in tracks:
            elements.append({'id':track.id, 'displayValue': track.name , 'value': track.name})

    return ain7_render_to_response(request, 'pages/complete.html', {'elements': elements})

def activityfield(request):
    elements = []

    if request.method == 'POST':
        input = request.POST['text']
        activityfields = ActivityField.objects.filter(label__icontains=input)
        for cf in activityfields:
            elements.append({'id': cf.id, 'displayValue': cf.label , 'value': cf.label })

    return ain7_render_to_response(request, 'pages/complete.html', {'elements': elements})

