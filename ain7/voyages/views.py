# -*- coding: utf-8
"""
 ain7/voyages/views.py
"""
#
#   Copyright © 2007-2018 AIn7
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

from django.contrib import messages
from django.forms.models import modelform_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _

from ain7.decorators import access_required, confirmation_required
from ain7.pages.models import Text
from ain7.utils import ain7_generic_delete
from ain7.voyages.filters import TravelFilter
from ain7.voyages.models import Travel


def index(request):
    """index"""

    travels = TravelFilter(request.GET, queryset=Travel.objects.all())
    text = Text.objects.get(textblock__shortname='voyages')

    return render(request, 'voyages/index.html', {
        'travels': travels,
        'text': text,
        }
    )


@confirmation_required(
    lambda user_id = None,
    travel_id = None: str(get_object_or_404(Travel, pk=travel_id)),
    'voyages/base.html',
    _('Do you REALLY want to delete this travel'))
@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def delete(request, travel_id):
    """delete travel"""

    return ain7_generic_delete(request,
        get_object_or_404(Travel, pk=travel_id),
        '/voyages/', _('Travel successfully deleted.'))


def details(request, travel_id):
    """travel details"""
    travel = get_object_or_404(Travel, pk=travel_id)
    return render(request, 'voyages/details.html', {
        'travel': travel,
        }
    )


@access_required(groups=['ain7-ca', 'ain7-secretariat'])
def edit(request, travel_id=None):
    """edit travel"""

    travel = None
    if travel_id:
        travel = Travel.objects.get(pk=travel_id)

    TravelForm = modelform_factory(Travel, exclude=())
    form = TravelForm(
        request.POST or None,
        request.FILES or None,
        instance=travel,
    )

    if request.method == 'POST' and form.is_valid():
        travel = form.save()
        messages.success(
            request,
            _('Modifications have been successfully saved.')
        )

        return redirect(travel)

    return render(request, 'voyages/edit.html', {
        'form': form,
        'action_title': _("Modification of personal data for"),
        'back': request.META.get('HTTP_REFERER', '/'),
        'travel': travel,
        }
    )
