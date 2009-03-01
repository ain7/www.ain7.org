# -*- coding: utf-8
#
# pages/views.py
#
#   Copyright (C) 2007-2008 AIn7
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
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect, HttpResponse

from ain7.news.models import NewsItem
from ain7.sondages.models import Survey
from ain7.utils import ain7_render_to_response
from ain7.annuaire.models import AIn7Member
from ain7.pages.forms import LostPasswordForm
from ain7.annuaire.models import Person, Email

def homepage(request):
    news = NewsItem.objects.all().order_by('-creation_date')[:2]
    is_auth = request.user.is_authenticated()
    surveys = [(s, (is_auth and s.has_been_voted_by(request.user.person)))\
               for s in Survey.objects.all() if s.is_valid()][:2]
    today = datetime.datetime.today()
    birthdays = []
    if is_auth:
        birthdays = [ m for m in AIn7Member.objects.filter(
            person__birth_date__day=today.day,
            person__birth_date__month=today.month,
            person__death_date=None) ]
        birthdays.sort(lambda x,y: cmp(x.person.last_name,y.person.last_name))
    return ain7_render_to_response(request, 'pages/homepage.html', 
        {'news': news , 'surveys': surveys, 'birthdays': birthdays})

def lostpassword(request):

    messages = request.session.setdefault('messages', [])
    form = LostPasswordForm()
    if request.method == 'GET':
        return ain7_render_to_response(request, 'pages/lostpassword.html', {'form': form})
    if request.method == 'POST':
        form = LostPasswordForm(request.POST)
        if form.is_valid():
            e = form.cleaned_data['email']
            p = Email.objects.get(email=e).person
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

def count_members():
    nb_members = AIn7Member.objects.all().count()
    return nb_members

def count_subscribers():
    nb_subscribers = AIn7Member.objects.all().count()
    return nb_subscribers

def association(request):
   # calcul du nombre d'AIn7Member
    return ain7_render_to_response(request, 'pages/association.html', {'count_members': count_members(), 'count_subscribers': count_subscribers()})

def status(request):
    return ain7_render_to_response(request, 'pages/status.html', {'count_members': count_members(), 'count_subscribers': count_subscribers()})

def board(request):
    return ain7_render_to_response(request, 'pages/board.html', {'count_members': count_members(), 'count_subscribers': count_subscribers()})

def council(request):
    return ain7_render_to_response(request, 'pages/council.html', {'count_members': count_members(), 'count_subscribers': count_subscribers()})

def contact(request):
    return ain7_render_to_response(request, 'pages/contact.html', {'count_members': count_members(), 'count_subscribers': count_subscribers()})

def canal_n7(request):
    return ain7_render_to_response(request, 'pages/canal_n7.html', {})

def international(request):
    return ain7_render_to_response(request, 'pages/international.html', {})

def mentions_legales(request):
    return ain7_render_to_response(request, 'pages/mentions_legales.html', {})

def publications(request):
    return ain7_render_to_response(request, 'pages/publications.html', {})

def rss(request):
    return ain7_render_to_response(request, 'pages/rss.html', {})

