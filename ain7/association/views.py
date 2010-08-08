# -*- coding: utf-8
"""
 ain7/association/views.py
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

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from ain7.annuaire.models import AIn7Member
from ain7.association.forms import CouncilRoleForm
from ain7.decorators import confirmation_required
from ain7.groups.models import Group, GroupHead, GroupLeader
from ain7.pages.models import Text
from ain7.utils import ain7_render_to_response, ain7_generic_delete
from ain7.utils import check_access


def count_members():
    """count all members of the association"""
    nb_members = AIn7Member.objects.all().count()
    return nb_members

def index(request):
    """index page"""
    text = Text.objects.get(textblock__shortname='presentation_ain7') 
    return ain7_render_to_response(request, 'association/index.html', 
                {'count_members': count_members(), 'text': text}) 
 
def status(request):
    """status page""" 
    text = Text.objects.get(textblock__shortname='statuts_ain7') 
    return ain7_render_to_response(request, 'association/status.html', 
                {'count_members': count_members(), 'text': text}) 

def internalrules(request):
    """internal rules page""" 
    text = Text.objects.get(textblock__shortname='internal_rules_ain7') 
    return ain7_render_to_response(request, 'association/internalrules.html', 
                {'count_members': count_members(), 'text': text}) 
 
def council(request):
    """council presentation page"""
    from ain7.groups.models import Group
    ca = get_object_or_404(Group, slug='ain7')
    return ain7_render_to_response(request, 'association/council.html',
        {'group': ca, 'count_members': count_members()})
 
def contact(request):
    """contact page"""
    text = Text.objects.get(textblock__shortname='contact_ain7') 
    return ain7_render_to_response(request, 'association/contact.html', 
          {'count_members': count_members(), 'text': text}) 

def activites(request):
    """activities page"""
    text = Text.objects.get(textblock__shortname='activites_ain7') 
    return ain7_render_to_response(request, 'association/activites.html', 
          {'count_members': count_members(), 'text': text}) 

@login_required
def edit_council_role(request, role_id=None):
    """edit council role"""

    access = check_access(request, request.user,
        ['ain7-secretariat'])
    if access:
        return access

    form = CouncilRoleForm()

    if role_id:
        group_role = get_object_or_404(GroupLeader, id=role_id)
        form = CouncilRoleForm(instance=group_role)
    
    if request.method == 'POST':
        if role_id:
            form = CouncilRoleForm(request.POST, instance=group_role)
        else:
            form = CouncilRoleForm(request.POST)
        if form.is_valid():
            council_role = form.save(commit=False)
            council_role.grouphead = GroupHead.objects.get(group__slug='ain7')
            council_role.save()
            return HttpResponseRedirect(reverse(council))

        else:
            request.user.message_set.create(message=_('Something was wrong in\
 the form you filled. No modification done.'))
            # TODO : le champ username n'est pas renseigné ici (LP 346274)

    return ain7_render_to_response(request,
        'association/council_edit.html',
        {'count_members': count_members(), 'form': form,
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda role_id=None, all_current=None:
     str(get_object_or_404(GroupLeader, pk=role_id)), 'association/base.html',
     _('Do you really want to remove the role of this person (you can end a\
 role by setting its end date)'))
@login_required
def delete_council_role(request, role_id):
    """delete council role"""

    access = check_access(request, request.user,
        ['ain7-secretariat'])
    if access:
        return access

    return ain7_generic_delete(request,
        get_object_or_404(GroupLeader, pk=role_id),
        reverse(council),
        _('Role successfully deleted.'))

def media_com(request):
    """media communication index page"""
    text = Text.objects.get(textblock__shortname='publication_ain7')
    return ain7_render_to_response(request, 
            'media_communication/index.html', {'text': text})

def canal_n7(request):
    """Canal N7 page"""
    text1 = Text.objects.get(textblock__shortname='presentation_canal_n7')
    text2 = Text.objects.get(textblock__shortname='redaction_canal_n7')
    text3 = Text.objects.get(textblock__shortname='canal_n7')
    text4 = Text.objects.get(textblock__shortname='sommaire_canal_n7')
    return ain7_render_to_response(request, 'media_communication/canal_n7.html',
                  {'text1': text1, 'text2': text2, 'text3': text3, 'text4': text4})

def canal_n7_edito(request): 
    """Canal N7 edito"""
    text1 = Text.objects.get(textblock__shortname='edito_canal_n7')
    text2 = Text.objects.get(textblock__shortname='sommaire_canal_n7')
    return ain7_render_to_response(request, 
                      'media_communication/canal_n7_edito.html', 
                     {'text1': text1, 'text2': text2})

