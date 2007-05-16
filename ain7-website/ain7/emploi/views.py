# -*- coding: utf-8
#
# emploi/views.py
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
from django.newforms import widgets

from ain7.annuaire.models import Person

def index(request):
    if not request.user.is_authenticated():
        return render_to_response('annuaire/authentification_needed.html',
                                  {'user': request.user})
    # TODO : renseigner liste_emploiss avec la liste des emplois
    # correspondant aux filières qui intéressent la personne
    return render_to_response('emploi/index.html', {'user': request.user})


def cv_detail(request, user_id):

    if not request.user.is_authenticated():
        return render_to_response('annuaire/authentification_needed.html',
                                  {'user': request.user})
    
    p = get_object_or_404(Person, user=user_id)
    return render_to_response('emploi/cv_detail.html',
                              {'person': p, 'user': request.user})


def cv_edit(request, user_id=None):

    if not request.user.is_authenticated():
        return render_to_response('annuaire/authentification_needed.html',
                                  {'user': request.user})
    # TODO : un joli formulaire...
    # return render_to_response('emploi/cv_edit.html',
    #                           {'form': form, 'user': request.user,  })
    return render_to_response('emploi/cv_edit.html', {'user': request.user,  })

