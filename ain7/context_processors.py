# -*- coding: utf-8
"""
 ain7/context_processors.py
"""
#
#   Copyright © 2007-2017 AIn7 Devel Team
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

from django.conf import settings


def piwik(request):
    return {
        'piwik_url': settings.PIWIK_URL,
        'piwik_site_id': settings.PIWIK_SITE_ID,
    }

def user_groups(request):

    from ain7.annuaire.models import Person

    user_groups = []

    if request.user.is_authenticated() and Person.objects.filter(user=request.user):
        user_groups = request.user.person.groups.values_list('group__name', flat=True)

    return { 
        'superadmin': settings.PORTAL_ADMIN in user_groups,
        'ca_member': 'ain7-ca' in user_groups,
        'secretariat_member': 'ain7-secretariat' in user_groups,
        'contributeur': 'ain7-contributeur' in user_groups,
    }

