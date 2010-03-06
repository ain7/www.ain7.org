# -*- coding: utf-8
"""
 ain7:adhesions/views.py
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

import datetime

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _

from ain7.adhesions.forms import ConfigurationForm, SubscriptionForm
from ain7.adhesions.models import Subscription, SubscriptionConfiguration
from ain7.annuaire.models import AIn7Member, Person
from ain7.manage.models import Payment
from ain7.decorators import confirmation_required
from ain7.utils import ain7_render_to_response
from ain7.utils import ain7_generic_delete, check_access


def index(request):
    """index adhesions"""
    count_subscribers = Subscription.objects.filter(validated=True).exclude(\
        start_year__gt=datetime.date.today().year).exclude(\
        end_year__lt=datetime.date.today().year).count()

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/accounts/login/?next=' + \
           reverse('ain7.adhesions.views.index'))

    user_groups = request.user.groups.all().values_list('name', flat=True)

    if not 'ain7-secretariat' in user_groups and \
        not 'ain7-admin' in user_groups and \
        not 'ain7-ca' in user_groups:
        return HttpResponseRedirect('/adhesions/'+str(request.user.id)+ \
            '/subscriptions/add/')

    return ain7_render_to_response(request, 'adhesions/index.html',
        {'subscriptions_list': Subscription.objects.filter(validated=True).\
            order_by('-id')[:20],
         'count_members': AIn7Member.objects.count(),
         'count_subscribers': count_subscribers})

@login_required
def subscriptions(request, to_validate=False):
    """list subscriptions"""
    access = check_access(request, request.user,
        ['ain7-secretariat','ain7-ca'])
    if access:
        return access

    nb_results_by_page = 50
    subscriptions_list = Subscription.objects.order_by(\
         'validated', '-start_year', '-end_year')

    if to_validate:
        subscriptions_list = subscriptions_list.filter(validated=False)
    paginator = Paginator(subscriptions_list, nb_results_by_page)

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

@confirmation_required(lambda user_id=None, subscription_id=None : 
     str(get_object_or_404(Subscription, pk=subscription_id)), 
     'adhesions/base.html', 
    _('Do you really want to validate this subscription'))
@login_required
def subscription_validate(request, subscription_id=None):
    """validate subscription"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access

    subscription = get_object_or_404(Subscription, pk=subscription_id)
    subscription.validated = True
    subscription.logged_save(request.user.person)

    request.user.message_set.create(\
         message=_('Subscription successfully validated'))
    return HttpResponseRedirect(reverse(subscriptions))

@confirmation_required(lambda user_id=None, subscription_id=None :
    str(get_object_or_404(Subscription, pk=subscription_id)),
    'adhesions/base.html', 
    _('Do you really want to delete this subscription'))
@login_required
def subscription_delete(request, subscription_id=None):
    """delete subscription"""

    access = check_access(request, request.user, ['ain7-secretariat'])
    if access:
        return access

    return ain7_generic_delete(request,
        get_object_or_404(Subscription, pk=subscription_id),
        reverse(subscriptions),
        _('Subscription successfully deleted'))

@login_required
def user_subscriptions(request, user_id):
    """show user subscriptions"""

    access = check_access(request, request.user,
        ['ain7-secretariat','ain7-ca'])
    is_myself = int(request.user.id) == int(user_id)

    if access and not is_myself:
        return access

    person = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    subscriptions_list = Subscription.objects.filter(member=ain7member).\
        order_by('-start_year')

    return ain7_render_to_response(request, 
        'adhesions/user_subscriptions.html',
        {'person': person, 'ain7member': ain7member, 
         'subscriptions_list': subscriptions_list})

@login_required
def subscription_add(request, user_id=None):
    """add user subscription"""
    access = check_access(request, request.user, ['ain7-secretariat'])
    if access and unicode(request.user.id) != user_id:
        return access

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    title = _('Adding a subscription for')

    page_dict = {'action_title': title, 'person': person,
        'configurations': SubscriptionConfiguration.objects.all().\
             order_by('type'),
        'back': request.META.get('HTTP_REFERER', '/')}

    # 1er passage : on propose un formulaire avec les données actuelles
    if request.method == 'GET':
        if Subscription.objects.filter(member=ain7member).\
            exclude(start_year__gt=datetime.date.today().year).\
            exclude(end_year__lt=datetime.date.today().year):
            request.user.message_set.create(\
            message=_('You already have an active subscription.'))
        form = SubscriptionForm()
        page_dict.update({'form': form})
        return ain7_render_to_response(request, 
            'adhesions/subscribe.html', page_dict)

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        form = SubscriptionForm(request.POST.copy(), request.FILES)
        if form.is_valid():
            configuration = SubscriptionConfiguration.objects.get(\
                type=form.data['configuration'])

            subscription = Subscription()
            subscription.dues_amount = form.cleaned_data['dues_amount']
            subscription.newspaper_amount = \
                form.cleaned_data['newspaper_amount']
            subscription.tender_type = form.cleaned_data['tender_type']
            subscription.start_year = form.cleaned_data['start_year']
            subscription.end_year = form.cleaned_data['start_year'] + \
                configuration.duration - 1
            subscription.date = datetime.date.today()
            subscription.member = ain7member

            payment = Payment()
            payment.amount = form.cleaned_data['dues_amount']
            if form.cleaned_data['newspaper_amount']:
                payment.amount += form.cleaned_data['newspaper_amount']
            payment.type = form.cleaned_data['tender_type']
            payment.person = ain7member.person
            payment.date = datetime.date.today()
            payment.save()

            subscription.payment = payment
            subscription.save()

            if person == request.user.person:
                person.send_mail(_(u'AIn7 subscription request registered'), \
_(u"""Hi %(firstname)s,

We have registered your subscription request for the next year to the
association AIn7. Your subscription will be validated as soon as we have
received your payment.

All the AIn7 Team would like to thanks you for you support. See you on
the website or at one of our events.

Cheers,

AIn7 Team

""") % { 'firstname': person.first_name })

            spplusurl = ''

            if payment.type == 4:

                import subprocess
                from django.conf import settings

                data = "siret=%(siret)s&montant=%(amount)s.00&taxe=0.00&\
validite=31/12/2099&langue=FR&devise=978&version=1&reference=%(reference)s" \
 % { 'siret': settings.AIN7_SIRET, 'amount': payment.amount,
     'reference': payment.id }
                
                proc = subprocess.Popen('REQUEST_METHOD=GET QUERY_STRING=\''+ \
                    data+'\' '+settings.SPPLUS_EXE, shell=True, \
                    stdout=subprocess.PIPE)
                spplusurl = proc.communicate()[0].replace('Location: ','').\
                    replace('\n','')
                print spplusurl

            return ain7_render_to_response(request,
                 'adhesions/informations.html',
                 {'payment': payment, 'spplusurl': spplusurl })

@login_required
def configurations(request):
    """configure subscriptions"""
    access = check_access(request, request.user,
        ['ain7-secretariat','ain7-ca'])
    if access:
        return access

    return ain7_render_to_response(request, 'adhesions/configurations.html',
        {'configurations_list': 
         SubscriptionConfiguration.objects.all().order_by('type')})

@login_required
def configuration_edit(request, config_id=None):
    """edit subscription configuration"""
    access = check_access(request, request.user, 
        ['ain7-secretariat','ain7-ca'])
    if access:
        return access

    form = ConfigurationForm()

    if config_id:
        config = get_object_or_404(SubscriptionConfiguration,
            pk=config_id)
        form = ConfigurationForm(instance=config)

    if request.method == 'POST':
        if config_id:
            form = ConfigurationForm(request.POST, instance=config)
        else:
            form = ConfigurationForm(request.POST)
        if form.is_valid():
            form.save()
            request.user.message_set.create(message=_('Modifications have been\
 successfully saved.'))

        return HttpResponseRedirect(reverse(configurations))

    return ain7_render_to_response(
        request, 'adhesions/configuration_edit.html',
        {'form': form, 'action_title': _("Modification of configuration"),
         'back': request.META.get('HTTP_REFERER', '/')})

@confirmation_required(lambda user_id=None, config_id=None:
    str(get_object_or_404(SubscriptionConfiguration, pk=config_id)),
    'adhesions/base.html', _('Do you really want to delete this configuration'))
@login_required
def configuration_delete(request, config_id=None):
    """delete subscription configuration"""

    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-ca'])
    if access:
        return access

    return ain7_generic_delete(request, 
         get_object_or_404(SubscriptionConfiguration, pk=config_id),
         reverse(configurations),
         _('Configuration successfully deleted.'))

def notification(request):
    """SPPlus notification url management"""

    from django.conf import settings

    if not settings.DEBUG and not request.META['REMOTE_ADDR'] in \
    settings.SPPLUS_IP:
        return  HttpResponseRedirect('/')

    if request.method == 'GET':
        if request.GET.has_key('etat'):
            etat = request.GET['etat']
        if request.GET.has_key('reference'):
            reference = request.GET['reference']

        if etat == '1':
            pay = Payment.objects.get(id=reference)
            pay.validated = True
            pay.save()

    return ain7_render_to_response(request, 'adhesions/notification.html', {})

