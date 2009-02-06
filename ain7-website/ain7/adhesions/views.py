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
from django.core.paginator import Paginator, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from ain7.adhesions.models import *
from ain7.adhesions.forms import *
from ain7.annuaire.models import Person
from ain7.decorators import confirmation_required
from ain7.utils import ain7_render_to_response, ain7_generic_edit, ain7_generic_delete, check_access
from ain7.annuaire.models import AIn7Member

def index(request):
    return ain7_render_to_response(request, 'adhesions/index.html',
        {'subscriptions_list': Subscription.objects.filter(validated=True).order_by('-last_change_at')[:10],
         'count_members': AIn7Member.objects.count(),
         'count_subscribers': Subscription.objects.filter(year=datetime.date.today().year, validated=True).count()})

@login_required
def subscriptions(request):
    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    nb_results_by_page = 5
    subscriptions_list = Subscription.objects.order_by('validated')

    filter = False
    if request.GET.has_key('filter'):
        filter = True
        subscriptions_list = subscriptions_list.filter(validated=False)
    paginator = Paginator(subscriptions_list,nb_results_by_page)

    try:
        page = int(request.GET.get('page', '1'))
        subscriptions_list = paginator.page(page).object_list
    except PageNotAnInteger:
        raise Http404

    return ain7_render_to_response(request, 'adhesions/subscriptions.html',
        {'subscriptions_list': subscriptions_list, 'request': request,
         'paginator': paginator, 'is_paginated': paginator.num_pages > 1,
         'has_next': paginator.page(page).has_next(),
         'has_previous': paginator.page(page).has_previous(),
         'current_page': page, 'pages': paginator.num_pages,
         'next_page': page + 1, 'previous_page': page - 1,
         'first_result': (page-1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.count),
         'hits': paginator.count, 'filter': filter})

@confirmation_required(lambda user_id=None, subscription_id=None : str(get_object_or_404(Subscription, pk=subscription_id)), 'adhesions/base.html', _('Do you really want to validate this subscription'))
@login_required
def subscription_validate(request, subscription_id=None):
    r = check_access(request, request.user, ['ain7-secretariat'])
    if r and unicode(request.user.id) != user_id:
        return r

    subscription = get_object_or_404(Subscription, pk=subscription_id)
    subscription.validated=True
    subscription.logged_save(request.user.person)

    request.user.message_set.create(message=_('Subscription successfully validated.'))
    return HttpResponseRedirect(reverse(subscriptions))

@confirmation_required(lambda user_id=None, subscription_id=None : str(get_object_or_404(Subscription, pk=subscription_id)), 'adhesions/base.html', _('Do you really want to delete this subscription'))
@login_required
def subscription_delete(request, subscription_id=None):
    r = check_access(request, request.user, ['ain7-secretariat'])
    if r:
        return r

    return ain7_generic_delete(request,
        get_object_or_404(Subscription, pk=subscription_id),
        reverse(subscriptions),
        _('Subscription successfully deleted.'))

@login_required
def user_subscriptions(request, user_id):
    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    p = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=p)

    subscriptions_list = Subscription.objects.filter(member=ain7member).order_by('-year')

    return ain7_render_to_response(request, 'adhesions/user_subscriptions.html',
                            {'person': p, 'ain7member': ain7member, 'subscriptions_list': subscriptions_list})

@login_required
def subscription_add(request, user_id=None):
    r = check_access(request, request.user, ['ain7-secretariat'])
    if r and unicode(request.user.id) != user_id:
        return r


    # TODO: utiliser un formulaire spécifique et une gestion spécifique
    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    if Subscription.objects.filter(member=ain7member,year=datetime.datetime.now().year):
        request.user.message_set.create(message=_('You already subscribe this year.'))

    subscription = None
    title = _('Adding a subscription for')
    msgDone = _('Subscription successfully added.')
    return ain7_generic_edit(
        request, subscription, SubscriptionForm,
        {'member': ain7member}, 'adhesions/edit_form.html',
        {'action_title': title, 'person': person,
         'back': request.META.get('HTTP_REFERER', '/')}, {},
        reverse(user_subscriptions, kwargs={'user_id': user_id}), msgDone)
