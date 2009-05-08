# -*- coding: utf-8
#
# groupes_professionnels/views.py
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

from ain7.annuaire.models import Person
from ain7.decorators import confirmation_required
from ain7.groupes_professionnels.models import *
from ain7.groupes_professionnels.forms import *
from ain7.pages.models import Text
from ain7.utils import ain7_render_to_response, ain7_generic_edit, ain7_generic_delete, check_access


def index(request):
    text = Text.objects.get(shortname='groupes_professionnels')
    groups = GroupPro.objects.all().order_by('name')
    return ain7_render_to_response(request, 'groupes_professionnels/index.html',
                    {'groups': groups, 'text': text})

def details(request, group_id):
    g = get_object_or_404(GroupPro, pk=group_id)
    return ain7_render_to_response(request, 
                        'groupes_professionnels/details.html', {'group': g})

@login_required
def subscribe(request, group_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    group = get_object_or_404(GroupPro, pk=group_id)
    f =  SubscribeGroupProForm()

    if request.method == 'POST':
        f = SubscribeGroupProForm(request.POST)
        if f.is_valid():
            person = Person.objects.get(id=f.cleaned_data['member'])
            # on vérifie que la personne n'est pas déjà inscrite
            already_subscribed = False
            for subscription in person.group_memberships.all():
                if subscription.group == group:
                    already_subscribed = True
            if not already_subscribed:            
                membership = f.save(group=group)
                p = membership.member
                request.user.message_set.create(
                    message=_('You have successfully subscribed')+
                    ' '+p.first_name+' '+p.last_name+' '+_('to this group.'))
                return HttpResponseRedirect(reverse(details, args=[group.id]))
            else:
                request.user.message_set.create(
                message=_('This person is already subscribed to this group.'))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 
         'groupes_professionnels/subscribe.html',
        {'group': group, 'form': f, 'back': back,
         'group_list': GroupPro.objects.all()})

@login_required
def unsubscribe(request, group_id):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat'])
    if r:
        return r

    group = get_object_or_404(GroupPro, pk=group_id)

    if request.method == 'POST':
        f = UnsubscribeGroupProForm(request.POST)
        if f.is_valid():
            person = f.cleaned_data['member']
            if group.has_for_member(person):
                f.unsubscribe(group)
                request.user.message_set.create(
                    message=_('Subscription successfully removed.'))
            else:
                request.user.message_set.create(
               message=_('This person is not a member of this group. Nothing done.'))                
        else:
            request.user.message_set.create(
                message=_('Something was wrong in the form you filled. No modification done.'))
        return HttpResponseRedirect(reverse(details, args=[group.id]))

    f =  UnsubscribeGroupProForm()
    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(
        request, 'groupes_professionnels/subscribe.html',
        {'group': group, 'form': f, 'back': back,
         'group_list': GroupPro.objects.all()})



@login_required
def edit(request, group_id=None):

    r = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat', 'ain7-contributeur'])
    if r:
        return r

    if group_id is None:
        form = GroupProForm()

    else:
        group = GroupPro.objects.get(pk=group_id)
        form = GroupProForm(instance=group)

        if request.method == 'POST':
             form = GroupProForm(request.POST, instance=group)
             if form.is_valid():
                 form.save(user=request.user)
                 request.user.message_set.create(
                     message=_("Modifications have been successfully saved."))
                 return HttpResponseRedirect(reverse(details, args=[group.id]))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 'groupes_professionnels/edit.html', {'form': form, 'group': group, 'back': back})

@login_required
def build_roles_by_type(request, group=None, all_current=None,
    the_type=None, form_for_the_type=None,
    the_role=None, form_for_the_role=None):
    """Structure les données à passer à la page d'édition d'un groupe
    professionnel.
    group: le groupe professionnel
    all_current: 'current' n'affiche que les membres actuelles, 'all' tous
    the_type, form_for_the_type: on peut envoyer un formulaire spécifique
        à un type (exple: ajouter un responsable)
    the_role, form_for_role: on peut envoyer un formulaire spécifique
        à un role (exple: changer les dates d'un membre donné)"""
    roles_by_type = []
    for a_type, a_type_display in GroupProRole.ROLE_TYPE:
        a_form = None
        if str(a_type)==the_type: a_form = form_for_the_type
        if all_current == 'current':
            roles = [ r for r in group.current_roles() if r.type==a_type ]
        else:
            roles = [ r for r in group.roles.all() if r.type==a_type ]
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
def edit_roles(request, group_id, all_current=None):

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r

    group = get_object_or_404(GroupPro, pk=group_id)
    is_member = request.user.is_authenticated()\
                and group.has_for_member(request.user.person)
    roles_by_type = build_roles_by_type(request, group, all_current,
                                        None, None, None, None)
    return ain7_render_to_response(request,
        'groupes_professionnels/edit_roles.html',
        {'group': group, 'is_member': is_member,
         'roles_by_type': roles_by_type, 'all_current': all_current,
         'back': request.META.get('HTTP_REFERER', '/')})

@login_required
def add_role(request, group_id=None, type=None, all_current=None):

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r

    group = get_object_or_404(GroupPro, pk=group_id)
    is_member = request.user.is_authenticated()\
                and group.has_for_member(request.user.person)
    
    form = None
    if request.method=='GET':
        form = NewRoleForm()
    roles_by_type = build_roles_by_type(
        request, group, all_current, type, form, None, None)
    
    if request.method == 'POST':
        form = NewRoleForm(request.POST)
        if form.is_valid():
            gr = form.save(group, type)
            return HttpResponseRedirect(reverse(edit_roles, args=[group.id,all_current]))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            roles_by_type = build_roles_by_type(
                request, group, all_current, type, form, None, None)
    return ain7_render_to_response(request,
        'groupes_professionnels/edit_roles.html',
        {'group': group, 'is_member': is_member,
         'roles_by_type': roles_by_type, 'all_current': all_current,
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda group_id=None, role_id=None, all_current=None: str(get_object_or_404(GroupProRole, pk=role_id)), 'groupes_professionnels/base.html', _('Do you really want to remove the role of this person (you can end a role by setting its end date)'))
@login_required
def delete_role(request, group_id=None, role_id=None, all_current=None):

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r

    return ain7_generic_delete(request,
        get_object_or_404(GroupProRole, pk=role_id),
        reverse(edit_roles, args=[group_id,all_current]),
        _('Role successfully deleted.'))

@login_required
def change_dates(request, group_id=None, role_id=None, all_current=None):

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r

    group = get_object_or_404(GroupPro, pk=group_id)
    is_member = request.user.is_authenticated()\
                and group.has_for_member(request.user.person)
    role = get_object_or_404(GroupProRole, pk=role_id)
    roles_by_type = build_roles_by_type(
        request, group, all_current, None, None, role,
        ChangeDatesForm(initial={'start_date': role.start_date,
                                 'end_date': role.end_date}))

    if request.method == 'POST':
        form = ChangeDatesForm(request.POST)
        if form.is_valid():
            form.save(role)
            return HttpResponseRedirect(reverse(edit_roles, args=[group.id,all_current]))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            roles_by_type = build_roles_by_type(
                request, group, all_current, None, None, role, form)
    return ain7_render_to_response(request,
        'groupes_professionnels/edit_roles.html',
        {'group': group, 'is_member': is_member,
         'roles_by_type': roles_by_type, 'all_current': all_current,
         'back': request.META.get('HTTP_REFERER', '/')})
