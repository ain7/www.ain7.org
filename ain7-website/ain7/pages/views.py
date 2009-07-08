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
from ain7.pages.forms import LostPasswordForm, TextForm
from ain7.pages.models import Text
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
            e = form.cleaned_data['email']
            p = Email.objects.filter(email=e).person
            new_random_password = User.objects.make_random_password(length=10, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')
            p.user.set_password(new_random_password)
            p.user.save() # appel explicite de .save pour changer le mot de passe de façon permanente
            p.send_mail(_('Login Service: Forgotten Password'), \
                        _('Hi,\n\nYou, or someone posing as you, has requested a new password for your AIn7 account.' + \
                          '\n\nYour password is now set to: ' + new_random_password + '\n\n'))
            info = _('We have sent you an email with instructions to reset your password.')
            request.path = '/'
            return ain7_render_to_response(request, 'pages/lostpassword.html', {'info': info})
        else:
            info = _('If you are claiming an existing account but don\'t know the email address that was used, please contact an AIn7 administrator.')
            return ain7_render_to_response(request, 'pages/lostpassword.html', {'form': form, 'info': info})

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
           return HttpResponseRedirect(request.META.get('HTTP_REFERER', ''))

    return ain7_render_to_response(request, 'pages/text_edit.html', 
            {'text_id': text_id, 'form': form, 'back': request.META.get('HTTP_REFERER')})

