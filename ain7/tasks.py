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

from celery import shared_task

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from ain7.adhesions.models import Subscription
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
        if member.is_subscriber():
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
    ).exclude(member__person__emails__isnull=True)
    for sub in subscriptions:
        if not sub.member.has_subscription_next():
            sub.member.notify_expiring_membership()
