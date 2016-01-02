# -*- coding: utf-8
"""
 ain7/pages/tests.py
"""
#
#   Copyright © 2007-2016 AIn7 Devel Team
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

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from ain7.annuaire.models import Person
from ain7.groups.models import Group


class TestLogin(TestCase):

    def setUp(self):
        user = User.objects.create_user('user', 'user@ain7.com', 'password')
        user.save()
        user.person = Person(first_name='AIn7', last_name='User')
        user.person.save()

        contrib = User.objects.create_user('contrib', 'contrib@ain7.com', 'password')
        contrib.save()
        contrib.person = Person(first_name='AIn7', last_name='Contrib')
        contrib.person.save()

        group = Group(name='ain7-contributeur')
        group.save()
        group.add(contrib.person)


    def test_homepage(self):
        "access to the homepage"

        response = self.client.get(reverse('ain7.pages.views.homepage'))
        self.assertEqual(response.status_code, 200)

    def test_lostpassword(self):
        "access to the lostpassword page"

        response = self.client.get(reverse('ain7.pages.views.lostpassword'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('ain7.pages.views.lostpassword'),
            {'email': 'user@ain7.com'})
        self.assertEqual(response.status_code, 200)

    def test_changepassword(self):
        "access to the changepassword page"
        response = self.client.get(reverse('ain7.pages.views.lostpassword'), 
            args=['abcd1234'])
        self.assertEqual(response.status_code, 200)

    def test_apropos(self):
        "access to apropos"
        response = self.client.get(reverse('ain7.pages.views.apropos'))
        self.assertEqual(response.status_code, 200)

    def test_web(self):
        "access to web"
        response = self.client.get(reverse('ain7.pages.views.web'))
        self.assertEqual(response.status_code, 200)

    def test_legal(self):
        "access to legal"
        response = self.client.get(reverse('ain7.pages.views.mentions_legales'))
        self.assertEqual(response.status_code, 200)

    def test_relations(self):
        "access to web"
        response = self.client.get(reverse(\
            'ain7.pages.views.relations_ecole_etudiants'))
        self.assertEqual(response.status_code, 200)

    def test_rss(self):
        "access to the rss feed page"
        response = self.client.get(reverse('ain7.pages.views.rss'))
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        "login to the portal"
        response = self.client.put(reverse('ain7.pages.views.login'), 
             {'login': 'user', 'password': 'password'})
        self.assertEqual(response.status_code, 200)
        print self.client.session

    def test_edit_page(self):
        "try to edit a page"

        from ain7.pages.models import Text, TextBlock
        tn = TextBlock.objects.create(shortname='test', url='/')
        t = Text.objects.create(title='Title', body='Wonderfull text body', textblock=tn)
        t.save()

        response = self.client.get(reverse('ain7.pages.views.edit', 
             args=[t.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/edit/'+str(t.id)+'/', status_code=302)

        self.client.login(username='user', password='password')
        response = self.client.get(reverse('ain7.pages.views.edit', args=[t.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, u'Vous n\'êtes pas autorisé')

        self.client.login(username='contrib', password='password')
        response = self.client.get(reverse('ain7.pages.views.edit', args=[t.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Title')
        self.assertContains(response, 'Wonderfull text body')

    def test_sitemap(self):
        "access to sitemap"
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)

