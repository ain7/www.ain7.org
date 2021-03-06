# -*- coding: utf-8
"""
 ain7/shop/models.py
"""
#
#   Copyright © 2007-2018 AIn7 Devel Team
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

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person
from ain7.groups.models import Group


class PackageCategory(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(
        _('Description'), max_length=200, blank=True, null=True,
    )

    def __unicode__(self):
        return self.name


class Package(models.Model):
    category = models.ForeignKey('shop.PackageCategory', null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(
        _('Description'), max_length=200, blank=True, null=True
    )

    def __unicode__(self):
        return self.name

    def amount(self, person=None):

        from ain7.filters_local import FILTERS

        amount = 0
        for article in self.article_set.all():
            price_proposal = []
            for price in article.articleprice_set.all():
                if person and price.filter:
                    if person in Person.objects.filter(
                        FILTERS[price.filter.filter][1]
                    ):
                        price_proposal.append(price.price)
                else:
                    price_proposal.append(price.price)

            amount += min(price_proposal)
        return amount


class Article(models.Model):
    package = models.ForeignKey('shop.Package')
    name = models.CharField(max_length=50)
    description = models.TextField(
        _('Description'), max_length=200, blank=True, null=True
    )
    option = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class ArticlePrice(models.Model):
    article = models.ForeignKey('shop.Article')
    price = models.IntegerField()
    filter = models.ForeignKey('manage.Filter')


class ShoppingCart(models.Model):

    name = models.CharField(max_length=50, null=True, blank=True)
    saved = models.BooleanField(default=False)
    person = models.ForeignKey('annuaire.Person')


class ShoppingCartItem(models.Model):

    shoppingcart = models.ForeignKey('shop.ShoppingCart')
    package = models.ForeignKey('shop.Package')
    quantity = models.IntegerField(default=1)


class Order(models.Model):

    person = models.ForeignKey('annuaire.Person')
    payment = models.OneToOneField('shop.Payment', null=True, blank=True)
    shoppingcart = models.ForeignKey('shop.ShoppingCart')

    def amount(self):
        amount = 0
        for item in self.shoppingcart.shoppingcartitem_set.all():
            amount += item.quantity * item.package.amount(self.person)
        return amount


class PaymentMethod(models.Model):
    """payment method"""

    name = models.CharField(
        verbose_name=_('name'), max_length=200, null=True, blank=True,
    )
    public = models.BooleanField(verbose_name=_('public'), default=False)
    obsolete = models.BooleanField(verbose_name=_('obsolete'), default=False)

    def __unicode__(self):
        """return unicode representation of means of payment"""
        return self.name


class Payment(models.Model):
    """payment"""

    TYPE = (
        (1, _('Cash')),
        (2, _('Check CE')),
        (3, _('Check CCP')),
        (4, _('Card')),
        (5, _('Transfer CE')),
        (6, _('Transfer CCP')),
        (7, _('Other')),
    )

    person = models.ForeignKey('annuaire.Person', blank=True, null=True)
    method = models.ForeignKey('shop.PaymentMethod', blank=True, null=True)

    amount = models.FloatField(verbose_name=_('amount'))
    type = models.IntegerField(verbose_name=_('Type'), choices=TYPE)

    bank = models.CharField(
        verbose_name=_('Bank'), max_length=200, null=True, blank=True
    )
    check_number = models.CharField(
        verbose_name=_('Check number'), max_length=200, null=True, blank=True,
    )
    date = models.DateField(verbose_name=_('payment date'), null=True)
    validated = models.BooleanField(verbose_name=_('validated'), default=False)
    deposited = models.DateTimeField(
        verbose_name=_('deposit date'), null=True, blank=True
    )

    created_at = models.DateTimeField(
        verbose_name=_('registration date'), editable=False,
    )
    created_by = models.ForeignKey(
        'annuaire.Person', null=True, editable=False,
        related_name='payment_added',
    )
    modified_at = models.DateTimeField(
        verbose_name=_('modification date'), editable=False,
    )
    modified_by = models.ForeignKey(
        'annuaire.Person', null=True,
        editable=False, related_name='payment_modified',
    )

    def save(self):
        """custom save method to save creation timesamp"""

        if self.created_at:
            selfdb = Payment.objects.get(pk=self.pk)

            if not selfdb.validated and self.validated:

                membre = Group.objects.get(name=settings.AIN7_MEMBERS)
                membre.add(self.person)
                self.validate_mail()

        if not self.created_at:
            self.created_at = datetime.datetime.now()
        self.modified_at = datetime.datetime.now()
        return super(Payment, self).save()

    def __unicode__(self):
        """payment unicode"""
        uni = _('payment of ') + str(self.amount)
        if self.person:
            uni += _(' from ') + ' ' + self.person.complete_name
        return uni

    def validate_mail(self):
        """send a mail saying subscription is now validated"""

        if self.subscriptions.count() == 1:
            sub = self.subscriptions.order_by('id')[0]
            sub.validated = True
            sub.save()

            self.person.send_mail(
                _(u'AIn7 Subscription validated'),
                _(u"""Hi %(firstname)s,

We have validated your subscription for the next year to the association AIn7.

We remind you that you have an access to the website and can update your
personal informations by accessing this link:
https://ain7.com/annuaire/%(id)s/edit/

On the website, you can find the directory, next events, news in the N7
world, employment.

All the AIn7 Team would like to thanks you for you support. See you on
the website or at one of our events.

Cheers,

AIn7 Team

""") % {'firstname': self.person.first_name, 'id': self.person.id})
