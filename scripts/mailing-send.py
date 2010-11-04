#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Copyright © 2010 AIn7 Devel Team <ain7-devel@lists.ain7.info>
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

import datetime
import os
import sys
BASE_DIR = os.path.abspath(os.path.join( os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)

from django.core.management import setup_environ

from ain7 import settings
setup_environ(settings)

from ain7.manage.models import Mailing

for mailing in Mailing.objects.filter(approved_at__isnull=False, \
    approved_by__isnull=False, sent_at__isnull=True):
    mailing.send(False)

