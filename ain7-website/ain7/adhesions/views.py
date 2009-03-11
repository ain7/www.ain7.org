# -*- coding: utf-8
#
# adhesions/views.py
#
#   Copyright © 2007-2009 AIn7 Devel Team
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

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from ain7.adhesions.forms import ConfigurationForm, SubscriptionForm
from ain7.adhesions.models import Subscription, SubscriptionConfiguration
from ain7.annuaire.models import AIn7Member, Person
from ain7.decorators import confirmation_required
from ain7.utils import ain7_render_to_response, ain7_generic_edit, ain7_generic_delete, check_access


def index(request):
    count_subscribers = Subscription.objects.filter(validated=True).exclude(start_year__gt=datetime.date.today().year).exclude(end_year__lt=datetime.date.today().year).count()
    return ain7_render_to_response(request, 'adhesions/index.html',
        {'subscriptions_list': Subscription.objects.filter(validated=True).order_by('-start_year', '-end_year')[:10],
         'count_members': AIn7Member.objects.count(),
         'count_subscribers': count_subscribers})

@login_required
def subscriptions(request, to_validate=False):
    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    nb_results_by_page = 50
    subscriptions_list = Subscription.objects.order_by('validated', '-start_year', '-end_year')

    if to_validate:
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
         'hits': paginator.count})

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

    subscriptions_list = Subscription.objects.filter(member=ain7member).order_by('-start_year')

    return ain7_render_to_response(request, 'adhesions/user_subscriptions.html',
                            {'person': p, 'ain7member': ain7member, 'subscriptions_list': subscriptions_list})

@login_required
def subscription_add(request, user_id=None):
    r = check_access(request, request.user, ['ain7-secretariat'])
    if r and unicode(request.user.id) != user_id:
        return r

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    title = _('Adding a subscription for')

    pageDict = {'action_title': title, 'person': person,
                'configurations': SubscriptionConfiguration.objects.all().order_by('type'),
                'back': request.META.get('HTTP_REFERER', '/')}

    # 1er passage : on propose un formulaire avec les données actuelles
    if request.method == 'GET':
        if Subscription.objects.filter(member=ain7member).exclude(start_year__gt=datetime.date.today().year).exclude(end_year__lt=datetime.date.today().year):
            request.user.message_set.create(message=_('You already have an active subscription.'))
        f = SubscriptionForm()
        pageDict.update({'form': f})
        return ain7_render_to_response(request, 'adhesions/subscribe.html', pageDict)

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        f = SubscriptionForm(request.POST.copy(), request.FILES)
        if f.is_valid():
            configuration = SubscriptionConfiguration.objects.get(type=f.data['configuration'])
            formInitDict = {'member': ain7member,
                            'end_year': f.cleaned_data['start_year'] + configuration.duration - 1}
            for k,v in formInitDict.iteritems():
                f.cleaned_data[k] = v
            subscription = f.save()
            if isinstance(subscription, LoggedClass) and request.user:
                subscription.logged_save(request.user.person)
            request.user.message_set.create(message=_('Subscription successfully added.'))
        else:
            pageDict.update({'form': f})
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            return ain7_render_to_response(request, 'adhesions/subscribe.html', pageDict)
        redirect = reverse(user_subscriptions, kwargs={'user_id': user_id})
        return HttpResponseRedirect(redirect)

@login_required
def configurations(request):
    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    return ain7_render_to_response(request, 'adhesions/configurations.html',
                                   {'configurations_list': SubscriptionConfiguration.objects.all().order_by('type')})

@login_required
def configuration_edit(request, configuration_id=None):
    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    configuration = None
    action = 'create'
    msgDone = _('Configuration successfully added.')
    if configuration_id:
        configuration = get_object_or_404(SubscriptionConfiguration, pk=configuration_id)
        action = 'edit'
        msgDone = _('Configuration informations updated successfully.')
    return ain7_generic_edit(
        request, configuration, ConfigurationForm, {},
        'adhesions/configuration_edit.html',
        {'action': 'create', 'back': request.META.get('HTTP_REFERER', '/')}, {},
         reverse(configurations), msgDone)

@confirmation_required(lambda user_id=None, configuration_id=None : str(get_object_or_404(SubscriptionConfiguration, pk=configuration_id)), 'adhesions/base.html', _('Do you really want to delete this configuration'))
@login_required
def configuration_delete(request, configuration_id=None):

    r = check_access(request, request.user, ['ain7-secretariat','ain7-ca'])
    if r:
        return r

    return ain7_generic_delete(request, get_object_or_404(SubscriptionConfiguration, pk=configuration_id),
                               reverse(configurations),
                               _('Configuration successfully deleted.'))
