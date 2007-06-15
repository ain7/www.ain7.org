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

from django.shortcuts import render_to_response
from django.template import RequestContext

from ain7.news.models import NewsItem
from ain7.sondages.models import Survey

def homepage(request):
    news = NewsItem.objects.all().order_by('title')[:5]
    surveys = Survey.objects.filter(start_date__lte=datetime.datetime.now(), end_date__gte=datetime.datetime.now())[:2]
    return render_to_response('pages/homepage.html', 
                             {'news': news , 'surveys': surveys, 
                              'user': request.user }, 
                              context_instance=RequestContext(request))

def apropos(request):
    return render_to_response('pages/apropos.html', 
                             {'user': request.user },
                             context_instance=RequestContext(request))

def association(request):
    return render_to_response('pages/association.html', 
                             {'user': request.user },
                             context_instance=RequestContext(request))

def canal_n7(request):
    return render_to_response('pages/canal_n7.html', 
                             {'user': request.user },
                             context_instance=RequestContext(request))

def contact(request):
    return render_to_response('pages/contact.html',
                             {'user': request.user },
                             context_instance=RequestContext(request))

def international(request):
    return render_to_response('pages/international.html', 
                             {'user': request.user },
                             context_instance=RequestContext(request))

def mentions_legales(request):
    return render_to_response('pages/mentions_legales.html', 
                             {'user': request.user },
                             context_instance=RequestContext(request))

def publications(request):
    return render_to_response('pages/publications.html', 
                             {'user': request.user },
                             context_instance=RequestContext(request))

def rss(request):
    return render_to_response('pages/rss.html', 
                             {'user': request.user },
                             context_instance=RequestContext(request))

def sitemap(request):
    return render_to_response('pages/sitemap.html', 
                             {'user': request.user },
                             context_instance=RequestContext(request))

