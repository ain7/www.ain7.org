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

class Evenement(models.Model):

    nom = models.CharField(maxlength=20)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    description = models.TextField()
    auteur = models.CharField(maxlength=20)
    mail_de_contact = models.CharField(maxlength=50)
    lien = models.CharField(maxlength=60)
    lieu = models.CharField(maxlength=60)
    date_debut_publication =  models.DateTimeField()
    date_fin_publication = models.DateTimeField()

    date_creation = models.DateTimeField()
    date_modification = models.DateTimeField()
    created_by = models.ForeignKey(Personne, related_name='creator')
    modified_by = models.ForeignKey(Personne, related_name='modifier')

class InscriptionEvenement(models.Model):

    personne = models.ForeignKey(Personne)
    evenement = models.ForeignKey(Evenement)
    date_inscription = models.DateTimeField()
    nombre_de_personnes = models.IntegerField()

