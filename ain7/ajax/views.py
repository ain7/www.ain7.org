# -*- coding: utf-8
#
# ajax/views.py
#
#   Copyright © 2007-2010 AIn7 Devel Team
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

def ajax_resolve():
    """Maps Ajax URLs to model fields.
    These mappings are groupped by models.
    For each model, the first element of its list is
    the default one for completion."""
    return {Person:  [ ('complete_name', 'person') ],
            Country: [ ('name','country'), ('nationality', 'nationality') ],
            PromoYear:     [ ('year','promoyear') ],
            Track:         [ ('name','track') ],
            Organization:  [ ('name','organization') ],
            Office:        [ ('name','office') ],
            ActivityField: [ ('label','activity_field'), ('code','activitycode') ],
            }

def ajaxed_strings():
    """Lists strings for which an autocompletion using Ajax exists,
    and the names of these autocompletion methods."""
    return [ 'diploma' ]

def ajax_get_model_field(completed_name):
    """Given an Ajax URL, returns the corresponding model and field name."""
    model = None
    field_name = None
    for modl, pairs in ajax_resolve().iteritems():
        for fname, cname in pairs:
            if completed_name == cname:
                field_name = fname
                model = modl
    return model, field_name

def ajax_field_value(url, model_pk):
    """Returns the value of an ajaxed field, given the completed name (url)
    and the id."""
    model, field_name = ajax_get_model_field(url)
    model_inst = model.objects.get(pk=model_pk)
    return getattr(model_inst, field_name)

@login_required
def ajax_request(request, completed_name, field_name):
    elements = []
    if request.method == 'POST':
        input = request.POST[field_name + '_text']
        if completed_name in ajaxed_strings():
            method = globals().get(completed_name)
            if method == None:
                raise Http404
            elements = method(input)
        else:
            elements = ajax_get_elements(completed_name, input)

    return ain7_render_to_response(request, 'ajax/complete.html', {'elements': elements})

def ajax_get_elements(completed_name, input):
    """Given a completed_name, and some input of the user, returns
    the set of matching objects."""
    elements = []
    model, field_name = ajax_get_model_field(completed_name)
    criteria = Q(**{field_name+'__icontains': input})
    # for offices, we also look into the name of the organization
    if completed_name=='office':
        criteria |= Q(**{'organization__name__icontains': input})
    selected = model.objects.filter(criteria).order_by(field_name)
    for selection in selected:
        display = getattr(selection, field_name)
        if completed_name == 'office':
             display += '<i>'
             for field in ['city', 'zip_code', 'line1', 'line2']:
                 if getattr(selection, field):
                     display += ' - ' + getattr(selection,field)
             display += '</i>'
        elements.append({
            'id': selection.id,
            'displayValue': display,
            'value': display })
    return elements[:50]

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

