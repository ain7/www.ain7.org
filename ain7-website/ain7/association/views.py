# -*- coding: utf-8
#
# association/views.py
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

from ain7.utils import ain7_render_to_response
from ain7.annuaire.models import AIn7Member

def count_members():
    nb_members = AIn7Member.objects.all().count()
    return nb_members

def count_subscribers():
    nb_subscribers = AIn7Member.objects.all().count()
    return nb_subscribers

def index(request): 
   # calcul du nombre d'AIn7Member 
    return ain7_render_to_response(request, 'association/index.html', {'count_members': count_members(), 'count_subscribers': count_subscribers()}) 
 
def status(request): 
    return ain7_render_to_response(request, 'association/status.html', {'count_members': count_members(), 'count_subscribers': count_subscribers()}) 
 
def board(request): 
    return ain7_render_to_response(request, 'association/board.html', {'count_members': count_members(), 'count_subscribers': count_subscribers()}) 
 
def council(request): 
    return ain7_render_to_response(request, 'association/council.html', {'count_members': count_members(), 'count_subscribers': count_subscribers()}) 
 
def contact(request): 
    return ain7_render_to_response(request, 'association/contact.html', {'count_members': count_members(), 'count_subscribers': count_subscribers()}) 

