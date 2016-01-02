# -*- coding: utf-8
"""
 ain7/groups/views.py
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

import autocomplete_light
import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person
from ain7.decorators import access_required, confirmation_required
from ain7.groups.models import Group, Member, GroupLeader, GroupHead
from ain7.utils import ain7_generic_delete


def index(request):
    """index page"""
    groups = Group.objects.active()
    return render(request, 'groups/index.html', {
        'groups': groups
        }
    )


def details(request, slug):
    """group details"""
    group = get_object_or_404(Group, slug=slug)
    is_member = (request.user.is_authenticated()
        and group.has_for_member(request.user.person)
    )

    return render(request, 'groups/details.html', {
        'group': group,
        'is_member': is_member
        }
    )


@access_required(groups=['ain7-ca', 'ain7-secretariat', 'ain7-contributeur'])
def edit(request, slug=None):
    """edit group"""

    is_member = False
    group = None

    if slug:
        group = get_object_or_404(Group, slug=slug)
        is_member = request.user.is_authenticated()\
                and group.has_for_member(request.user.person)

    GroupForm = modelform_factory(Group)
    form = GroupForm(request.POST or None, instance=group)

    if request.method == 'POST' and form.is_valid():
        group = form.save()
        messages.success(
            request,
            _("Modifications have been successfully saved.")
        )
        return redirect('group-details', group.slug)

    return render(request, 'groups/edit.html', {
        'form': form,
        'group': group,
        'back': request.META.get('HTTP_REFERER', '/'),
        'is_member': is_member,
        }
    )


@access_required(groups=['ain7-admin'])
def join(request, slug):
    """join group"""

    group = get_object_or_404(Group, slug=slug)
    person = request.user.person

    if not group.has_for_member(person):
        grp_membership = Member()
        grp_membership.group = group
        grp_membership.member = person
        grp_membership.save()
        messages.success(
            request,
            _("You have been successfully added to this group.")
        )
    else:
        messages.info(request, _("You are already a member of this group."))

    return redirect('group-details', group.slug)


@login_required
def members(request, slug):
    """group members"""
    group = get_object_or_404(Group, slug=slug)
    members = Person.objects.filter(groups__group=group) #, end_date__gte=datetime.date.today(), expiration_date__gte=datetime.date.today())

    is_member = request.user.is_authenticated()\
        and group.has_for_member(request.user.person)

    return render(request, 'groups/members.html', {
        'group': group,
        'is_member': is_member,
        'members': members,
        }
    )


@access_required(groups=['ain7-admin'])
def member_edit(request, slug, member_id=None):
    """add a new member to the role"""

    group = get_object_or_404(Group, slug=slug)

    member = None
    if member_id:
        member = get_object_or_404(Member, pk=member_id)

    MemberForm = autocomplete_light.modelform_factory(
        Member,
        exclude=('group', 'start_date', 'end_date', 'expiration_date',),
    )
    form = MemberForm(request.POST or None, instance=member)

    if request.method == 'POST' and form.is_valid():
        member = form.save(commit=False)
        member.group = group
        member.save()
        messages.success(request, _('User added to group'))
        return redirect('group-details', group.slug)

    return render(request, 'groups/edit.html', {
        'form': form,
        'group': group,
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@access_required(groups=['ain7-admin'])
def member_delete(request, slug, member_id):
    """delete member role"""

    group = get_object_or_404(Group, slug=slug)
    member = get_object_or_404(Member, pk=member_id)

    member.end_date = datetime.date.today()

    messages.success(request, _('Member removed from role'))

    return redirect('group-details', group.slug)


@confirmation_required(lambda slug:
    str(get_object_or_404(Group, slug=slug)),
    'groups/base.html', _('Do you really want to quit the group'))
@access_required(groups=['ain7-membre'])
def quit(request, slug):
    """leave group"""

    group = get_object_or_404(Group, slug=slug)
    person = request.user.person

    if group.has_for_member(person):
        if group.has_for_board_member(person):
            messages.info(
                request,
                _("You are a member of the office of this group. You have to \
unsubscribe from every role in your group before leaving it."))
        else:
            membership = Member.objects\
                .filter(
                    group=group, member=person
                ).exclude(
                    end_date__isnull=False,
                    end_date__lte=datetime.datetime.now()
                ).latest('end_date')
            membership.end_date = datetime.datetime.now()
            membership.save()
            messages.success(
                request,
                _('You have been successfully removed from this group.')
            )
    else:
        messages.info(request, _("You are not a member of this group."))

    return redirect('group-details', group.slug)


@access_required(groups=['ain7-secretariat'])
def role_edit(request, slug, role_id=None):
    """edit group head"""

    group = get_object_or_404(Group, slug=slug)

    is_member = request.user.is_authenticated()\
        and group.has_for_member(request.user.person)

    role = None
    if role_id:
        role = get_object_or_404(GroupLeader, id=role_id)

    RoleForm = autocomplete_light.modelform_factory(
        GroupLeader,
        exclude=('grouphead',)
    )
    form = RoleForm(request.POST or None, instance=role)

    if request.method == 'POST' and form.is_valid():
        role = form.save(commit=False)
        role.grouphead = GroupHead.objects.get(group__slug=group.slug)
        role.save()
        return redirect('group-details', group.slug)

    return render(request, 'groups/edit.html', {
        'group': group,
        'is_member': is_member,
        'form': form,
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@confirmation_required(lambda slug=None, role_id=None:
      str(get_object_or_404(GroupLeader, pk=role_id)), 
      'groups/base.html', _('Do you really want to remove the role\
 of this person (you can end a role by setting its end date)'))
@access_required(groups=['ain7-secretariat'])
def role_delete(request, slug=None, role_id=None):
    """delete a role to a regional group"""

    return ain7_generic_delete(request,
        get_object_or_404(GroupLeader, pk=role_id),
        reverse(details, args=[slug]),
        _('Role successfully deleted.'))
