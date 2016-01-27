# -*- coding: utf-8
"""
 ain7/annuaire/filers.py
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

import django_filters

from django.db.models import Q
from django.utils.translation import ugettext as _

from ain7.annuaire.models import AIn7Member, Country, Track


class AIn7MemberFilter(django_filters.FilterSet):

    last_name = django_filters.MethodFilter(
        name='person__last_name', label=_('last name').capitalize(),
        lookup_type='icontains', action='filter_last_name',
    )
    first_name = django_filters.CharFilter(
        name='person__first_name', label=_('first name').capitalize(),
        lookup_type='icontains',
    )
    year = django_filters.NumberFilter(
        name='promos__year__year', label=_('year').capitalize(),
        lookup_type='exact',
    )
    track = django_filters.ModelChoiceFilter(
        name='promos__track__name', label=_('track').capitalize(),
        lookup_type='icontains', queryset=Track.objects.all(),
    )
    organization = django_filters.CharFilter(
        name='positions__office__organization__name',
        label=_('organization').capitalize(), lookup_type='icontains',
        distinct=True,
    )
    city = django_filters.CharFilter(
        name='person__addresses__city', label=_('city').capitalize(),
        lookup_type='icontains',
    )
    country = django_filters.ModelChoiceFilter(
        name='person__addresses__country', label=_('country').capitalize(),
        queryset=Country.objects.all(),
        )

    class Meta:
        model = AIn7Member
        fields = {}

    def filter_last_name(self, queryset, value):
        return queryset.filter(
            Q(person__last_name__icontains=value) |
            Q(person__maiden_name__icontains=value)
        )


class AIn7MemberAdvancedFilter(django_filters.FilterSet):

    last_name = django_filters.MethodFilter(
        name='person__last_name', label=_('last name').capitalize(),
        lookup_type='icontains', action='filter_last_name',
    )
    first_name = django_filters.CharFilter(
        name='person__first_name', label=_('first name').capitalize(),
        lookup_type='icontains',
    )
    year = django_filters.NumberFilter(
        name='promos__year__year', label=_('year').capitalize(),
        lookup_type='exact',
    )
    track = django_filters.ModelChoiceFilter(
        name='promos__track__name', label=_('track').capitalize(),
        lookup_type='icontains', queryset=Track.objects.all(),
    )
    organization = django_filters.CharFilter(
        name='positions__office__organization__name',
        label=_('organization').capitalize(), lookup_type='icontains',
    )
    position = django_filters.CharFilter(
        name='positions__fonction',
        label=_('fonction').capitalize(), lookup_type='icontains',
    )
    zip_code = django_filters.CharFilter(
        name='person__addresses__zip_code', label=_('zip code').capitalize(),
        lookup_type='icontains',
    )
    city = django_filters.CharFilter(
        name='person__addresses__city', label=_('city').capitalize(),
        lookup_type='icontains',
    )
    country = django_filters.ModelChoiceFilter(
        name='person__addresses__country', label=_('country').capitalize(),
        queryset=Country.objects.all(),
        )


    class Meta:
        model = AIn7Member
        fields = {}

    def filter_last_name(self, queryset, value):
        return queryset.filter(
            Q(person__last_name__icontains=value) |
            Q(person__maiden_name__icontains=value)
        )
