# -*- coding: utf-8
#
# pages/views.py
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
from ain7.news.models import NewsItem
from ain7.sondages.models import Survey

def homepage(request):
    news = NewsItem.objects.all().order_by('title')[:5]
    liste_sondages = Survey.objects.all()[:2]
    user = request.user
    return render_to_response('pages/homepage.html', {'news': news , 'liste_sondages': liste_sondages, 'user': user })

def apropos(request):
    user = request.user
    return render_to_response('pages/apropos.html', {'user': user })

def association(request):
    user = request.user
    return render_to_response('pages/association.html', {'user': user })

def canal_n7(request):
    user = request.user
    return render_to_response('pages/canal_n7.html', {'user': user })

def contact(request):
    user = request.user
    return render_to_response('pages/contact.html', {'user': user })

def international(request):
    user = request.user
    return render_to_response('pages/international.html', {'user': user })

def mentions_legales(request):
    user = request.user
    return render_to_response('pages/mentions_legales.html', {'user': user })

def publications(request):
    user = request.user
    return render_to_response('pages/publications.html', {'user': user })

def sitemap(request):
    user = request.user
    return render_to_response('pages/sitemap.html', {'user': user })

