# -*- coding: utf-8
"""
 ain7:adhesions/views.py
"""
#
#   Copyright © 2007-2015 AIn7 Devel Team
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
import hashlib

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from ain7.adhesions.forms import SubscriptionForm
from ain7.adhesions.models import Subscription, SubscriptionConfiguration
from ain7.annuaire.models import AIn7Member, Person
from ain7.shop.models import Payment
from ain7.decorators import access_required, confirmation_required
from ain7.utils import ain7_generic_delete


def index(request):
    """index adhesions"""

    count_subscribers = Subscription.objects.filter(validated=True).exclude(
        start_year__gt=datetime.date.today().year).exclude(
        end_year__lt=datetime.date.today().year).count()

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/accounts/login/?next=' +
           reverse('ain7.adhesions.views.index'))

    user_groups = request.user.person.groups.values_list('group__name', flat=True)

    if not 'ain7-secretariat' in user_groups and \
        not 'ain7-admin' in user_groups and \
        not 'ain7-ca' in user_groups:
        return HttpResponseRedirect('/adhesions/'+str(request.user.id)+ 
            '/subscriptions/add/')

    return render(request, 'adhesions/index.html', {
        'subscriptions_list': Subscription.objects.filter(
            validated=True
        ).order_by('-id')[:20],
        'count_members': AIn7Member.objects.count(),
        'count_subscribers': count_subscribers
        }
    )


@access_required(groups=['ain7-secretariat','ain7-ca'])
def subscriptions(request, to_validate=False):
    """list subscriptions"""

    subscriptions_list = Subscription.objects.order_by(
         'validated', '-start_year', '-end_year')

    if to_validate:
        subscriptions_list = subscriptions_list.filter(validated=False)

    return render(request, 'adhesions/subscriptions.html', {
        'subscriptions_list': subscriptions_list,
        }
    )


@confirmation_required(lambda user_id=None, subscription_id=None : 
     str(get_object_or_404(Subscription, pk=subscription_id)), 
     'adhesions/base.html', 
    _('Do you really want to validate this subscription'))
@access_required(groups=['ain7-secretariat'])
def subscription_validate(request, subscription_id=None):
    """validate subscription"""

    subscription = get_object_or_404(Subscription, pk=subscription_id)
    subscription.validated = True
    subscription.logged_save(request.user.person)

    messages.success(request, _('Subscription successfully validated'))
    return redirect('subscriptions')


@confirmation_required(lambda user_id=None, subscription_id=None :
    str(get_object_or_404(Subscription, pk=subscription_id)),
    'adhesions/base.html', 
    _('Do you really want to delete this subscription'))
@access_required(groups=['ain7-secretariat'])
def subscription_delete(request, subscription_id=None):
    """delete subscription"""

    return ain7_generic_delete(request,
        get_object_or_404(Subscription, pk=subscription_id),
        reverse(subscriptions),
        _('Subscription successfully deleted'))


@access_required(groups=['ain7-secretariat', 'ain7-ca'], allow_myself=True)
def user_subscriptions(request, user_id):
    """show user subscriptions"""

    person = get_object_or_404(Person, pk=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    subscriptions_list = Subscription.objects.filter(member=ain7member).\
        order_by('-start_year', '-id')

    return render(request, 'adhesions/user_subscriptions.html', {
        'person': person,
        'ain7member': ain7member,
        'subscriptions_list': subscriptions_list,
        }
    )


@access_required(groups=['ain7-secretariat'], allow_myself=True)
def subscription_add(request, user_id=None):
    """add user subscription"""

    person = get_object_or_404(Person, user=user_id)
    ain7member = get_object_or_404(AIn7Member, person=person)

    title = _('Adding a subscription for')

    year_current = datetime.date.today().year

    page_dict = {'action_title': title, 'person': person,
        'configurations': SubscriptionConfiguration.objects.filter(year=year_current).\
             order_by('type'),
        'back': request.META.get('HTTP_REFERER', '/')}

    # 1er passage : on propose un formulaire avec les données actuelles
    if request.method == 'GET':
        if Subscription.objects.filter(member=ain7member).\
            exclude(start_year__gt=year_current).\
            exclude(end_year__lt=year_current):
            messages.warning(request, _('You already have an active subscription.'))
        form = SubscriptionForm()
        page_dict.update({'form': form})
        return render(request, 
            'adhesions/subscribe.html', page_dict)

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        form = SubscriptionForm(request.POST.copy(), request.FILES)
        if form.is_valid():
            configuration = SubscriptionConfiguration.objects.get(\
                type=form.data['configuration'], year=year_current)

            subscription = Subscription()
            subscription.dues_amount = form.cleaned_data['dues_amount']
            subscription.newspaper_amount = \
                form.cleaned_data['newspaper_amount']
            subscription.tender_type = form.cleaned_data['tender_type']
            subscription.start_year = form.cleaned_data['start_year']
            subscription.end_year = form.cleaned_data['start_year'] + \
                configuration.duration - 1
            subscription.date = datetime.datetime.now()
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

            systempay = {}
            systempay_signature = ''

            if payment.type == 4:

                # payment amount in cents
                systempay['vads_amount'] = payment.amount*100
                # 978 is code for Euros
                systempay['vads_currency'] = 978
                systempay['vads_site_id'] = settings.SYSTEM_PAY_SITE_ID
                systempay['vads_trans_id'] = "%06d" % (payment.id % 900000)
                systempay['vads_trans_date'] = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
                systempay['vads_version'] = 'V2'
                systempay['vads_payment_config'] = 'SINGLE'
                systempay['vads_page_action'] = 'PAYMENT'
                systempay['vads_action_mode'] = 'INTERACTIVE'
                systempay['vads_ctx_mode'] = settings.SYSTEM_PAY_MODE
                systempay['vads_order_id'] = payment.id
                systempay['vads_cust_name'] = person.complete_name.encode('utf-8')
                systempay['vads_cust_email'] = person.mail_favorite()

                systempay_string = '+'.join([str(v) for k, v in sorted(systempay.items())])+'+'+settings.SYSTEM_PAY_CERTIFICATE
                systempay_signature = hashlib.sha1(systempay_string).hexdigest()

            return render(request, 'adhesions/informations.html', {
                'payment': payment,
                'systempay': systempay,
                'systempay_signature': systempay_signature,
                'systempay_url': settings.SYSTEM_PAY_URL
                }
            )


@access_required(groups=['ain7-secretariat', 'ain7-ca'])
def configurations(request, year=datetime.date.today().year):
    """configure subscriptions"""

    year = int(year)

    # let's create configurations on the fly, but only for next year
    if (
        SubscriptionConfiguration.objects.filter(year=year).count() == 0
        and
        year <= datetime.date.today().year + 1
        and
        SubscriptionConfiguration.objects.filter(year=year-1).count() > 0
    ):
        for conf in SubscriptionConfiguration.objects.filter(year=year-1):
            conf.id = None
            conf.year = year
            conf.save()

    return render(request, 'adhesions/configurations.html', {
        'configurations_list': SubscriptionConfiguration.objects.filter(
            year=year
            ).order_by('type'),
        }
    )


@access_required(groups=['ain7-secretariat','ain7-ca'])
def configuration_edit(request, year, config_id=None):
    """edit subscription configuration"""

    config = None
    if config_id:
        config = get_object_or_404(SubscriptionConfiguration, pk=config_id)

    ConfigurationForm = modelform_factory(SubscriptionConfiguration, exclude=())
    form = ConfigurationForm(request.POST or None, instance=config)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _('Modifications have been successfully saved.'))
        return redirect('configurations')

    return render(request, 'adhesions/configuration_edit.html', {
        'form': form,
        'action_title': _("Modification of configuration"),
        'back': request.META.get('HTTP_REFERER', '/'),
        }
    )


@confirmation_required(lambda user_id=None, config_id=None:
    str(get_object_or_404(SubscriptionConfiguration, pk=config_id)),
    'adhesions/base.html', _('Do you really want to delete this configuration'))
@access_required(groups=['ain7-secretariat', 'ain7-ca'])
def configuration_delete(request, config_id=None):
    """delete subscription configuration"""

    return ain7_generic_delete(request, 
         get_object_or_404(SubscriptionConfiguration, pk=config_id),
         reverse(configurations),
         _('Configuration successfully deleted.'))


@csrf_exempt
def notification(request):
    """SPPlus notification url management"""

    from django.conf import settings

    if request.method == 'POST':
       
        systempay_string = '+'.join([str(v) for k, v in sorted(request.POST.items()) if k.startswith('vads_')])+'+'+settings.SYSTEM_PAY_CERTIFICATE
        systempay_signature = hashlib.sha1(systempay_string).hexdigest()

        if systempay_signature == request.POST['signature'] and request.POST['vads_result'] == '00':

            pay = Payment.objects.get(id=int(request.POST['vads_order_id']))
            pay.validated = True
            pay.save()

    return render(request, 'adhesions/notification.html', {})
