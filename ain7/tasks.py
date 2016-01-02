# -*- coding: utf-8 -*-

#
# Copyright © 2015-2016 AIn7 Devel Team <ain7-devel@lists.ain7.info>
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
from django.utils import timezone

from ain7.annuaire.models import AIn7Member
from ain7.emploi.models import JobOffer
from ain7.groups.models import Group
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

    today = timezone.now().date()
    members = Group.objects.get(name=settings.AIN7_MEMBERS)
    members_list = members.active_members()

    for member in AIn7Member.objects.all():
        if member.is_subscriber():
            if member.person not in members_list:
                logging.info('Adding %s to %s' % (member.person, settings.AIN7_MEMBERS))
                print ('Adding %s to %s' % (member.person, settings.AIN7_MEMBERS))
                members.add(member.person)
        elif member.person in members_list:
            logging.info('Removing %s from %s' % (member.person, settings.AIN7_MEMBERS))
            print ('Removing %s from %s' % (member.person, settings.AIN7_MEMBERS))
            members.remove(member.person)
