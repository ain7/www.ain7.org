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
from string import Template

from django.contrib import auth
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms
from django.db import models
from django.utils.translation import ugettext as _
from django import template

from ain7 import settings
from ain7.widgets import DateTimeWidget

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

    user_groups = req.user.groups.all().values_list('name', flat=True)

    args[1]['portal_version'] = settings.VERSION
    args[1]['tinymce_version'] = settings.TINYMCE_VERSION
    args[1]['mootools_version'] = settings.MOOTOOLS_VERSION
    args[1]['mootools_more_version'] = settings.MOOTOOLS_MORE_VERSION
    args[1]['debug_mode'] = settings.DEBUG
    args[1]['user_groups'] = user_groups
    kwargs['context_instance'] = RequestContext(req)
    return render_to_response(*args, **kwargs)

# détermine si un user a le profil administrateur
def isAdmin(user):
    try:
        portal_admin = Group.objects.get(name=settings.AIN7_PORTAL_ADMIN)
        if portal_admin in user.groups.all():
            return True
    except Group.DoesNotExist:
        return False
    else:
        return False

def check_access(request, user, groups):

    user_groups = user.groups.values_list('name', flat=True)

    if settings.AIN7_PORTAL_ADMIN in user_groups:
        return None

    for group in user_groups:
       if group in groups:
           return None

    return ain7_render_to_response(request, 'pages/permission_denied.html', {})


def ain7_generic_edit(request, obj, MyForm, formInitDict, formPage, formPageDict, saveDict, redirectPage, msgDone):
    """ Méthode utilisée pour éditer (ou créer) un objet de façon standard,
    c'est-à-dire via un formulaire de type ModelForms.
    obj : objet à éditer. S'il s'agit de None, on est en mode création.
    MyForm : la classe du formulaire.
    formInitDict : données de l'objet exclues du formulaire.
    formPage : template du formulaire.
    formPageDict : dictionnaire passé au template du formulaire.
    saveDict : argument passés à la méthode save du formulaire.
    redirectPage : redirection après le formulaire. Utiliser $objid pour l'identifiant de l'objet.
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
            f = MyForm(request.POST.copy(), request.FILES, instance=obj)
        else:
            f = MyForm(request.POST.copy(), request.FILES)
        if f.is_valid():
            for k,v in formInitDict.iteritems():
                f.cleaned_data[k] = v
            obj = f.save(**saveDict)
            if isinstance(obj, LoggedClass) and request.user:
                obj.logged_save(request.user)
            request.user.message_set.create(message=msgDone)
        else:
            pageDict = {'form': f}
            pageDict.update(formPageDict)
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            return ain7_render_to_response(request, formPage, pageDict)
        redirect = Template(redirectPage).substitute(objid=obj.id)
        return HttpResponseRedirect(redirect)

def ain7_generic_delete(request, obj, redirectPage, msgDone):
    """ Méthode générique pour supprimer un objet."""

    obj.delete()
    request.user.message_set.create(message=msgDone)
    return HttpResponseRedirect(redirectPage)

 
class LoggedClass(models.Model):
    """ Classe abstraite contenant les infos à enregistrer pour les modèles
    pour lesquels on veut connaître la date de création/modif et l'auteur."""
    last_change_by = models.ForeignKey(User, verbose_name=_('modifier'), editable=False,
        related_name='last_changed_%(class)s', blank=True, null=True)
    last_change_at = models.DateTimeField(verbose_name=_('last changed at'), blank=True, editable=False)

    class Meta:
        abstract = True
        
    def logged_save(self, user):
        self.last_change_by = user
        return self.save()
        
    def save(self):
        self.last_change_at = datetime.datetime.now()
        return super(LoggedClass, self).save()
        
def generic_show_last_change(logged_obj):
    """ Utilisé pour le rendu du tag show_last_change.
    Peut être utilisé sur tout objet dont le modèle hérite de LoggedClass."""
    if not isinstance(logged_obj, LoggedClass):
        raise django.template.TemplateSyntaxError,\
            "show_last_change should only be used with LoggedClass objects."
    return {'obj': logged_obj}

