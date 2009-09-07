# -*- coding: utf-8
#
# pages/views.py
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

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from ain7.annuaire.models import AIn7Member, Email, Person
from ain7.news.models import NewsItem
from ain7.pages.forms import LostPasswordForm, TextForm, ChangePasswordForm
from ain7.pages.models import Text, LostPassword
from ain7.sondages.models import Survey
from ain7.utils import ain7_render_to_response, check_access


def homepage(request):
    news = NewsItem.objects.all().order_by('-creation_date')[:2]
    is_auth = request.user.is_authenticated()
    surveys = [(s, (is_auth and s.has_been_voted_by(request.user.person)))\
               for s in Survey.objects.all() if s.is_valid()][:2]
    today = datetime.datetime.today()
    birthdays = []
    text1 = Text.objects.get(textblock__shortname='edito')
    text2 = Text.objects.get(textblock__shortname='enseeiht')
    if is_auth:
        birthdays = [ m for m in AIn7Member.objects.filter(
            person__birth_date__isnull=False,
            person__birth_date__day=today.day,
            person__birth_date__month=today.month,
            person__death_date=None) ]
        birthdays.sort(lambda x,y: cmp(x.person.last_name,y.person.last_name))
    return ain7_render_to_response(request, 'pages/homepage.html', 
        {'news': news , 'surveys': surveys, 'birthdays': birthdays, 
         'text1': text1, 'text2': text2})

def lostpassword(request):

    messages = request.session.setdefault('messages', [])
    form = LostPasswordForm()
    if request.method == 'GET':
        return ain7_render_to_response(request, 'pages/lostpassword.html', {'form': form})
    if request.method == 'POST':
        form = LostPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            person = Email.objects.get(email=email).person
            lostpw = LostPassword()
            lostpw.key = User.objects.make_random_password(50)
            lostpw.person = person
            lostpw.save()

            url = 'http://%s%s' % (request.get_host(), lostpw.get_absolute_url())
            person.send_mail(_('Login Service: Forgotten Password'), \
                        _("""Hi,

You, or someone posing as you, has requested a new password for your AIn7 account.

To change your password to a new one, please follow this link:
 %s

Note: if you did not make this request, you can safely ignore this email.
-- 
http://ain7.com""") % url)
            info = _('We have sent you an email with instructions to reset your password.')
            request.path = '/'
            return ain7_render_to_response(request, 'pages/lostpassword.html', {'info': info})
        else:
            info = _('If you are claiming an existing account but don\'t know the email address that was used, please contact an AIn7 administrator.')
            return ain7_render_to_response(request, 'pages/lostpassword.html', {'form': form, 'info': info})

def changepassword(request, key):
    form = ChangePasswordForm()

    lostpw = get_object_or_404(LostPassword, key=key)

    if lostpw.is_expired():
        lostpw.delete()
        info = _('Page expired, please request a new key')
        return ain7_render_to_response(request, 'pages/changepassword.html', {'info': info})

    if request.POST:
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            person = lostpw.person
            lostpw.delete()
            person.user.set_password(form.cleaned_data['password'])
            person.user.save() # appel explicite de .save pour changer le mot de passe de façon permanente
            info = _('Successfully changed password')
            return ain7_render_to_response(request, 'pages/changepassword.html', {'person': person, 'info': info})

    return ain7_render_to_response(request, 'pages/changepassword.html', {'form': form, 'person': lostpw.person})


def apropos(request):
    return ain7_render_to_response(request, 'pages/apropos.html', {})

def international(request):
    text = Text.objects.get(pk=17)
    return ain7_render_to_response(request, 'pages/international.html', 
                       {'text': text})

def mentions_legales(request):
    return ain7_render_to_response(request, 'pages/mentions_legales.html', {})

def rss(request):
    return ain7_render_to_response(request, 'pages/rss.html', {})

def edit(request, text_id):

    r = check_access(request, request.user, ['ain7-member', 
                                       'ain7-secretariat', 'contributeur'])
    if r:
        return r

    text = get_object_or_404(Text, pk=text_id)

    form = TextForm(initial={'title': text.title, 'body': text.body})

    if request.method == 'POST':
        form = TextForm(request.POST)
        if form.is_valid():
           text.title = form.cleaned_data['title']
           text.body = form.cleaned_data['body']
           text.save()

           request.user.message_set.create(message=_("Modifications saved."))
           return HttpResponseRedirect(text.textblock.url)

    return ain7_render_to_response(request, 'pages/text_edit.html', 
            {'text_id': text_id, 'form': form, 'back': request.META.get('HTTP_REFERER')})

