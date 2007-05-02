# -*- coding: utf-8
#
# annuaire/management.py
#
#   Copyright (C) 2007 AIn7
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

from django.dispatch import dispatcher
from django.db.models import signals
from ain7.annuaire import models as annuaire_app

def filldb(app, created_models, verbosity, **kwargs):
    from ain7 import filldb
    if annuaire_app.Person in created_models:
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

dispatcher.connect(filldb, sender=annuaire_app, signal=signals.post_syncdb)

