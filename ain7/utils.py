# -*- coding: utf-8
"""
 ain7/utils.py
"""
#
#   Copyright © 2007-2010 AIn7 Devel Team
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

from string import Template

from django import forms
from django.conf import settings
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, TemplateSyntaxError
from django.utils.translation import ugettext as _

# the separator used in CSV exports, when a cell contains a list of values
CSV_INNERSEP = '|'

CONFIDENTIALITY_LEVELS = (
    (0, _('published in directory and website')),
    (1, _('published in website only')),
    (2, _('published in directory only')),
    (3, _('private')),
    )

def ain7_website_confidential(obj):
    if not isinstance(obj, models.Model):
        raise NotImplementedError
    return (obj.confidentiality>1)

# pour alléger les appels à render_to_response
# http://www.djangosnippets.org/snippets/3/
# Serait pas mieux d'utiliser un ContextProcessor ?
# http://docs.djangoproject.com/en/dev/ref/templates/api/#writing-your-own-context-processors
def ain7_render_to_response(req, *args, **kwargs):

    user_groups = []

    if req.user.is_authenticated():
        user_groups = req.user.person.groups.values_list('group__name', flat=True)

    args[1]['portal_version'] = settings.VERSION
    args[1]['tinymce_version'] = settings.TINYMCE_VERSION
    args[1]['mootools_version'] = settings.MOOTOOLS_VERSION
    args[1]['jquery_version'] = settings.JQUERY_VERSION
    args[1]['piwik_url'] = settings.PIWIK_URL
    args[1]['piwik_site_id'] = settings.PIWIK_SITE_ID
    args[1]['request'] = req
    args[1]['superadmin'] = settings.AIN7_PORTAL_ADMIN in user_groups
    args[1]['ca_member'] = 'ain7-ca' in user_groups
    args[1]['secretariat_member'] = 'ain7-secretariat' in user_groups
    args[1]['contributeur'] = 'ain7-contributeur' in user_groups
    kwargs['context_instance'] = RequestContext(req)
    return render_to_response(*args, **kwargs)

def isAdmin(user):
    """détermine si un user a le profil administrateur"""

    from ain7.annuaire.models import Person
    from ain7.groups.models import Group

    try:
        person = Person.objects.get(user=user)
        portal_admin = Group.objects.get(name=settings.AIN7_PORTAL_ADMIN)
        if portal_admin in person.groups.values_list('group__name', flat=True):
            return True
    except Group.DoesNotExist:
        return False
    else:
        return False

def check_access(request, user, groups):

    user_groups = user.person.groups.values_list('group__name', flat=True)

    if settings.AIN7_PORTAL_ADMIN in user_groups:
        return None

    for group in user_groups:
        if group in groups:
            return None

    return ain7_render_to_response(request, 'pages/permission_denied.html', {})

def ain7_generic_edit(request, obj, MyForm, formInitDict, formPage, \
    formPageDict, saveDict, redirectPage, msgDone):
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
            for k, v in formInitDict.iteritems():
                f.cleaned_data[k] = v
            obj = f.save(**saveDict)
            if isinstance(obj, LoggedClass) and request.user:
                obj.logged_save(request.user.person)
            request.user.message_set.create(message=msgDone)
        else:
            pageDict = {'form': f}
            pageDict.update(formPageDict)
            request.user.message_set.create(message=\
                _('Something was wrong in the form you filled. No modification done.'))
            return ain7_render_to_response(request, formPage, pageDict)
        redirect = redirectPage
        if obj:
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
    last_change_by = models.ForeignKey('annuaire.Person',
        verbose_name=_('modifier'), editable=False,
        related_name='last_changed_%(class)s', blank=True, null=True)
    last_change_at = models.DateTimeField(verbose_name=_('last changed at'),
        blank=True, editable=False)

    class Meta:
        abstract = True
        
    def logged_save(self, person):
        self.last_change_by = person
        return self.save()
        
    def save(self):
        self.last_change_at = datetime.datetime.now()
        return super(LoggedClass, self).save()
        
def generic_show_last_change(logged_obj):
    """ Utilisé pour le rendu du tag show_last_change.
    Peut être utilisé sur tout objet dont le modèle hérite de LoggedClass."""
    if not isinstance(logged_obj, LoggedClass):
        raise TemplateSyntaxError, \
            "show_last_change should only be used with LoggedClass objects."
    return {'obj': logged_obj}

class AIn7ModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AIn7ModelForm, self).__init__(*args, **kwargs)
        tag_required_fields(self)

class AIn7Form(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AIn7Form, self).__init__(*args, **kwargs)
        tag_required_fields(self)

def tag_required_fields(form):
    if isinstance(form, forms.BaseForm):
        for fname, field in form.fields.iteritems():
            # si on veut mettre le type de champ comme classe CSS :
            # new_classes = set((type(field).__name__, type(field.widget).__name__, field.required and "Required" or "Optional"))
            new_classes = set([field.required and "requiredField" or "optionalField"])
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] = \
                   " ".join(set(field.widget.attrs['class'].split()).\
                   union(new_classes))
            else:
                field.widget.attrs['class'] = " ".join(new_classes)

