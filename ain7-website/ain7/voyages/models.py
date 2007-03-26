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
from ain7.annuaire.models import Personne

class Voyage(models.Model):

#    label = models.CharField(maxlength=20)
    date_debut = models.DateField()
    date_fin = models.DateField()
    date = models.CharField(maxlength=30)
    description = models.TextField()
    vignette = models.ImageField(upload_to='data',blank=True,null=True)
    compte_rendu = models.TextField()

class Inscription(models.Model):

    personne = models.ForeignKey(Personne)
    voyage = models.ForeignKey(Voyage)
    nombre_de_personnes = models.IntegerField()
    commentaire = models.TextField()

