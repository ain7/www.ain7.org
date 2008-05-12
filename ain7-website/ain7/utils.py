# -*- coding: utf-8
#
# utils.py
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
import smtplib
import time

from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import newforms as forms
from django.db import models
from django.utils.translation import ugettext as _

from ain7 import settings
from ain7.widgets import DateTimeWidget

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
    args[1]['portal_version'] = settings.VERSION
    args[1]['tinymce_version'] = settings.TINYMCE_VERSION
    args[1]['mootools_version'] = settings.MOOTOOLS_VERSION
    kwargs['context_instance'] = RequestContext(req)
    return render_to_response(*args, **kwargs)

# détermine si un user a le profil administrateur
def isAdmin(user):
    result = False
    for profileMembership in user.profiles.all():
        if profileMembership.profile.name == 'admin':
            result = True
    return result

def ain7_generic_edit(request, user_id, obj, MyForm, formInitDict, formPage, formPageDict, redirectPage, msgDone):
    """ Méthode utilisée pour éditer (ou créer) un objet de façon standard,
    c'est-à-dire via un formulaire de type ModelForms.
    obj : objet à éditer. S'il s'agit de None, on est en mode création.
    MyForm : la classe du formulaire.
    formInitDict : données de l'objet exclues du formulaire.
    formPage : template du formulaire.
    formPageDict : dictionnaire passé au template du formulaire.
    redirectPage : redirection après le formulaire.
    msgDone : message en cas de succès."""
    
    # 1er passage : on propose un formulaire avec les données actuelles
    if request.method == 'GET':
        if obj:
            f = MyForm(instance=obj)
        else:
            f = MyForm()
        pageDict = {'form': f}
        pageDict.update(formPageDict)
        return ain7_render_to_response(request, formPage, pageDict)

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        if obj:
            f = MyForm(request.POST.copy(), instance=obj)
        else:
            f = MyForm(request.POST.copy())
        if f.is_valid():
            for k,v in formInitDict.iteritems():
                f.cleaned_data[k] = v
            f.save()
            request.user.message_set.create(message=msgDone)
        else:
            pageDict = {'form': f}
            pageDict.update(formPageDict)
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            return ain7_render_to_response(request, formPage, pageDict)
        return HttpResponseRedirect(redirectPage)

def ain7_generic_delete(request, obj, redirectPage, msgDone):
    """ Méthode générique pour supprimer un objet."""

    obj.delete()
    request.user.message_set.create(message=msgDone)
    return HttpResponseRedirect(redirectPage)

