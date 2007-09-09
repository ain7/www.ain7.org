# -*- coding: utf-8
#
# groupes/views.py
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

from django.http import HttpResponse
from django.template import Context, loader, RequestContext
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django import newforms as forms
from django.newforms import widgets
from django.http import HttpResponseRedirect

from ain7.groupes.models import Group
from ain7.utils import ain7_render_to_response

def index(request):
    groups = Group.objects.all().order_by('name')
    return ain7_render_to_response(request, 'groupes/index.html', {'groups': groups})

def detail(request, group_id):
    g = get_object_or_404(Group, pk=group_id)
    return ain7_render_to_response(request, 'groupes/details.html', {'group': g})

@login_required
def edit(request, group_id=None):

    if group_id is None:
        GroupForm = forms.models.form_for_model(Group)
        GroupForm.base_fields['web_page'].widget = forms.widgets.Textarea(attrs={'rows':10, 'cols':90})
        form = GroupForm()

    else:
        group = Group.objects.get(id=group_id)
        GroupForm = forms.models.form_for_instance(group)
        GroupForm.base_fields['web_page'].widget = forms.widgets.Textarea(attrs={'rows':10, 'cols':90})
        form = GroupForm()

        if request.method == 'POST':
             form = GroupForm(request.POST)
             if form.is_valid():
                 form.save()

                 request.user.message_set.create(message=_("Modifications have been successfully saved."))

                 return HttpResponseRedirect('/groupes/%s/' % (group.id))

    return ain7_render_to_response(request, 'groupes/edit.html', {'form': form, 'group': group})

