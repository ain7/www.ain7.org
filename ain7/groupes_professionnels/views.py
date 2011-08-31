# -*- coding: utf-8
"""
 ain7/groupes_professionnels/views.py
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

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person
from ain7.decorators import access_required, confirmation_required
from ain7.groups.models import Group, Member, GroupHead, GroupLeader
from ain7.groupes_professionnels.forms import SubscribeGroupProForm, GroupProForm,\
                                              UnsubscribeGroupProForm, RoleForm
from ain7.pages.models import Text
from ain7.utils import ain7_generic_delete, check_access


def index(request):
    """index page"""
    text = Text.objects.get(textblock__shortname='groupes_professionnels')
    groups = Group.objects.get_by_type("ain7-professionnel")
    return render(request, 'groupes_professionnels/index.html',
                    {'groups': groups, 'text': text})

def details(request, slug):
    """group details"""
    group = get_object_or_404(Group, slug=slug, type__name="ain7-professionnel")
    return render(request, 
        'groupes_professionnels/details.html', {'group': group})

@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def subscribe(request, slug):
    """subscribe to a group"""

    group = get_object_or_404(Group, slug=slug, type__name="ain7-professionnel")
    form =  SubscribeGroupProForm()

    if request.method == 'POST':
        form = SubscribeGroupProForm(request.POST)
        if form.is_valid():
            person = Person.objects.get(id=form.cleaned_data['member'])
            if not group.has_for_member(person):
                membership = form.save(group=group)
                request.user.message_set.create(
                    message=_('You have successfully subscribed')+
                    ' '+person.first_name+' '+person.last_name+' '+
                    _('to this group.'))
                return HttpResponseRedirect(reverse(details, args=[group.slug]))
            else:
                request.user.message_set.create(
                message=_('This person is already subscribed to this group.'))
                return HttpResponseRedirect(reverse(details, args=[group.slug]))

    back = request.META.get('HTTP_REFERER', '/')
    return render(request, 
         'groupes_professionnels/subscribe.html',
        {'group': group, 'form': form, 'back': back,
         'group_list': Group.objects.all()})

@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def unsubscribe(request, slug):
    """unsubscribe from a group"""

    group = get_object_or_404(Group, slug=slug, type__name="ain7-professionnel")

    if request.method == 'POST':
        form = UnsubscribeGroupProForm(request.POST)
        if form.is_valid():
            person = form.cleaned_data['member']
            if group.has_for_member(person):
                form.unsubscribe(group)
                request.user.message_set.create(
                    message=_('Subscription successfully removed.'))
            else:
                request.user.message_set.create(
                    message=_('This person is not a member of this group.\
 Nothing done.'))
        else:
            request.user.message_set.create(
                message=_('Something was wrong in the form you filled. No\
 modification done.'))
        return HttpResponseRedirect(reverse(details, args=[group.slug]))

    form =  UnsubscribeGroupProForm()
    back = request.META.get('HTTP_REFERER', '/')
    return render(
        request, 'groupes_professionnels/subscribe.html',
        {'group': group, 'form': form, 'back': back,
         'group_list': Group.objects.all()})

@access_required(groups=['ain7-ca', 'ain7-secretariat', 'ain7-contributeur'])
def edit(request, slug):
    """edit group informations"""

    group = Group.objects.get(slug=slug, type__name="ain7-professionnel")
    form = GroupProForm(instance=group)

    if request.method == 'POST':
        form = GroupProForm(request.POST, instance=group)
        if form.is_valid():
            form.save(user=request.user)
            request.user.message_set.create(
                message=_("Modifications have been successfully saved."))
            return HttpResponseRedirect(reverse(details, args=[group.slug]))

    back = request.META.get('HTTP_REFERER', '/')
    return render(request, 'groupes_professionnels/edit.html',
        {'form': form, 'group': group, 'back': back})

@access_required(groups=['ain7-secretariat'])
def edit_role(request, slug, role_id=None):
    """edit group roles"""

    group = get_object_or_404(Group, slug=slug, type__name="ain7-professionnel")

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

    return render(request,
        'groupes_professionnels/roles_edit.html',
        {'group': group, 'is_member': is_member, 'form': form,
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda slug=None, role_id=None:
      str(get_object_or_404(GroupLeader, pk=role_id)),
      'groupes_professionnels/base.html', 
      _('Do you really want to remove the role of this person (you can end a\
 role by setting its end date)'))
@access_required(groups=['ain7-secretariat'])
def delete_role(request, slug=None, role_id=None):
    """delete role"""

    return ain7_generic_delete(request,
        get_object_or_404(GroupLeader, pk=role_id),
        reverse(details, args=[slug]),
        _('Role successfully deleted.'))

