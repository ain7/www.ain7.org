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

from ain7.annuaire.models import Person

class Travel(models.Model):

    TRAVEL_TYPE = (
         (0,'Circuit'),
         (1,'Croisière'),
         (2,'Circuit & Croisière'),
    )

    libelle = models.CharField(maxlength=20)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    date = models.CharField(maxlength=30)
    duree = models.IntegerField(blank=True, null=True)
    #travel_type = models.IntegerField(choices=TRAVEL_TYPE)
    lieux_visites = models.CharField(maxlength=100)
    description = models.TextField()
    price = models.IntegerField(blank=True, null=True)
    vignette = models.ImageField(upload_to='data',blank=True,null=True)
    compte_rendu = models.TextField()

    creation_date =  models.DateTimeField(editable=False)
    modification_date = models.DateTimeField(editable=False)

    def __str__(self):
        return self.libelle

    def save(self):
        if not self.creation_date:
             self.creation_date = datetime.date.today()
        self.modification_date = datetime.datetime.today()
        return super(Travel, self).save()

    class Admin:
        pass

class Inscription(models.Model):

    person = models.ForeignKey(Person)
    travel = models.ForeignKey(Travel)
    person_number = models.IntegerField()
    comment = models.TextField()

