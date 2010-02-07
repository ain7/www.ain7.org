# -*- coding: utf-8
"""
 ain7/association/views.py
"""
#
#   Copyright © 2007-2009 AIn7 Devel Team
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

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from ain7.annuaire.models import AIn7Member
from ain7.association.models import CouncilRole
from ain7.association.forms import ChangeDatesForm, NewCouncilRoleForm
from ain7.decorators import confirmation_required
from ain7.pages.models import Text
from ain7.utils import ain7_render_to_response, ain7_generic_delete


def count_members():
    """count all members of the association"""
    nb_members = AIn7Member.objects.all().count()
    return nb_members

def current_council_roles():
    """current council roles"""
    return [ rol for rol in CouncilRole.objects.all() if rol.current() ]

def current_board_roles():
    """current board roles"""
    return [ rol for rol in CouncilRole.objects.filter(board_member=True) \
        if rol.current() ]

def index(request):
    """index page"""
    text = Text.objects.get(textblock__shortname='presentation_ain7') 
    return ain7_render_to_response(request, 'association/index.html', 
                {'count_members': count_members(), 'text': text}) 
 
def status(request):
    """status page""" 
    text = Text.objects.get(textblock__shortname='statuts_ain7') 
    return ain7_render_to_response(request, 'association/status.html', 
                {'count_members': count_members(), 'text': text}) 
 
def council(request):
    """council presentation page"""
    return ain7_render_to_response(request, 'association/council.html',
        {'count_members': count_members(),
         'current_roles': current_council_roles() }) 
 
def contact(request):
    """contact page"""
    text = Text.objects.get(textblock__shortname='contact_ain7') 
    return ain7_render_to_response(request, 'association/contact.html', 
          {'count_members': count_members(), 'text': text}) 

def activites(request):
    """activities page"""
    text = Text.objects.get(textblock__shortname='activites_ain7') 
    return ain7_render_to_response(request, 'association/activites.html', 
          {'count_members': count_members(), 'text': text}) 

@login_required
def build_council_roles_by_type(request, all_current=None,
    the_type=None, form_for_the_type=None,
    the_role=None, form_for_the_role=None):
    """Structure les données à passer à la page d'édition du CA.
    all_current: 'current' n'affiche que les membres actuelles, 'all' tous
    the_type, form_for_the_type: on peut envoyer un formulaire spécifique
        à un type (exple: ajouter un secrétaire)
    the_role, form_for_role: on peut envoyer un formulaire spécifique
        à un role (exple: changer les dates d'un membre donné)"""
    roles_by_type = []
    for a_type, a_type_display in CouncilRole.COUNCIL_ROLE:
        a_form = None
        if str(a_type)==the_type:
            a_form = form_for_the_type
        if all_current == 'current':
            roles = [ r for r in current_council_roles() if r.role==a_type]
        else:
            roles = CouncilRole.objects.filter(role=a_type).\
                order_by('-start_date')
        this_types_roles = []
        for role in roles:
            if role == the_role:
                this_types_roles.append((role, form_for_the_role))
            else:
                this_types_roles.append((role, None))
        roles_by_type.append((a_type, a_type_display,
                              a_form, this_types_roles))
    return roles_by_type

@login_required
def edit_council(request, all_current=None):
    """edit council"""
    roles_by_type = build_council_roles_by_type(request, all_current,
                                        None, None, None, None)
    return ain7_render_to_response(request,
        'association/edit_council.html',
        {'roles_by_type': roles_by_type, 'all_current': all_current,
         'count_members': count_members(), 
         'back': request.META.get('HTTP_REFERER', '/')})

@login_required
def add_council_role(request, role_type=None, all_current=None):
    """add new council role"""
    form = NewCouncilRoleForm()
    roles_by_type = build_council_roles_by_type(
        request, all_current, role_type, form, None, None)
    
    if request.method == 'POST':
        form = NewCouncilRoleForm(request.POST)
        if form.is_valid():
            form.save(role_type)
            return HttpResponseRedirect(reverse(edit_council,
                 args=[all_current]))
        else:
            request.user.message_set.create(message=_('Something was wrong in\
 the form you filled. No modification done.'))
            # TODO : le champ username n'est pas renseigné ici (LP 346274)
            roles_by_type = build_council_roles_by_type(
                request, all_current, role_type, form, None, None)
    return ain7_render_to_response(request,
        'association/edit_council.html',
        {'roles_by_type': roles_by_type, 'all_current': all_current,
         'count_members': count_members(), 
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda role_id=None, all_current=None:
     str(get_object_or_404(CouncilRole, pk=role_id)), 'association/base.html',
     _('Do you really want to remove the role of this person (you can end a\
 role by setting its end date)'))
@login_required
def delete_council_role(request, role_id=None, all_current=None):
    """delete council role"""
    return ain7_generic_delete(request,
        get_object_or_404(CouncilRole, pk=role_id),
        reverse(edit_council, args=[all_current]),
        _('Role successfully deleted.'))

@login_required
def change_council_dates(request, role_id=None, all_current=None):
    """change council dates"""
    role = get_object_or_404(CouncilRole, pk=role_id)
    roles_by_type = build_council_roles_by_type(
        request, all_current, None, None, role,
        ChangeDatesForm(initial={'start_date': role.start_date,
                                 'end_date': role.end_date}))

    if request.method == 'POST':
        form = ChangeDatesForm(request.POST)
        if form.is_valid():
            form.save(role)
            return HttpResponseRedirect(reverse(edit_council,
                 args=[all_current]))
        else:
            request.user.message_set.create(message=_('Something was wrong\
 in the form you filled. No modification done.'))
            roles_by_type = build_council_roles_by_type(
                request, all_current, None, None, role, form)
    return ain7_render_to_response(request,
        'association/edit_council.html',
        {'roles_by_type': roles_by_type, 'all_current': all_current,
         'count_members': count_members(),          
         'back': request.META.get('HTTP_REFERER', '/')})

