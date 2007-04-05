# -*- coding: utf-8
#
# models.py
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

from django.db import models

class Sondage(models.Model):
    question = models.CharField(maxlength=200)
    date_publication = models.DateTimeField('date publication')
    en_ligne = models.BooleanField()

    def __str__():
	return question

    class Admin:
	list_display = ('question', 'date_publication')

class Choix(models.Model):
    sondage = models.ForeignKey(Sondage, edit_inline=models.STACKED, num_in_admin=3)
    choix = models.CharField(maxlength=200, core=True)
    votes = models.IntegerField(default=0, editable=False)

