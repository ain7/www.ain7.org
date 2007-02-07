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

from django.shortcuts import render_to_response
from ain7.news.models import Actualite
from ain7.sondages.models import Sondage

def homepage(request):
    liste_actualites = Actualite.objects.all().order_by('titre')[:5]
    liste_sondages = Sondage.objects.all()[:2]
    return render_to_response('pages/index.html', {'liste_actualites': liste_actualites , 'liste_sondages': liste_sondages })

def apropos(request):
    return render_to_response('pages/apropos.html')

def contact(request):
    return render_to_response('pages/contact.html')

