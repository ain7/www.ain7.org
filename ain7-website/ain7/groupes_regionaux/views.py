# -*- coding: utf-8
#
# groupes_regionaux/views.py
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

from ain7.groupes_regionaux.models import Group

def index(request):
    groups = Group.objects.all().filter(is_active=True).order_by('name')
    return render_to_response('groupes_regionaux/index.html', {'groups': groups, 'user': request.user})

def detail(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    return render_to_response('groupes_regionaux/details.html', {'group': group, 'user': request.user})
