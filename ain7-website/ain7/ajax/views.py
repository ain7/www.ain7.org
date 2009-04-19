# -*- coding: utf-8
#
# ajax/views.py
#
#   Copyright © 2007-2009 AIn7 Devel Team
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
from django.http import Http404


from ain7.annuaire.models import Person, Country, Track, PromoYear
from ain7.emploi.models import ActivityField, Organization, Office, EducationItem, DiplomaItem
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

def ajaxed_strings():
    """Links strings for which an autocompletion using Ajax exists,
    and the names of these autocompletion methods."""
    return [ 'diploma' ]

def completion_list(objects):
    """Builds and returns the completion list, from the query."""
    elements = []
    for o in objects:
        elements.append({'id': o.pk,
            'displayValue': o.autocomplete_str(),
            'value': o.autocomplete_str()})
    return elements

def ajax_search_method(name):
    method = globals().get(name)
    return method

@login_required
def ajax_request(request, completed_name, field_name):
    # get the method for auto-completion of "name"
    method = ajax_search_method(completed_name)
    if method == None:
        # ups... can't complet this... raise 404
        raise Http404
    elements = []
    if request.method == 'POST':
        input = request.POST[field_name + '_text']
        elements = method(input)

    return ain7_render_to_response(request, 'ajax/complete.html', {'elements': elements})


def person(input):
    elements = completion_list(
        Person.objects.filter(complete_name__icontains=input).order_by('last_name','first_name'))

    return elements

def nationality(input):
    elements = completion_list(
        Country.objects.filter(nationality__icontains=input).order_by('nationality'))

    return elements

def promoyear(input):
    elements = completion_list(
        PromoYear.objects.filter(year__icontains=input).order_by('year'))

    return elements

def track(input):
    elements = completion_list(
        Track.objects.filter(name__icontains=input).order_by('name').order_by('name'))

    return elements

def organization(input):
    elements = completion_list(Organization.objects.\
        filter(name__icontains=input).\
        order_by('name'))

    return elements

def activity_field(input):
    elements = completion_list(
        ActivityField.objects.filter(label__icontains=input).order_by('label'))

    return elements

def activitycode(input):
    elements = []

    activitycode = ActivityField.objects.filter(code__icontains=input).order_by('code')
    for cf in activitycode:
        elements.append({'id': cf.id, 'displayValue': cf.code , 'value': cf.code })

    return elements

def office(input):
    elements = completion_list(
        Office.objects.filter(Q(name__icontains=input) | Q(organization__name__icontains=input)).order_by('organization__name','name'))

    return elements

def diploma(input):
    elements = []

    diplomas = []
    for e in EducationItem.objects.filter(diploma__icontains=input):
        diplomas.append(e.diploma)
    for e in DiplomaItem.objects.filter(diploma__icontains=input):
        diplomas.append(e.diploma)
    diplomas = list(set(diplomas))
    diplomas.sort()
    for d in diplomas:
        elements.append( {'id': d, 'displayValue': d, 'value': d} )

    return elements
