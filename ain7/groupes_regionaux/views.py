# -*- coding: utf-8
"""
 ain7/groupes_regionaux/views.py
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

import datetime

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from ain7.decorators import confirmation_required
from ain7.groupes_regionaux.models import Group, GroupMembership, GroupRole
from ain7.groupes_regionaux.forms import *
from ain7.pages.models import Text
from ain7.utils import ain7_render_to_response
from ain7.utils import ain7_generic_delete, check_access


def index(request):
    """index page"""
    groups = Group.objects.all().filter(is_active=True).order_by('name')
    text = Text.objects.get(textblock__shortname='groupes_regionaux')
    return ain7_render_to_response(request, 'groupes_regionaux/index.html',
                            {'groups': groups, 'text': text})

def details(request, group_shortname):
    """regional group details"""
    group = get_object_or_404(Group, shortname=group_shortname)
    is_member = request.user.is_authenticated()\
                and group.has_for_member(request.user.person)

    return ain7_render_to_response(request, 'groupes_regionaux/details.html',
                            {'group': group, 'is_member': is_member})

@login_required
def edit(request, group_shortname):
    """edit regional group"""

    access = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat',
        'ain7-contributeur'])
    if access:
        return access

    group = get_object_or_404(Group, shortname=group_shortname)
    is_member = request.user.is_authenticated()\
                and group.has_for_member(request.user.person)

    form = GroupForm(instance=group)

    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            request.user.message_set.create(
                message=_("Modifications have been successfully saved."))
            return HttpResponseRedirect(reverse(details,
                args=[group.shortname]))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 'groupes_regionaux/edit.html', 
         {'form': form, 'group': group, 'back': back, 'is_member': is_member})

@login_required
def join(request, group_shortname):
    """join regional group"""

    group = get_object_or_404(Group, shortname=group_shortname)
    person = request.user.person

    access = check_access(request, request.user, ['ain7-membre'])
    if access:
        return access

    if not group.has_for_member(person):
        grp_membership = GroupMembership()
        grp_membership.type = 7
        grp_membership.group = group
        grp_membership.member = person
        grp_membership.save()
        request.user.message_set.create(message=
            _("You have been successfully added to this group."))
    else:
        request.user.message_set.create(message=
            _("You are already a member of this group."))

    return HttpResponseRedirect(reverse(details, args=[group.shortname]))

@confirmation_required(lambda group_shortname: 
    str(get_object_or_404(Group, shortname=group_shortname)),
    'groupes_regionaux/base.html', _('Do you really want to quit the group'))
@login_required
def quit(request, group_shortname):
    """leave regional group"""

    group = get_object_or_404(Group, shortname=group_shortname)
    person = request.user.person

    access = check_access(request, request.user, ['ain7-membre'])
    if access:
        return access

    if group.has_for_member(person):
        if group.has_for_board_member(person):
            request.user.message_set.create(message=
                _("You are a member of the office of this group. You have to \
unsubscribe from every role in your group before leaving it."))
        else:
            membership = GroupMembership.objects\
                .filter(group=group, member=person)\
                .exclude(end_date__isnull=False, end_date__lte=\
                datetime.datetime.now())\
                .latest('end_date')
            membership.end_date = datetime.datetime.now()
            membership.save()
            request.user.message_set.create(message=
               _('You have been successfully removed from this group.'))
    else:
        request.user.message_set.create(message=
            _("You are not a member of this group."))

    return HttpResponseRedirect(reverse(details, args=[group.shortname]))

@login_required
def build_roles_by_type(request, group=None, all_current=None,
    the_type=None, form_for_the_type=None,
    the_role=None, form_for_the_role=None):
    """Structure les données à passer à la page d'édition d'un groupe
    régional.
    group: le groupe régional
    all_current: 'current' n'affiche que les membres actuelles, 'all' tous
    the_type, form_for_the_type: on peut envoyer un formulaire spécifique
        à un type (exple: ajouter un secrétaire)
    the_role, form_for_role: on peut envoyer un formulaire spécifique
        à un role (exple: changer les dates d'un membre donné)"""
    roles_by_type = []
    for a_type, a_type_display in GroupRole.ROLE_TYPE:
        a_form = None
        if str(a_type)==the_type:
            a_form = form_for_the_type
        if all_current == 'current':
            roles = group.office_memberships().filter(type=a_type).\
                order_by('-start_date')
        else:
            roles = group.roles.filter(type=a_type).order_by('-start_date')
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
def edit_roles(request, group_shortname, all_current=None):
    """edit regional group"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access

    group = get_object_or_404(Group, shortname=group_shortname)
    is_member = request.user.is_authenticated()\
                and group.has_for_member(request.user.person)
    roles_by_type = build_roles_by_type(request, group, all_current,
                                        None, None, None, None)
    return ain7_render_to_response(request,
        'groupes_regionaux/edit_roles.html',
        {'group': group, 'is_member': is_member,
         'roles_by_type': roles_by_type, 'all_current': all_current,
         'back': request.META.get('HTTP_REFERER', '/')})

@login_required
def add_role(request, group_shortname=None, type=None, all_current=None):
    """add role to a regional group"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access

    group = get_object_or_404(Group, shortname=group_shortname)
    is_member = request.user.is_authenticated()\
                and group.has_for_member(request.user.person)
    
    form = None
    if request.method == 'GET':
        form = NewRoleForm()
    roles_by_type = build_roles_by_type(
        request, group, all_current, type, form, None, None)
    
    if request.method == 'POST':
        form = NewRoleForm(request.POST)
        if form.is_valid():
            form.save(group, type)
            return HttpResponseRedirect(reverse(edit_roles, 
                args=[group.shortname, all_current]))
        else:
            request.user.message_set.create(message=
                _('Something was wrong in the form you filled.\
 No modification done.'))
            roles_by_type = build_roles_by_type(
                request, group, all_current, type, form, None, None)
    return ain7_render_to_response(request,
        'groupes_regionaux/edit_roles.html',
        {'group': group, 'is_member': is_member,
         'roles_by_type': roles_by_type, 'all_current': all_current,
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda group_shortname=None, role_id=None,
      all_current=None: str(get_object_or_404(GroupRole, pk=role_id)), 
      'groupes_regionaux/base.html', _('Do you really want to remove the role\
 of this person (you can end a role by setting its end date)'))
@login_required
def delete_role(request, group_shortname=None, role_id=None, all_current=None):
    """delete a role to a regional group"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access

    return ain7_generic_delete(request,
        get_object_or_404(GroupRole, pk=role_id),
        reverse(edit_roles, args=[group_shortname, all_current]),
        _('Role successfully deleted.'))

@login_required
def change_dates(request, group_shortname=None, role_id=None, all_current=None):
    """change dates for a regional group membership"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access

    group = get_object_or_404(Group, shortname=group_shortname)
    is_member = request.user.is_authenticated()\
                and group.has_for_member(request.user.person)
    role = get_object_or_404(GroupRole, pk=role_id)
    roles_by_type = build_roles_by_type(
        request, group, all_current, None, None, role,
        ChangeDatesForm(initial={'start_date': role.start_date,
                                 'end_date': role.end_date}))

    if request.method == 'POST':
        form = ChangeDatesForm(request.POST)
        if form.is_valid():
            form.save(role)
            return HttpResponseRedirect(reverse(edit_roles,
                args=[group.shortname, all_current]))
        else:
            request.user.message_set.create(message=_('Something was wrong in\
 the form you filled. No modification done.'))
            roles_by_type = build_roles_by_type(
                request, group, all_current, None, None, role, form)
    return ain7_render_to_response(request,
        'groupes_regionaux/edit_roles.html',
        {'group': group, 'is_member': is_member,
         'roles_by_type': roles_by_type, 'all_current': all_current,
         'back': request.META.get('HTTP_REFERER', '/')})

