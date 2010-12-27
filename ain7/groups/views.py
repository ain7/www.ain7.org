# -*- coding: utf-8
"""
 ain7/groups/views.py
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

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person
from ain7.decorators import confirmation_required
from ain7.groups.forms import GroupForm, MemberForm, RoleForm
from ain7.groups.models import Group, Member, GroupRole, GroupLeader, GroupHead
from ain7.utils import ain7_render_to_response
from ain7.utils import ain7_generic_delete, check_access


def index(request):
    """index page"""
    groups_regional = Group.objects.get_by_type("ain7-regional")
    groups_pro = Group.objects.get_by_type("ain7-professionnel")
    return ain7_render_to_response(request, 'groups/index.html',
        {'groups_regional': groups_regional, 'groups_pro': groups_pro})

def details(request, slug):
    """group details"""
    group = get_object_or_404(Group, slug=slug)
    is_member = request.user.is_authenticated()\
                and group.has_for_member(request.user.person)

    return ain7_render_to_response(request, 'groups/details.html',
                            {'group': group, 'is_member': is_member})

@login_required
def edit(request, slug=None):
    """edit group"""

    access = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat',
        'ain7-contributeur'])
    if access:
        return access

    if slug:
        group = get_object_or_404(Group, slug=slug)
        is_member = request.user.is_authenticated()\
                and group.has_for_member(request.user.person)

        form = GroupForm(instance=group)
    else:
        form = GroupForm()
        is_member = False
        group = None

    if request.method == 'POST':
        if slug:
             form = GroupForm(request.POST, instance=group)
        else:
             form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            request.user.message_set.create(
                message=_("Modifications have been successfully saved."))
            return HttpResponseRedirect(reverse(details,
                args=[group.slug]))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 'groups/edit.html', 
         {'form': form, 'group': group, 'back': back, 'is_member': is_member})

@login_required
def join(request, slug):
    """join group"""

    group = get_object_or_404(Group, slug=slug)
    person = request.user.person

    access = check_access(request, request.user, ['ain7-admin'])
    if access:
        return access

    if not group.has_for_member(person):
        grp_membership = Member()
        grp_membership.group = group
        grp_membership.member = person
        grp_membership.save()
        request.user.message_set.create(message=
            _("You have been successfully added to this group."))
    else:
        request.user.message_set.create(message=
            _("You are already a member of this group."))

    return HttpResponseRedirect(reverse(details, args=[group.slug]))

def members(request, slug):
    """group members"""
    group = get_object_or_404(Group, slug=slug)
    members = Person.objects.filter(groups__group=group) #, end_date__gte=datetime.date.today(), expiration_date__gte=datetime.date.today())

    is_member = request.user.is_authenticated()\
                and group.has_for_member(request.user.person)

    return ain7_render_to_response(request, 'groups/members.html',
        {'group': group, 'is_member': is_member, 'members': members, 'is_paginated': False})

@login_required
def member_edit(request, slug, member_id=None):
    """add a new member to the role"""

    access = check_access(request, request.user, ['ain7-admin'])
    if access:
        return access

    group = get_object_or_404(Group, slug=slug)
    member = None
    form = MemberForm()

    if member_id:
        member = get_object_or_404(Member, pk=member_id)
        form = MemberForm(instance=member)

    if request.method == 'POST':
        if member_id:
            form = MemberForm(request.POST, instance=member)
        else:
            form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.group = group
            member.save()
            request.user.message_set.create(message=_('User added to group'))
            return HttpResponseRedirect('/groups/%s/' % group.slug)
        else:
            request.user.message_set.create(message=_('User is not correct'))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request, 'groups/edit.html',
        {'form': form, 'group': group, 'back': back})


@login_required
def member_delete(request, slug, member_id):
    """delete member role"""

    access = check_access(request, request.user, ['ain7-admin'])
    if access:
        return access

    group = get_object_or_404(Group, slug=role_id)
    member = get_object_or_404(Member, pk=member_id)

    member.end_date = datetime.date.today()

    request.user.message_set.create(message=_('Member removed from role'))

    return HttpResponseRedirect('/groups/%s/' % group.slug)


@confirmation_required(lambda slug: 
    str(get_object_or_404(Group, slug=slug)),
    'groups/base.html', _('Do you really want to quit the group'))
@login_required
def quit(request, slug):
    """leave group"""

    group = get_object_or_404(Group, slug=slug)
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
            membership = Member.objects\
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

    return HttpResponseRedirect(reverse(details, args=[group.slug]))


@login_required
def role_edit(request, slug, role_id=None):
    """edit group head"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access

    group = get_object_or_404(Group, slug=slug)

    is_member = request.user.is_authenticated()\
                and group.has_for_member(request.user.person)

    form = RoleForm()

    if role_id:
        role = get_object_or_404(GroupLeader, id=role_id)
        form = RoleForm(instance=role)

    if request.method == 'POST':
        if role_id:
            form = RoleForm(request.POST, instance=role)
        else:
            form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save(commit=False)
            role.grouphead = GroupHead.objects.get(group__slug=group.slug)
            role.save()
            return HttpResponseRedirect(reverse(details, args=[group.slug]))

        else:
            request.user.message_set.create(message=_('Something was wrong in\
 the form you filled. No modification done.'))


    return ain7_render_to_response(request,
        'groups/edit.html',
        {'group': group, 'is_member': is_member, 'form': form,
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda slug=None, role_id=None:
      str(get_object_or_404(GroupLeader, pk=role_id)), 
      'groups/base.html', _('Do you really want to remove the role\
 of this person (you can end a role by setting its end date)'))
@login_required
def role_delete(request, slug=None, role_id=None):
    """delete a role to a regional group"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access

    return ain7_generic_delete(request,
        get_object_or_404(GroupLeader, pk=role_id),
        reverse(details, args=[slug]),
        _('Role successfully deleted.'))

