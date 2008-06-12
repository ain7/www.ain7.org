# -*- coding: utf-8
#
# pages/views.py
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

import datetime

from django.template import RequestContext
from django.utils.translation import ugettext as _

from ain7.news.models import NewsItem
from ain7.sondages.models import Survey
from ain7.utils import ain7_render_to_response
from ain7.annuaire.models import AIn7Member

def homepage(request):
    news = NewsItem.objects.all().order_by('-creation_date')[:2]
    surveys = Survey.objects.filter(start_date__lte=datetime.datetime.now(), end_date__gte=datetime.datetime.now())[:2]
    return ain7_render_to_response(request, 'pages/homepage.html', 
                            {'news': news , 'surveys': surveys})

def apropos(request):
    return ain7_render_to_response(request, 'pages/apropos.html', {})

def association(request):
    # calcul du nombre d'AIn7Member ayant un diplome (au sens large)
    nbDiplomes = 0
    for member in AIn7Member.objects.all():
        if member.diplomas.count() != 0:
            nbDiplomes = nbDiplomes + 1
    # calcul du nombre d'AIn7Member
    nbAdherents = AIn7Member.objects.all().count()
    return ain7_render_to_response(request, 'pages/association.html', {'nbDiplomes': nbDiplomes, 'nbAdherents': nbAdherents})

def status(request):
    return ain7_render_to_response(request, 'pages/status.html', {})

def board(request):
    return ain7_render_to_response(request, 'pages/board.html', {})

def council(request):
    return ain7_render_to_response(request, 'pages/council.html', {})

def canal_n7(request):
    return ain7_render_to_response(request, 'pages/canal_n7.html', {})

def contact(request):
    return ain7_render_to_response(request, 'pages/contact.html', {})

def international(request):
    return ain7_render_to_response(request, 'pages/international.html', {})

def mentions_legales(request):
    return ain7_render_to_response(request, 'pages/mentions_legales.html', {})

def publications(request):
    return ain7_render_to_response(request, 'pages/publications.html', {})

def rss(request):
    return ain7_render_to_response(request, 'pages/rss.html', {})

