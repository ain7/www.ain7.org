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
from ain7.pages.forms import LostPasswordForm

def homepage(request):
    news = NewsItem.objects.all().order_by('-creation_date')[:2]
    is_auth = request.user.is_authenticated()
    surveys = [(s, (is_auth and s.has_been_voted_by(request.user.person)))\
               for s in Survey.objects.all() if s.is_valid()][:2]
    return ain7_render_to_response(request, 'pages/homepage.html', 
                            {'news': news , 'surveys': surveys})

def lostpassword(request):

    form = LostPasswordForm()

    return ain7_render_to_response(request, 'pages/lostpassword.html', {'form': form})

def apropos(request):
    return ain7_render_to_response(request, 'pages/apropos.html', {})

def count_members():
    nb_members = AIn7Member.objects.all().count()
    return nb_members

def count_subscribers():
    nb_subscribers = AIn7Member.objects.all().count()
    return nb_subscribers

def association(request):
   # calcul du nombre d'AIn7Member
    return ain7_render_to_response(request, 'pages/association.html', {'count_members': count_members(), 'count_subscribers': count_subscribers()})

def status(request):
    return ain7_render_to_response(request, 'pages/status.html', {'count_members': count_members(), 'count_subscribers': count_subscribers()})

def board(request):
    return ain7_render_to_response(request, 'pages/board.html', {'count_members': count_members(), 'count_subscribers': count_subscribers()})

def council(request):
    return ain7_render_to_response(request, 'pages/council.html', {'count_members': count_members(), 'count_subscribers': count_subscribers()})

def contact(request):
    return ain7_render_to_response(request, 'pages/contact.html', {'count_members': count_members(), 'count_subscribers': count_subscribers()})

def canal_n7(request):
    return ain7_render_to_response(request, 'pages/canal_n7.html', {})

def international(request):
    return ain7_render_to_response(request, 'pages/international.html', {})

def mentions_legales(request):
    return ain7_render_to_response(request, 'pages/mentions_legales.html', {})

def publications(request):
    return ain7_render_to_response(request, 'pages/publications.html', {})

def rss(request):
    return ain7_render_to_response(request, 'pages/rss.html', {})

