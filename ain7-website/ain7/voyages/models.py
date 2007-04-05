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

from ain7.annuaire.models import Personne

class Voyage(models.Model):

    TYPE_VOYAGE = (
         (0,'Circuit'),
         (1,'Croisière'),
         (2,'Circuit & Croisière'),
    )

    libelle = models.CharField(maxlength=20)
    date_debut = models.DateField(blank=True, null=True)
    date_fin = models.DateField(blank=True, null=True)
    date = models.CharField(maxlength=30)
    duree = models.IntegerField(blank=True, null=True)
    type_voyage = models.IntegerField(choices=TYPE_VOYAGE)
    lieux_visites = models.CharField(maxlength=100)
    description = models.TextField()
    prix = models.IntegerField(blank=True, null=True)
    vignette = models.ImageField(upload_to='data',blank=True,null=True)
    compte_rendu = models.TextField()

    date_creation =  models.DateTimeField(editable=False)
    date_modification = models.DateTimeField(editable=False)

    def __str__(self):
        return self.libelle

    def save(self):
        if not self.date_creation:
             self.date_creation = datetime.date.today()
        self.date_modification = datetime.datetime.today()
        return super(Voyage, self).save()

    class Admin:
        pass

class Inscription(models.Model):

    personne = models.ForeignKey(Personne)
    voyage = models.ForeignKey(Voyage)
    nombre_de_personnes = models.IntegerField()
    commentaire = models.TextField()

