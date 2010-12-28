# -*- coding: utf-8
"""
 ain7/groupes_regionaux/views.py
"""
#
#   Copyright © 2007-2011 AIn7 Devel Team
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
from ain7.groups.models import Group, Member, GroupRole, GroupLeader, GroupHead
from ain7.groupes_regionaux.forms import GroupForm, RoleForm
from ain7.pages.models import Text
from ain7.utils import ain7_render_to_response
from ain7.utils import ain7_generic_delete, check_access


def index(request):
    """index page"""
    text = Text.objects.get(textblock__shortname='groupes_regionaux')
    groups = Group.objects.get_by_type("ain7-regional")
    return ain7_render_to_response(request, 'groupes_regionaux/index.html',
                            {'groups': groups, 'text': text})

def details(request, slug):
    """regional group details"""
    group = get_object_or_404(Group, slug=slug, type__name="ain7-regional")
    is_member = request.user.is_authenticated()\
                and group.has_for_member(request.user.person)

    return ain7_render_to_response(request, 'groupes_regionaux/details.html',
                            {'group': group, 'is_member': is_member})

@login_required
def edit(request, slug):
    """edit regional group"""

    access = check_access(request, request.user, ['ain7-ca', 'ain7-secretariat',
        'ain7-contributeur'])
    if access:
        return access

    group = get_object_or_404(Group, slug=slug, type__name="ain7-regional")
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
                args=[group.slug]))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 'groupes_regionaux/edit.html', 
         {'form': form, 'group': group, 'back': back, 'is_member': is_member})

@login_required
def join(request, slug):
    """join regional group"""

    group = get_object_or_404(Group, slug=slug, type__name="ain7-regional")
    person = request.user.person

    access = check_access(request, request.user, ['ain7-membre'])
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

@confirmation_required(lambda slug: 
    str(get_object_or_404(Group, slug=slug)),
    'groupes_regionaux/base.html', _('Do you really want to quit the group'))
@login_required
def quit(request, slug):
    """leave regional group"""

    group = get_object_or_404(Group, slug=slug, type__name="ain7-regional")
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
def edit_role(request, slug, role_id=None):
    """edit regional group"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access

    group = get_object_or_404(Group, slug=slug, type__name="ain7-regional")

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
        'groupes_regionaux/roles_edit.html',
        {'group': group, 'is_member': is_member, 'form': form,
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda slug=None, role_id=None:
      str(get_object_or_404(GroupLeader, pk=role_id)), 
      'groupes_regionaux/base.html', _('Do you really want to remove the role\
 of this person (you can end a role by setting its end date)'))
@login_required
def delete_role(request, slug=None, role_id=None):
    """delete a role to a regional group"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access

    return ain7_generic_delete(request,
        get_object_or_404(GroupLeader, pk=role_id),
        reverse(details, args=[slug]),
        _('Role successfully deleted.'))

