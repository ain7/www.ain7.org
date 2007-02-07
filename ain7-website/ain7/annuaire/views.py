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

from django.shortcuts import get_object_or_404, render_to_response
from ain7.annuaire.models import Personne

def index(request):
    liste_personnes = Personne.objects.all().order_by('nom')[:5]
    return render_to_response('annuaire/index.html', {'liste_personnes': liste_personnes})

def detail(request, personne_id):
    p = get_object_or_404(Personne, pk=personne_id)
    return render_to_response('annuaire/detail.html', {'personne': p})

