# -*- coding: utf-8 -*-

#
# Copyright © 2015-2017 AIn7 Devel Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of version 3 of the GNU General Public License as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import absolute_import

import datetime
import logging
import os

from celery import shared_task

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from email.mime.image import MIMEImage

from ain7.adhesions.models import Subscription, SubscriptionKey
from ain7.annuaire.models import AIn7Member
from ain7.emploi.models import JobOffer
from ain7.groups.models import Group, Member
from ain7.manage.models import Mailing


@shared_task
def expire_job_offers():

    expiration_date = datetime.datetime.now()+datetime.timedelta(days=-120)

    for job in JobOffer.objects.filter(
            modified_at__lt=expiration_date,
            obsolete=False,
            ):
        job.mark_obsolete()
        logging.info("Mark as obsolete %s (id=%s)" % (job.title, job.id))


@shared_task
def mailing_send():

    for mailing in Mailing.objects.filter(
            approved_at__isnull=False,
            approved_by__isnull=False,
            sent_at__isnull=True,
            mail_to__isnull=False,
            ):
        mailing.send(False)


@shared_task
def refresh_membership():

    members = Group.objects.get(name=settings.AIN7_MEMBERS)

    Member.objects.filter(group=members).delete()

    for member in AIn7Member.objects.all():
        if member.person.is_subscriber:
            members.add(member.person)


@shared_task
def notify_expiring_membership():

    today = timezone.now().date()
    in_seven_days = today + datetime.timedelta(days=7)
    in_thirty_days = today + datetime.timedelta(days=30)
    twenty_days_ago = today + datetime.timedelta(days=-20)

    subscriptions = Subscription.objects.filter(
        Q(end_date=in_thirty_days) | Q(end_date=in_seven_days) |
        Q(end_date=today) | Q(end_date=twenty_days_ago)
    ).distinct().exclude(member__person__emails__isnull=True).exclude(validated=False)
    for sub in subscriptions:
        if not sub.member.has_subscription_next():
            try:
                sub.member.notify_expiring_membership()
            except:
                pass

@shared_task
def notify_staff_membership_operations():

    import locale
    try:
        locale.setlocale(locale.LC_TIME,'fr_FR.UTF-8')
    except Exception:
        pass

    now = timezone.now()
    seven_days_ago = now - datetime.timedelta(days=7)

    notified_members = SubscriptionKey.objects.filter(created_at__gte=seven_days_ago).distinct()
    expired_members = Subscription.objects.filter(validated=True, end_date__gte=seven_days_ago, end_date__lte=now.date()).distinct()
    renew_members = Subscription.objects.filter(validated=True, date__gte=seven_days_ago.date()).distinct()

    subject = u'Adhésions AIn7: activité de la semaine du '+seven_days_ago.strftime("%d %B %Y")
    html_content = render_to_string(
        'emails/notification_staff_subscriptions_operations.html', {
        'notified_members': notified_members,
        'expired_members': expired_members,
        'renew_members': renew_members,
        'settings': settings,
    })

    text_content = render_to_string(
        'emails/notification_staff_subscriptions_operations.txt', {
        'notified_members': notified_members,
        'expired_members': expired_members,
        'renew_members': renew_members,
        'settings': settings,
    })
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        'AIn7 Adhesions <adhesions@ain7.com>',
        ['adhesions@ain7.com'],
    )

    msg.mixed_subtype = 'related'

    for img in ['logo_ain7.png', 'facebook.png', 'linkedin.png', 'twitter.png', 'googleplus.png']:
        fp = open(os.path.join(os.path.dirname(__file__), 'templates/emails/img', img), 'rb')
        msg_img = MIMEImage(fp.read())
        fp.close()
        msg_img.add_header('Content-ID', '<{}>'.format(img))
        msg.attach(msg_img)

    msg.attach_alternative(html_content, "text/html")
    msg.send()

@shared_task
def update_subscription_flag():

    from ain7.annuaire.models import Person

    for p in Person.objects.all():
        try:
            p.is_subscriber = p.ain7member.is_subscriber()
            p.save()
        except Exception:
            pass

