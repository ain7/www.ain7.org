# -*- coding: utf-8
"""
 ain7/pages/views.py
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

from django.conf import settings
from django.contrib import auth
from django.contrib import messages
from django.forms.models import modelform_factory
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext as _

from ain7.annuaire.models import AIn7Member, Email, Person
from ain7.decorators import access_required
from ain7.groups.models import Group
from ain7.news.models import NewsItem
from ain7.pages.forms import LostPasswordForm, ChangePasswordForm
from ain7.pages.models import Text, LostPassword


def homepage(request):
    """AIn7 homepage"""

    is_subscriber = False
    ain7member = None

    news = NewsItem.objects.filter(
        date__isnull=True,
        front_page_presence=True,
    ).order_by('-creation_date')[:5]
    events = NewsItem.objects.filter(
        date__gte=datetime.datetime.now()
    ).order_by('date')[:5]

    is_auth = request.user.is_authenticated()

    if is_auth:

        person = Person.objects.get(user=request.user.id)
        if AIn7Member.objects.filter(person=person).count() > 0:
            ain7member = get_object_or_404(AIn7Member, person=person)
            is_subscriber = ain7member.is_subscriber()

    return render(request, 'pages/homepage.html', {
        'news': news,
        'events': events,
        'settings': settings,
        'is_subscriber': is_subscriber,
        }
    )


def lostpassword(request):
    """lostpassword page"""

    form = LostPasswordForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        person = Email.objects.get(email=email).person

        person.password_ask(email=email, request=request)

        messages.success(request, _('We have sent you an email with\
 instructions to reset your password.'))
        return redirect('homepage')

    return render(request, 'pages/lostpassword.html', {'form': form})


def changepassword(request, key):
    """changepassword page"""

    form = ChangePasswordForm(request.POST or None)

    lostpw = get_object_or_404(LostPassword, key=key)

    if lostpw.is_expired():
        lostpw.delete()
        messages.error(request, _('Page expired, please request a new key'))
        return render(request, 'pages/changepassword.html')

    if request.POST and form.is_valid():
        person = lostpw.person
        lostpw.delete()
        person.user.set_password(form.cleaned_data['password'])
        person.user.save()
        messages.success(request, _('Successfully changed password'))
        user = auth.authenticate(
            username=person.user.username,
            password=form.cleaned_data['password']
        )
        auth.login(request, user)
        return redirect('homepage')

    return render(request, 'pages/changepassword.html', {
        'form': form,
        'person': lostpw.person
        }
    )


def apropos(request):
    """about page"""
    text = Text.objects.get(textblock__shortname='apropos')
    return render(request, 'pages/apropos.html', {'text': text})


def mentions_legales(request):
    """legal mentions"""
    text = Text.objects.get(textblock__shortname='mentions_legales')
    return render(request, 'pages/mentions_legales.html', {'text': text})


def rss(request):
    """rss feeds"""
    text = Text.objects.get(textblock__shortname='rss')
    return render(request, 'pages/rss.html', {'text': text})


@access_required(groups=['ain7-membre', 'ain7-ca', 'ain7-secretariat',
                         'ain7-contributeur'])
def edit(request, text_id):
    """edit text block"""

    text = get_object_or_404(Text, pk=text_id)

    TextForm = modelform_factory(Text, exclude=('textblock', 'lang'))
    form = TextForm(request.POST or None, instance=text)

    if request.method == 'POST' and form.is_valid():
        text = form.save()

        messages.success(request, message=_("Modifications saved."))
        return redirect(text)

    return render(request, 'pages/text_edit.html', {
        'text_id': text_id,
        'form': form,
        'back': request.META.get('HTTP_REFERER'),
        }
    )


def professionnal_groups(request):

    groups = Group.objects.filter(type__name='ain7-professionnel')
    text = Text.objects.get(textblock__shortname='groupes_professionnels')

    return render(request, 'pages/professionnal_groups.html', {
        'text': text,
        'groups': groups,
        }
    )


def regional_groups(request):

    groups = Group.objects.filter(type__name='ain7-regional')
    text = Text.objects.get(textblock__shortname='groupes_regionaux')

    return render(request, 'pages/regional_groups.html', {
        'text': text,
        'groups': groups,
        }
    )
