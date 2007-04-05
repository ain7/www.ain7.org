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

import datetime

from django.db import models

class Actualite(models.Model):

    titre = models.CharField(maxlength=100)
    description = models.TextField()
    image = models.ImageField(upload_to='data',null=True,blank=True)

    date_creation = models.DateTimeField()
    date_modification = models.DateTimeField()

    def __str__(self):
        return self.titre

    def save(self):
        if not self.date_creation:
             self.date_creation = datetime.date.today()
        self.date_modification = datetime.datetime.today()
	self.modifie_par = 1
        return super(Actualite, self).save()

    class Admin:
        list_display = ('titre','description')

