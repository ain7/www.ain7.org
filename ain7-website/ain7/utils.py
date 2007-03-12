# -*- coding: utf-8
#
# utils.py
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

from django.contrib.auth.models import User
from django.contrib import auth
from django.http import HttpResponseRedirect
from ain7 import settings

def login(request):
    username = request.POST['username']
    password = request.POST['password']

    user = auth.authenticate(username=username, password=password)
    auth.login(request, user)
    request.session['user_id'] = user.id
    user.last_login = datetime.datetime.now()
    user.save()

    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def planet(request):
    return HttpResponseRedirect(settings.PLANET_URL)

def forums(request):
    return HttpResponseRedirect(settings.FORUMS_URL)

