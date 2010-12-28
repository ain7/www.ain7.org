# -*- coding: utf-8
"""
 ain7/manage/models.py
"""
#
#   Copyright © 2007-2011 AIn7 Devel Team
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
from django.contrib.auth.models import User


class PortalError(models.Model):
    """portal error"""

    title = models.CharField(verbose_name=_('title'), max_length=200, 
        null=True, blank=True)
    user = models.ForeignKey(User, verbose_name=_('user'), 
        blank=True, null=True)
    date = models.DateTimeField(verbose_name=_('Date'))
    url = models.CharField(verbose_name=_('url'), max_length=500)
    referer = models.CharField(verbose_name=_('Referrer'), max_length=200,
        null=True, blank=True)
    browser_info = models.CharField(verbose_name=_('Browser info'), 
        max_length=200, null=True, blank=True)
    client_address = models.CharField(verbose_name=_('Client address'), 
        max_length=200, null=True, blank=True)
    exception = models.TextField(verbose_name=_('Exception'))
    comment = models.TextField(verbose_name=_('Comment'), null=True, blank=True)
    issue = models.CharField(verbose_name=_('Issue'), max_length=20, 
        null=True, blank=True)
    fixed = models.BooleanField(verbose_name=_('fixed'), default=False)


class Filter(models.Model):
    """Filter"""

    from ain7.filters import FILTERS

    label = models.CharField(max_length=20)
    description = models.CharField(max_length=200)
    filter = models.IntegerField(verbose_name=_('filter'),
        choices=FILTERS, default=0)

    def __unicode__(self):
        """return unicode string for Filter object"""
        return self.label

class Mailing(models.Model):
    """Mailing model"""

    title = models.CharField(max_length=500)
    description = models.CharField(max_length=500, null=True, blank=True)
    toc = models.BooleanField(verbose_name=_('Table of contents'),
        default=False)

    mail_to = models.ForeignKey('manage.Filter', verbose_name=_('Mail to'))

    introduction = models.TextField(blank=True, null=True)

    approved_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey('annuaire.Person',
        related_name="mailing_approved", null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('annuaire.Person', 
        related_name="mailing_created", null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey('annuaire.Person', 
        related_name="mailing_modified", null=True, blank=True)

    def __unicode__(self):
        """return unicode string for Mailing object"""
        return self.title

    def build_html_body(self):
        """build html body for a mailing"""

        from ain7.news.models import NewsItem

        body = ""
        body += open(settings.BASE_DIR+'/templates/manage/mailing_header.html')\
            .read().decode('utf-8')

        newsitems = NewsItem.objects.filter(mailingitem__mailing=self)

        body += self.introduction

        if self.toc:
            body += "<ul>"
            for item in newsitems:
                body += '<li><a href="#'+item.slug+'">'+item.title+'</a></li>'
            body += "</ul>"

        for item in newsitems:
            body += '<h2><a name="'+item.slug+'"/><a href="http://ain7.com'\
                +item.get_absolute_url()+'">'+item.title+'</a></h2>'
            body += item.body
            body = body.replace('<a href="../', '<a href="http://ain7.com'+\
                item.get_absolute_url()+'../')

        body += open(settings.BASE_DIR+'/templates/manage/mailing_footer.html')\
           .read().decode('utf-8')

        body = body.replace('||TITLE||', self.title)

        return body

    def send(self, testing=True, myself=True, request=None):
        """send mailing or test mailing"""

        import smtplib

        from django.db.models import permalink
        from django.core.urlresolvers import reverse
        from email.header import make_header
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        from ain7.annuaire.models import Person
        from ain7.filters_local import FILTERS


        url = reverse('ain7.manage.views.mailing_preview', args=[self.id])
        text = u"Si vous n'arrivez pas à voir ce mail correctement, merci de\
 vous\nrendre à l'URL "+url+u"\n\nL'équipe de l'AIn7"

        html = self.build_html_body()

        part1 = MIMEText(text.encode('utf-8'), 'plain', 'utf-8')
        part1.set_charset('utf-8')
        part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
        part2.set_charset('utf-8')

        msg = MIMEMultipart('alternative')
        title = self.title
        if testing:
            title = '[TEST] '+title
        msg['Subject'] = str(make_header([(title, 'utf-8')]))
        msg['Sender'] = u'bounces@ain7.com'
        msg['Presence'] = u'Bulk'
        msg['X-AIn7-Portal-Message-Rationale'] = u'Subscriber'
        msg.attach(part1)

        msg.attach(part2)

        recipients = Person.objects.none()

        if request:
            recipients = Person.objects.filter(user__id=request.user.id)

        if testing and not myself:
            recipients = Person.objects.filter(\
                groups__group__slug='ain7-mailing-tester')

        if not testing:
            recipients = Person.objects.filter(FILTERS[self.filter.filter][1])

        smtp = smtplib.SMTP('localhost')
        smtp.ehlo()

        for recipient in recipients:

            mail = recipient.mail_favorite()
            first_name = recipient.first_name
            last_name = recipient.last_name

            mail_modified = mail.replace('@','=')

            del(msg['From'])
            msg['From'] = u'Association AIn7 <noreply+'+\
                mail_modified+'@ain7.com>'
            del(msg['To'])
            msg['To'] = first_name+' '+last_name+' <'+mail+'>'

            try:
                smtp.sendmail('noreply+'+mail_modified+'@ain7.com', mail, 
                    msg.as_string())

                mailingrecipient = MailingRecipient()
                mailingrecipient.person = recipient
                mailingrecipient.mailing = self
                mailingrecipient.testing = True
                if not testing:
                    mailingrecipient.testing = False
                mailingrecipient.save()

            except Exception:
                pass

        smtp.quit()

        if not testing:
            self.sent_at = datetime.datetime.now()
            self.save()

    def nomail_export(self):

        from ain7.annuaire.models import Person
        from ain7.filters_local import FILTERS

        return Person.objects.filter(FILTERS[self.mail_to.filter][1], 
            emails__isnull=True, addresses__isnull=False)


class MailingItem(models.Model):
    """Mailing Item model"""

    mailing = models.ForeignKey('manage.Mailing')
    newsitem = models.ForeignKey('news.NewsItem')

class MailingRecipient(models.Model):
    """Mailing Recipient"""

    person = models.ForeignKey('annuaire.Person')
    mailing = models.ForeignKey('manage.mailing')
    testing = models.BooleanField(default=False)

