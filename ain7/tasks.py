# -*- coding: utf-8 -*-

#
# Copyright © 2015 AIn7 Devel Team <ain7-devel@lists.ain7.info>
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

from ain7.emploi.models import JobOffer
from ain7.manage.models import Mailing


@shared_task
def expire_job_offers():

    expiration_date = datetime.datetime.now()+datetime.timedelta(days=-90)

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
