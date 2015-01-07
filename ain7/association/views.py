# -*- coding: utf-8
"""
 ain7/association/views.py
"""
#
#   Copyright © 2007-2015 AIn7 Devel Team
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

from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _

import autocomplete_light

from ain7.annuaire.models import AIn7Member
from ain7.decorators import access_required, confirmation_required
from ain7.groups.models import Group, GroupHead, GroupLeader
from ain7.pages.models import Text
from ain7.utils import ain7_generic_delete


def count_members():
    """count all members of the association"""
    nb_members = AIn7Member.objects.all().count()
    return nb_members


def index(request):
    """index page"""
    text = Text.objects.get(textblock__shortname='presentation_ain7')

    return render(request, 'association/index.html', {
        'count_members': count_members(),
        'text': text,
        }
    )


def status(request):
    """status page"""

    text = Text.objects.get(textblock__shortname='statuts_ain7')

    return render(request, 'association/status.html', {
        'count_members': count_members(),
        'text': text,
        }
    )


def internalrules(request):
    """internal rules page"""
    text = Text.objects.get(textblock__shortname='internal_rules_ain7')

    return render(request, 'association/internalrules.html', {
        'count_members': count_members(),
        'text': text,
        }
    )


def council(request):
    """council presentation page"""

    ca = get_object_or_404(Group, slug='ain7')
    return render(request, 'association/council.html', {
        'group': ca,
        'count_members': count_members(),
        }
    )


def contact(request):
    """contact page"""
    text = Text.objects.get(textblock__shortname='contact_ain7')

    return render(request, 'association/contact.html', {
        'count_members': count_members(),
        'text': text,
        }
    )


@access_required(groups=['ain7-secretariat'])
def edit_council_role(request, role_id=None):
    """edit council role"""

    group_role = None
    if role_id:
        group_role = get_object_or_404(GroupLeader, id=role_id)

    CouncilRoleForm = autocomplete_light.modelform_factory(
        GroupLeader,
        exclude=('grouphead',)
    )
    form = CouncilRoleForm(request.POST or None, instance=group_role)

    if request.method == 'POST' and form.is_valid():
        council_role = form.save(commit=False)
        council_role.grouphead = GroupHead.objects.get(group__slug='ain7')
        council_role.save()
        return redirect('council-details')

    return render(request, 'association/council_edit.html', {
        'count_members': count_members(),
        'form': form,
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@confirmation_required(lambda role_id=None, all_current=None:
     str(get_object_or_404(GroupLeader, pk=role_id)), 'association/base.html',
     _('Do you really want to remove the role of this person (you can end a\
 role by setting its end date)'))
@access_required(groups=['ain7-secretariat'])
def delete_council_role(request, role_id):
    """delete council role"""

    return ain7_generic_delete(
        request,
        get_object_or_404(GroupLeader, pk=role_id),
        reverse(council),
        _('Role successfully deleted.')
    )
