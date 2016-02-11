# -*- coding: utf-8
"""
 ain7/utils.py
"""
#
#   Copyright © 2007-2016 AIn7 Devel Team
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

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template import TemplateSyntaxError
from django.utils import timezone
from django.utils.translation import ugettext as _

# the separator used in CSV exports, when a cell contains a list of values
CSV_INNERSEP = '|'

CONFIDENTIALITY_LEVELS = (
    (0, _('public')),
    (1, _('private')),
    )


def ain7_website_confidential(obj):
    if not isinstance(obj, models.Model):
        raise NotImplementedError
    return (obj.confidentiality > 0)


def is_admin(user):
    """détermine si un user a le profil administrateur"""

    from ain7.annuaire.models import Person
    from ain7.groups.models import Group

    try:
        person = Person.objects.get(user=user)
        portal_admin = Group.objects.get(name=settings.PORTAL_ADMIN)
        if portal_admin in person.groups.values_list('group__name', flat=True):
            return True
    except Group.DoesNotExist:
        return False
    else:
        return False


def check_access(request, user, groups):

    from ain7.annuaire.models import Person

    if Person.objects.filter(user=user):
        user_groups = user.person.groups.values_list('group__name', flat=True)

        if settings.PORTAL_ADMIN in user_groups:
            return None

        for group in user_groups:
            if group in groups:
                return None

    return render(request, 'pages/permission_denied.html', {})


def ain7_generic_delete(request, obj, redirectPage, msgDone):
    """ Méthode générique pour supprimer un objet."""

    obj.delete()
    messages.success(request, msgDone)
    return HttpResponseRedirect(redirectPage)


class LoggedClass(models.Model):
    """ Classe abstraite contenant les infos à enregistrer pour les modèles
    pour lesquels on veut connaître la date de création/modif et l'auteur."""
    last_change_by = models.ForeignKey(
        'annuaire.Person',
        verbose_name=_('modifier'), editable=False,
        related_name='last_changed_%(class)s', blank=True, null=True
    )
    last_change_at = models.DateTimeField(
        verbose_name=_('last changed at'),
        blank=True, editable=False
    )

    class Meta:
        abstract = True

    def logged_save(self, person):
        self.last_change_by = person
        return self.save()

    def save(self, *args, **kwargs):
        self.last_change_at = timezone.now()
        return super(LoggedClass, self).save(*args, **kwargs)


def generic_show_last_change(logged_obj):
    """ Utilisé pour le rendu du tag show_last_change.
    Peut être utilisé sur tout objet dont le modèle hérite de LoggedClass."""
    if not isinstance(logged_obj, LoggedClass):
        raise TemplateSyntaxError, \
            "show_last_change should only be used with LoggedClass objects."
    return {'obj': logged_obj}


def get_root_url(request=None):
    if request:
        return 'http' + ('', 's')[request.is_secure()] + '://' + request.get_host()
    else:
        from django.contrib.sites.models import Site
        return 'http://'+Site.objects.all()[0].domain


class AIn7ModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AIn7ModelForm, self).__init__(*args, **kwargs)


class AIn7Form(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AIn7Form, self).__init__(*args, **kwargs)

import unicodedata

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii


def generate_login(first_name, last_name):

    first_name = remove_accents(first_name)
    last_name = remove_accents(last_name)

    """login generation"""
    login = (first_name[0] + last_name).lower()

    tries = 0
    while (User.objects.filter(username=login).count() > 0):
        tries = tries + 1
        if tries < len(first_name):
            login = (first_name[0:tries] + last_name).lower()
        else:
            login = (first_name[0] + last_name + str(tries)).lower()

    return login
