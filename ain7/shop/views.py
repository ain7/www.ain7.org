# -*- coding: utf-8
"""
 ain7/shop/views.py
"""
#
#   Copyright © 2007-2017 AIn7 Devel Team
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

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _


from ain7.shop.forms import PaymentMethodForm
from ain7.shop.models import Order, Payment


def index(request):
    return reverse('homepage')

def order_pay(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    form = PaymentMethodForm()

    if request.method == 'POST':
       form = PaymentMethodForm(request.POST.copy())
       if form.is_valid():

            payment = form.save(commit=False)
            payment.person = request.user.person
            payment.amount = order.amount()
            payment.date = datetime.date.today()
            payment.created_by = request.user.person
            payment.modified_by = request.user.person
            payment.save()

            order.payment = payment
            order.save()

            spplusurl = ''

            if payment.type == 4:

                import subprocess
                from django.conf import settings

                reference = payment.id
                if settings.DEBUG:
                    reference = 'DEBUG-'+str(payment.id)

                data = "siret=%(siret)s&montant=%(amount)s.00&taxe=0.00&\
validite=31/12/2099&langue=FR&devise=978&version=1&reference=%(reference)s" \
 % { 'siret': settings.AIN7_SIRET, 'amount': payment.amount,
     'reference': reference }

                proc = subprocess.Popen('REQUEST_METHOD=GET QUERY_STRING=\''+ \
                    data+'\' '+settings.SPPLUS_EXE, shell=True, \
                    stdout=subprocess.PIPE)
                spplusurl = proc.communicate()[0].replace('Location: ','').\
                    replace('\n','')
                print spplusurl

            return render(request,
                 'shop/informations.html',
                 {'payment': payment, 'spplusurl': spplusurl })

    return render(request,
        'shop/form.html',
        {'form': form, })

