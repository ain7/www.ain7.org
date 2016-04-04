# -*- coding: utf-8
"""
 ain7/annuaire/management.py
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

from django.apps import AppConfig
from django.db.models import signals


def filldb(sender, **kwargs):
    """filling the database with demo datas"""

    from ain7 import filldb

    if kwargs.get('interactive', True):
        msg = "\nYou just installed AIn7 portal, which means you don't have " \
            "any data defined.\nWould you like to fill your db now? (yes/no): "
        confirm = raw_input(msg)
        while 1:
            if confirm not in ('yes', 'no'):
                confirm = raw_input('Please enter either "yes" or "no": ')
                continue
            if confirm == 'yes':
                filldb.filldb()
            break


class FillDb(AppConfig):
    name = "ain7.annuaire"

    def ready(self):
        signals.post_migrate.connect(filldb, sender=self)
