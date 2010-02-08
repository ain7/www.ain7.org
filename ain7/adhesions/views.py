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
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from ain7.adhesions.forms import ConfigurationForm, SubscriptionForm
from ain7.adhesions.models import Subscription, SubscriptionConfiguration
from ain7.annuaire.models import AIn7Member, Person
from ain7.manage.models import Payment
from ain7.decorators import confirmation_required
from ain7.utils import ain7_render_to_response, ain7_generic_edit
from ain7.utils import ain7_generic_delete, check_access, LoggedClass


def index(request):
    """index adhesions"""
    count_subscribers = Subscription.objects.filter(validated=True).exclude(\
        start_year__gt=datetime.date.today().year).exclude(\
        end_year__lt=datetime.date.today().year).count()
    return ain7_render_to_response(request, 'adhesions/index.html',
        {'subscriptions_list': Subscription.objects.filter(validated=True).\
            order_by('-start_year', '-end_year', '-id')[:20],
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
    if access and unicode(request.user.id) != user_id:
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
    if access:
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
            subscription.member = ain7member

            payment = Payment()
            payment.amount = form.cleaned_data['dues_amount'] + \
                form.cleaned_data['newspaper_amount']
            payment.type = form.cleaned_data['tender_type']
            payment.person = ain7member.person
            payment.date = datetime.date.today()
            payment.save()

            subscription.payment = payment
            subscription.save()

            request.user.person.send_mail(_(u'AIn7 Subscription registered'), \
_(u"""Hi %(firstname)s,

We have registered your subscription for the next year to the association AIn7.

We remind you that you have an access to the website and can update your
personal informations. On the website, you can find the directory,
next events, news in the N7 world, employment. If you have lost your 
password, you can recover at http://ain7.com/lostpassword/ .

All the AIn7 Team would like to thanks you for you support. See you on
the website or at one of our events.

Cheers,

AIn7 Team

""") % { 'firstname': request.user.person.first_name })

            if payment.type == 2:

                import ctypes
                from django.contrib.auth.models import User
                from ain7.settings import AIN7_SIRET, SPPLUS_CLENT, SPPLUS_LIB_PATH

                ctest = ctypes.CDLL(SPPLUS_LIB_PATH)
                clent = SPPLUS_CLENT
                secret_key =  User.objects.make_random_password(50)

                payment.secret_key = secret_key
                payment.save()

                data = 'https://www.spplus.net/paiement/init.do?montant='+str(payment.amount)+'&taxe=0&validite=31%2f12%2f2099&langue=FR&siret='+AIN7_SIRET+'&devise=978&reference='+str(payment.id)+'&arg2='+secret_key

                result = ctypes.c_char_p(ctest.signeURLPaiement(ctypes.c_char_p(clent), ctypes.c_char_p(data)))
                spplusurl = result.value
                ctest.free(result)
                return HttpResponseRedirect(spplusurl)

            if isinstance(subscription, LoggedClass) and request.user:
                subscription.logged_save(request.user.person)
            request.user.message_set.create(message=
                 _('Subscription successfully added'))
        else:
            page_dict.update({'form': form})
            request.user.message_set.create(message=_('Something was wrong in\
 the form you filled. No modification done.'))
            return ain7_render_to_response(request, 'adhesions/subscribe.html',
                page_dict)
        redirect = reverse(user_subscriptions, kwargs={'user_id': user_id})
        return HttpResponseRedirect(redirect)

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
def configuration_edit(request, configuration_id=None):
    """edit subscription configuration"""
    access = check_access(request, request.user, 
        ['ain7-secretariat','ain7-ca'])
    if access:
        return access

    configuration = None
    action = 'create'
    msg_done = _('Configuration successfully added.')
    if configuration_id:
        configuration = get_object_or_404(SubscriptionConfiguration,
            pk=configuration_id)
        action = 'edit'
        msg_done = _('Configuration informations updated successfully.')
    return ain7_generic_edit(
        request, configuration, ConfigurationForm, {},
        'adhesions/configuration_edit.html',
        {'action': 'create', 'back': request.META.get('HTTP_REFERER', '/')}, {},
         reverse(configurations), msg_done)

@confirmation_required(lambda user_id=None, configuration_id=None:
    str(get_object_or_404(SubscriptionConfiguration, pk=configuration_id)),
    'adhesions/base.html', _('Do you really want to delete this configuration'))
@login_required
def configuration_delete(request, configuration_id=None):
    """delete subscription configuration"""

    access = check_access(request, request.user,
        ['ain7-secretariat', 'ain7-ca'])
    if access:
        return access

    return ain7_generic_delete(request, 
         get_object_or_404(SubscriptionConfiguration, pk=configuration_id),
         reverse(configurations),
         _('Configuration successfully deleted.'))

def payment_validate(request):

    if request.method == 'GET':
        if request.GET.has_key('reference'):
            reference = request.GET['reference']
        if request.GET.has_key('montant'):
            montant = request.GET['montant']
        if request.GET.has_key('etat'):
            etat = request.GET['etat']
        if request.GET.has_key('arg2'):
            arg2 = request.GET['arg2']

        pay = Payment.objects.get(id=reference, amount=montant, secret_key=arg2)
        if etat == '1':
            pay.validated = True
            #pay.save()

            if pay.subscriptions.count() == 1:
               sub = pay.subscriptions.order_by('id')[0]
               sub.validated = True
               #sub.save()

    return  HttpResponseRedirect('/')

