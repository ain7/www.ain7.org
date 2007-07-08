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

import datetime

from django.template import RequestContext

from ain7.news.models import NewsItem
from ain7.sondages.models import Survey
from ain7.utils import _render_response

def homepage(request):
    news = NewsItem.objects.all().order_by('-creation_date')[:2]
    surveys = Survey.objects.filter(start_date__lte=datetime.datetime.now(), end_date__gte=datetime.datetime.now())[:2]
    return _render_response(request, 'pages/homepage.html', 
                            {'news': news , 'surveys': surveys})

def apropos(request):
    return _render_response(request, 'pages/apropos.html', {})

def association(request):
    return _render_response(request, 'pages/association.html', {})

def canal_n7(request):
    return _render_response(request, 'pages/canal_n7.html', {})

def contact(request):
    return _render_response(request, 'pages/contact.html', {})

def international(request):
    return _render_response(request, 'pages/international.html', {})

def mentions_legales(request):
    return _render_response(request, 'pages/mentions_legales.html', {})

def publications(request):
    return _render_response(request, 'pages/publications.html', {})

def rss(request):
    return _render_response(request, 'pages/rss.html', {})

def sitemap(request):
    return _render_response(request, 'pages/sitemap.html', {})

