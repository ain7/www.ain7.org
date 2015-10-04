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

import autocomplete_light
import datetime
import hashlib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from ain7.adhesions.models import (
    Subscription, SubscriptionConfiguration, SubscriptionKey
)
from ain7.annuaire.models import AIn7Member, Person
from ain7.shop.models import Payment
from ain7.decorators import access_required, confirmation_required
from ain7.utils import ain7_generic_delete


@login_required
def index(request):
    """index adhesions"""

    count_subscribers = Subscription.objects.filter(validated=True).exclude(
        start_year__gt=timezone.now().date().year).exclude(
        end_year__lt=timezone.now().date().year).count()

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


@access_required(groups=['ain7-secretariat', 'ain7-ca'])
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


@confirmation_required(lambda user_id=None, subscription_id=None:
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


@confirmation_required(lambda user_id=None, subscription_id=None:
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


#FIXME: allow everyone to scubscribe as we have oublic subscription
# and there is no financial impact as transaction need to be validated
#@access_required(groups=['ain7-secretariat'], allow_myself=True)
def subscription_add(request, user_id=None, key_id=None, config_id=None):
    """add user subscription"""

    if key_id:
        key = get_object_or_404(SubscriptionKey, key=key_id)
        user_id = key.person.pk

    if user_id:
        person = get_object_or_404(Person, user=user_id)
    elif request.user.is_authenticated():
        person = request.user.person
        user_id = person.pk

    if config_id:
        subscription_configuration = get_object_or_404(
            SubscriptionConfiguration, pk=config_id
        )

    year_current = timezone.now().date().year

    #page_dict = {'action_title': title, 'person': person,
    #    'configurations': SubscriptionConfiguration.objects.filter(year=year_current).\
    #         order_by('type'),
    #    'back': request.META.get('HTTP_REFERER', '/')}


    subscription_fields = ('configuration', 'tender_type', 'newspaper_subscription')
    if not user_id:
        subscription_fields += ('member',)

    SubscriptionForm = autocomplete_light.modelform_factory(
        Subscription,
        fields = subscription_fields,
    )
    form = SubscriptionForm(request.POST or None)
    form.fields['configuration'].queryset = SubscriptionConfiguration.objects.filter(year=year_current)

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST' and form.is_valid():

        subscription = form.save(commit=False)

        if user_id:
            subscription.member = person.ain7member
        if config_id:
            subscription.configuration = subscription_configuration
        subscription.dues_amount = subscription.configuration.dues_amount
        subscription.newspaper_amount = subscription.configuration.newspaper_amount
        subscription.tender_type = subscription.tender_type
        subscription.start_year = timezone.now().date().year
        subscription.start_date = timezone.now().date()
        if subscription.configuration.type in [SubscriptionConfiguration.TYPE_STUDENT_3Y, SubscriptionConfiguration.TYPE_STUDENT_2Y, SubscriptionConfiguration.TYPE_STUDENT_1Y]:
            subscription.end_year = subscription.member.promo
            subscription.end_date = datetime.date(subscription.member.promo, 10, 1)
        else:
            subscription.end_year = timezone.now().date().year+1
            subscription.end_date = subscription.start_date.replace(year=subscription.end_year)
        subscription.date = timezone.now().date()
        subscription.save()

        payment = Payment()
        payment.amount = subscription.dues_amount
        if subscription.newspaper_subscription:
            payment.amount += subscription.newspaper_amount
        payment.type = subscription.tender_type
        payment.person = subscription.member.person
        payment.date = timezone.now().date()
        payment.save()

        subscription.payment = payment
        subscription.save()

        subscription.member.person.send_mail(_(u'AIn7 subscription request registered'), \
_(u"""Hi %(firstname)s,

We have registered your subscription request for the next year to the
association AIn7. Your subscription will be validated as soon as we have
received your payment.

All the AIn7 Team would like to thanks you for you support. See you on
the website or at one of our events.

Cheers,

AIn7 Team

""") % { 'firstname': subscription.member.person.first_name })

        systempay = {}
        systempay_signature = ''

        if payment.type == 4:

            # payment amount in cents
            systempay['vads_amount'] = str(payment.amount*100)
            # 978 is code for Euros
            systempay['vads_currency'] = '978'
            systempay['vads_site_id'] = str(settings.SYSTEM_PAY_SITE_ID)
            systempay['vads_trans_id'] = "%06d" % (payment.id % 900000)
            systempay['vads_trans_date'] = timezone.now().strftime("%Y%m%d%H%M%S")
            systempay['vads_version'] = 'V2'
            systempay['vads_payment_config'] = 'SINGLE'
            systempay['vads_page_action'] = 'PAYMENT'
            systempay['vads_action_mode'] = 'INTERACTIVE'
            systempay['vads_ctx_mode'] = str(settings.SYSTEM_PAY_MODE)
            systempay['vads_order_id'] = str(payment.id)
            systempay['vads_cust_name'] = subscription.member.person.complete_name
            systempay['vads_cust_email'] = subscription.member.person.mail_favorite()

            systempay_string = '+'.join([v.encode('utf-8') for k, v in sorted(systempay.items())])+'+'+settings.SYSTEM_PAY_CERTIFICATE
            systempay_signature = hashlib.sha1(systempay_string).hexdigest()

        return render(request, 'adhesions/informations.html', {
            'payment': payment,
            'systempay': systempay,
            'systempay_signature': systempay_signature,
            'systempay_url': settings.SYSTEM_PAY_URL
            }
        )

    return render(request, 'adhesions/subscribe_form.html', {
        'form': form,
        }
    )


def welcome_subscription(request, person_id):

    member = get_object_or_404(AIn7Member, person__pk=person_id)
    configuration = SubscriptionConfiguration.objects.get(
        type=SubscriptionConfiguration.TYPE_STUDENT_3Y,
        year=timezone.now().date().year,
    )

    SubscriptionForm = modelform_factory(Subscription, fields=('tender_type',))
    form = SubscriptionForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        subscription = form.save(commit=False)
        subscription.member = member
        subscription.dues_amount = configuration.dues_amount
        subscription.newspaper_amount = configuration.newspaper_amount
        subscription.date = timezone.now().date()
        subscription.start_year = timezone.now().date().year
        subscription.end_year = timezone.now().date().year + 3
        subscription.save()

        payment = Payment()
        payment.amount = subscription.dues_amount
        payment.type = subscription.tender_type
        payment.person = member.person
        payment.date = timezone.now().date()
        payment.save()

        systempay = {}
        systempay_signature = ''

        if subscription.tender_type == 4:

            # payment amount in cents
            systempay['vads_amount'] = str(subscription.dues_amount*100)
            # 978 is code for Euros
            systempay['vads_currency'] = '978'
            systempay['vads_site_id'] = str(settings.SYSTEM_PAY_SITE_ID)
            systempay['vads_trans_id'] = "%06d" % (payment.id % 900000)
            systempay['vads_trans_date'] = timezone.now().strftime("%Y%m%d%H%M%S")
            systempay['vads_version'] = 'V2'
            systempay['vads_payment_config'] = 'SINGLE'
            systempay['vads_page_action'] = 'PAYMENT'
            systempay['vads_action_mode'] = 'INTERACTIVE'
            systempay['vads_ctx_mode'] = str(settings.SYSTEM_PAY_MODE)
            systempay['vads_order_id'] = str(payment.id)
            systempay['vads_cust_name'] = member.person.complete_name
            systempay['vads_cust_email'] = member.person.mail_favorite()

            systempay_string = '+'.join([v.encode('utf-8') for k, v in sorted(systempay.items())])+'+'+settings.SYSTEM_PAY_CERTIFICATE
            systempay_signature = hashlib.sha1(systempay_string).hexdigest()

        return render(request, 'adhesions/informations.html', {
            'payment': payment,
            'systempay': systempay,
            'systempay_signature': systempay_signature,
            'systempay_url': settings.SYSTEM_PAY_URL
            }
        )

    return render(request, 'adhesions/welcome.html', {
        'form': form,
        'member': member,
        }
    )


@access_required(groups=['ain7-secretariat', 'ain7-ca'])
def configurations(request, year=timezone.now().date().year):
    """configure subscriptions"""

    year = int(year)

    # let's create configurations on the fly, but only for next year
    if (
        SubscriptionConfiguration.objects.filter(year=year).count() == 0
        and
        year <= timezone.now().date().year + 1
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


@access_required(groups=['ain7-secretariat', 'ain7-ca'])
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

    return ain7_generic_delete(
        request,
        get_object_or_404(SubscriptionConfiguration, pk=config_id),
        reverse(configurations),
        _('Configuration successfully deleted.')
    )


@csrf_exempt
def notification(request):
    """SPPlus notification url management"""

    from django.conf import settings

    if request.method == 'POST':

        systempay_string = '+'.join([v.encode('utf-8') for k, v in sorted(request.POST.items()) if k.startswith('vads_')])+'+'+settings.SYSTEM_PAY_CERTIFICATE
        systempay_signature = hashlib.sha1(systempay_string).hexdigest()

        if systempay_signature == request.POST['signature'] and request.POST['vads_result'] == '00':

            pay = Payment.objects.get(id=int(request.POST['vads_order_id']))
            pay.validated = True
            pay.save()

    return render(request, 'adhesions/notification.html', {})
