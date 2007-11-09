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
import smtplib
import time

from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import newforms as forms

from ain7 import settings

class ImgUploadForm(forms.Form):
    img_file = forms.Field(widget=forms.FileInput, label='')

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def planet(request):
    return HttpResponseRedirect(settings.PLANET_URL)

def forums(request):
    return HttpResponseRedirect(settings.FORUMS_URL)

def galerie(request):
    return HttpResponseRedirect(settings.GALLERY_URL)

# pour alléger les appels à render_to_response
# http://www.djangosnippets.org/snippets/3/
def ain7_render_to_response(req, *args, **kwargs):
    kwargs['context_instance'] = RequestContext(req)
    return render_to_response(*args, **kwargs)
