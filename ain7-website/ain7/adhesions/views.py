# -*- coding: utf-8
#
# adhesions/views.py
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

import datetime

from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from ain7.adhesions.models import *
from ain7.adhesions.forms import *
from ain7.annuaire.models import Person
from ain7.decorators import confirmation_required
from ain7.utils import ain7_render_to_response, ain7_generic_edit, ain7_generic_delete, check_access
from ain7.annuaire.models import AIn7Member

def index(request): 
    return ain7_render_to_response(request, 'adhesions/index.html',
        {'count_members': AIn7Member.objects.count(),
         'count_subscribers': Subscription.objects.filter(year=datetime.date.today().year).count()})

@login_required
def subscribe(request):
    r = check_access(request, request.user, ['ain7-member','ain7-secretariat'])
    if r:
        return r

    return ain7_render_to_response(request, 'adhesions/index.html',
        {'count_members': AIn7Member.objects.count(),})

@login_required
def subscriptions(request, user_id):

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    p = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)

    subscriptions_list = Subscription.objects.filter(member=ain7member).order_by('-year')

    return ain7_render_to_response(request, 'adhesions/subscriptions.html',
                            {'person': p, 'ain7member': ain7member, 'subscriptions_list': subscriptions_list})

@login_required
def subscription_edit(request, user_id=None, subscription_id=None):

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)
    subscription = None
    title = _('Adding a subscription for')
    msgDone = _('Subscription successfully added.')
    if subscription_id:
        subscription = get_object_or_404(Subscription, pk=subscription_id)
        title = _('Modification of a subscription for')
        msgDone = _('Subscription informations updated successfully.')
    return ain7_generic_edit(
        request, subscription, SubscriptionForm,
        {'member': ain7member}, 'adhesions/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        '/adhesions/%s/subscriptions/' % user_id, msgDone)

@confirmation_required(lambda user_id=None, subscription_id=None : str(get_object_or_404(Subscription, pk=subscription_id)), 'annuaire/base.html', _('Do you really want to delete this subscription'))
@login_required
def subscription_delete(request, user_id=None, subscription_id=None):

    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r

    return ain7_generic_delete(request,
        get_object_or_404(Subscription, pk=subscription_id),
        '/adhesions/%s/subscriptions/' % user_id,
        _('Subscription successfully deleted.'))
