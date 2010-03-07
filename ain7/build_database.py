#!/usr/bin/python
# -*- coding: utf-8
#
# build_database.py
#
#   Copyright © 2007-2010 AIn7 Devel Team
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

import os
import pexpect
import sys

import settings

confirm = 'oui'

if os.path.exists(settings.DATABASE_NAME):
    msg = "La base de donnee existe deja, voulez vous la supprimer ? "
    confirm = raw_input(msg)
    while 1:
        if confirm not in ('oui', 'non'):
            confirm = raw_input('Merci de saisir "oui" ou "non" : ')
            continue
        if confirm == 'oui':
            os.remove(settings.DATABASE_NAME)
        break

# spawn the child process
child = pexpect.spawn('python manage.py syncdb')

# log on stdout
child.logfile = sys.stdout

if confirm == 'non':
    sys.exit(0)

# Wait for the application to give us this text (a regular expression)
child.expect('Would you like to create one now.*')

# Send this line in response
child.sendline('no')

# Wait for the application to give us this text (a regular expression)
child.expect('Would you like to fill your db now.*')

# Send this line in response
child.sendline('yes')

# This means wait for the end of the child's output
child.expect(pexpect.EOF, timeout=None)

