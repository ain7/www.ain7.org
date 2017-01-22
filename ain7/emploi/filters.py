# -*- coding: utf-8
"""
 ain7/emploi/filers.py
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

from django.utils.translation import ugettext as _
import django_filters

from ain7.emploi.models import JobOffer


class JobOfferFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        name='title', label=_('title').capitalize(),
        lookup_expr='icontains',
    )

    description = django_filters.CharFilter(
        name='description', label=_('description').capitalize(),
        lookup_expr='icontains',
    )

    contract_type = django_filters.TypedChoiceFilter(
        name='contract_type', label=_('contract_type').capitalize(),
        lookup_expr='icontains', choices=JobOffer.JOB_TYPES,
    )

    class Meta:
        model = JobOffer
        fields = []
