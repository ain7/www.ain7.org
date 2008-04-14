# -*- coding: utf-8
#
# groupes/views.py
#
#   Copyright (C) 2007-2008 AIn7
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

from datetime import datetime

from django.http import HttpResponse
from django.template import Context, loader, RequestContext
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django import newforms as forms
from django.newforms import widgets
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from ain7.groupes.models import Group, Membership
from ain7.utils import ain7_render_to_response, form_callback
from ain7.annuaire.models import Person

class SubscribeGroupForm(forms.Form):
    member = forms.IntegerField(label=_('Person to subscribe'))
    is_coordinator = forms.BooleanField(label=_('Is coordinator'))

    def __init__(self, *args, **kwargs):
        personList = []
        for person in Person.objects.all():
            personList.append( (person.user.id, str(person)) )
        self.base_fields['member'].widget = \
            forms.Select(choices=personList)
        super(SubscribeGroupForm, self).__init__(*args, **kwargs)

def index(request):
    groups = Group.objects.all().order_by('name')
    return ain7_render_to_response(request, 'groupes/index.html', {'groups': groups})

def detail(request, group_id):
    g = get_object_or_404(Group, pk=group_id)
    memberships = g.memberships
    return ain7_render_to_response(request, 'groupes/details.html', {'group': g, 'memberships': memberships})

@login_required
def subscribe(request, group_id):

    group = get_object_or_404(Group, pk=group_id)

    if request.method == 'POST':
        f = SubscribeGroupForm(request.POST)
        person = Person.objects.get(user__id=request.POST['member'])
        # on vérifie que la personne n'est pas déjà inscrite
        already_subscribed = False
        for subscription in person.group_memberships.all():
            if subscription.group == group:
                already_subscribed = True
        if already_subscribed:
            request.user.message_set.create(message=_('This person is already subscribed to this group.'))
            memberships = group.memberships
            return ain7_render_to_response(request, 'groupes/details.html',
                                           {'group': group, 'memberships': memberships})
        if f.is_valid():
            membership = Membership()
            membership.member = Person.objects.get(user__id=request.POST['member'])
            membership.group = group
            membership.is_coordinator = f.cleaned_data['is_coordinator']
            membership.save()

            p = membership.member

            request.user.message_set.create(message=_('You have successfully subscribed')+
                                            ' '+p.first_name+' '+p.last_name+' '+_('to this event.'))
        return HttpResponseRedirect('/groupes/%s/' % (group.id))

    f =  SubscribeGroupForm()
    next_groups = Group.objects.filter(end__gte=datetime.now())

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 'groupes/subscribe.html',
                                   {'group': group, 'form': f, 'back': back,
                                    'group_list': Group.objects.all(),
                                    'next_groups': next_groups})
@login_required
def edit(request, group_id=None):

    if group_id is None:
        GroupForm = forms.models.form_for_model(Group, formfield_callback=form_callback)
        GroupForm.base_fields['web_page'].widget = forms.widgets.Textarea(attrs={'rows':10, 'cols':90})
        form = GroupForm()

    else:
        group = Group.objects.get(id=group_id)
        GroupForm = forms.models.form_for_instance(group, formfield_callback=form_callback)
        GroupForm.base_fields['web_page'].widget = forms.widgets.Textarea(attrs={'rows':10, 'cols':90})
        form = GroupForm()

        if request.method == 'POST':
             form = GroupForm(request.POST)
             if form.is_valid():
                 form.save()

                 request.user.message_set.create(message=_("Modifications have been successfully saved."))

                 return HttpResponseRedirect('/groupes/%s/' % (group.id))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 'groupes/edit.html', {'form': form, 'group': group, 'back': back})

