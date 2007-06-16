# -*- coding: utf-8
#
# groupes_regionaux/views.py
#
#   Copyright (C) 2007 AIn7
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

from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django import newforms as forms
from django.newforms import widgets
from django.template import RequestContext
from django.http import HttpResponseRedirect

from ain7.groupes_regionaux.models import Group
from ain7.groupes_regionaux.models import GroupMembership
from ain7.decorators import confirmation_required

def index(request):
    groups = Group.objects.all().filter(is_active=True).order_by('name')
    return render_to_response('groupes_regionaux/index.html', 
                             {'groups': groups, 'user': request.user}, 
                             context_instance=RequestContext(request))

def details(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    is_member = request.user.is_authenticated()\
                and group.has_for_member(request.user.person)

    return render_to_response('groupes_regionaux/details.html', {'group': group,
                              'user': request.user, 'is_member': is_member}, 
                              context_instance=RequestContext(request))
def edit(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    is_member = request.user.is_authenticated()\
                and group.has_for_member(request.user.person)

    if request.method == 'POST':

        GroupForm = forms.models.form_for_instance(group)
        f = GroupForm(request.POST.copy())
        if f.is_valid():
            f.clean_data['group'] = group
            f.save()

        request.user.message_set.create(message=_("Regional group informations updated successfully."))

        return HttpResponseRedirect('/groupes_regionaux/%s/' % (group.id))

    GroupForm = forms.models.form_for_instance(group)
    f = GroupForm()

    return render_to_response('groupes_regionaux/edit.html', {'form': f, 
                              'group': group,'user': request.user, 'is_member': is_member}, 
                              context_instance=RequestContext(request))

@login_required
def join(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    person = request.user.person

    if not group.has_for_member(person):
        GroupMembership(type=7, group=group, member=person).save()
        request.user.message_set.create(message=_("You have been successfully added to this group."))
    else:
        request.user.message_set.create(message=_("You are already a member of this group."))

    return HttpResponseRedirect('/groupes_regionaux/%s/' % (group.id))

@confirmation_required(lambda group_id: str(get_object_or_404(Group, pk=group_id)), "groupes_regionaux/base.html", _("Do you really want to quit this group?"))
@login_required
def quit(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    person = request.user.person

    if group.has_for_member(person):
        membership = GroupMembership.objects.filter(group=group, member=person)\
                    .exclude(end_date__isnull=False, end_date__lte=datetime.datetime.now())\
                    .latest('end_date')
        membership.end_date = datetime.datetime.now()
        membership.save()
        request.user.message_set.create(message=_("You have been successfully removed from this group."))
    else:
        request.user.message_set.create(message=_("You are not a member of this group."))

    return HttpResponseRedirect('/groupes_regionaux/%s/' % (group.id))
