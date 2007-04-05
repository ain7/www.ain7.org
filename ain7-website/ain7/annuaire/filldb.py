# -*- coding: utf-8
#
# filldb.py
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

from datetime import date

from django.core import validators
from django.contrib.auth.models import User

import ain7.annuaire.models as annuaire
import ain7.groupes.models as groupes
import ain7.sondages.models as sondages
import ain7.news.models as news
import ain7.voyages.models as voyages

import sys

def filldb():
    lionel = annuaire.Personne()
    lionel.user = User.objects.create_user("lionel", "lionel@ain7.org","lionel")
    lionel.user.is_staff = True
    lionel.user.is_superuser = True
    lionel.user.save()
    lionel.prenom = "Lionel"
    lionel.nom = "Porcheron"
    lionel.filiere = 1
    lionel.promo = 2003
    lionel.date_naissance = date(1978,11,18)
    lionel.nationalite = 62
    lionel.surnom = "Yoyo"
    lionel.blog = "http://www.porcheron.info"
    lionel.blog_agrege_sur_le_planet = True
    lionel.save()

    lionel_adresse = annuaire.Adresse()
    lionel_adresse.personne = lionel
    lionel_adresse.rue = "2 rue Charles Camichel"
    lionel_adresse.code_postal = "31000"
    lionel_adresse.ville = "Toulouse"
    lionel_adresse.pays = "France"
    lionel_adresse.type = 0
    lionel_adresse.save()

    lionel_couriel = annuaire.Couriel()
    lionel_couriel.personne = lionel
    lionel_couriel.adresse = "lionel@ain7.org"
    lionel_couriel.type = 0
    lionel_couriel.save()

    lionel_messagerie1 = annuaire.Messagerie()
    lionel_messagerie1.personne = lionel
    lionel_messagerie1.type_im = 5
    lionel_messagerie1.valeur = "lionel@ain7.org"
    lionel_messagerie1.save()    

    lionel_messagerie2 = annuaire.Messagerie()
    lionel_messagerie2.personne = lionel
    lionel_messagerie2.type_im = 1
    lionel_messagerie2.valeur = "12345"
    lionel_messagerie2.save()    
    
    lionel_messagerie3 = annuaire.Messagerie()
    lionel_messagerie3.personne = lionel
    lionel_messagerie3.type_im = 2
    lionel_messagerie3.valeur = "lionel@ain7.org"
    lionel_messagerie3.save()    
    
    lionel_irc1 = annuaire.IRC()
    lionel_irc1.personne = lionel
    lionel_irc1.reseau = "irc.rezosup.net"
    lionel_irc1.nick = "lionel"
    lionel_irc1.canaux = "#ain7, #inp-net, #net7, #n7"
    lionel_irc1.save()    

    lionel_irc2 = annuaire.IRC()
    lionel_irc2.personne = lionel
    lionel_irc2.reseau = "irc.freenode.net"
    lionel_irc2.nick = "lionel"
    lionel_irc2.canaux = "#hive, #ubuntu-motu, #ubuntu-server"
    lionel_irc2.save()    

    lionel_position1 = annuaire.Position()
    lionel_position1.personne = lionel
    lionel_position1.titre = "Titre 1 !"
    lionel_position1.societe = "Societe"
    lionel_position1.debut = date(2003,06,01)
    lionel_position1.fin = date(2004,06,01)
    lionel_position1.organisation_activite = 6
    lionel_position1.organisation_type = 2
    lionel_position1.organisation_taille = 3
    lionel_position1.description = "Très occupé"
    lionel_position1.save()

    lionel_position2 = annuaire.Position()
    lionel_position2.personne = lionel
    lionel_position2.titre = "Titre 2 !"
    lionel_position2.societe = "Societe 2"
    lionel_position2.debut = date(2004,06,01)
    lionel_position2.organisation_activite = 6
    lionel_position2.organisation_type = 2
    lionel_position2.organisation_taille = 3
    lionel_position2.description = "Très occupé aussi !"
    lionel_position2.save()

    pierref = annuaire.Personne()
    pierref.user = User.objects.create_user("pierref", "pierre.fersing@inp-net.eu.org","pierref")
    pierref.user.is_staff = True
    pierref.user.is_superuser = True
    pierref.user.save()
    pierref.prenom = "Pierre"
    pierref.nom = "Fersing"
    pierref.filiere = 1
    pierref.promo = 2008
    pierref.date_naissance = date(1985,11,05)
    pierref.nationalite = 62
    pierref.surnom = "PierreF"
    pierref.save()

    pierref_adresse = annuaire.Adresse()
    pierref_adresse.personne = pierref
    pierref_adresse.rue = "2 rue Charles Camichel"
    pierref_adresse.code_postal = "31000"
    pierref_adresse.ville = "Toulouse"
    pierref_adresse.pays = "France"
    pierref_adresse.type = 0
    pierref_adresse.save()

    pierref_irc1 = annuaire.IRC()
    pierref_irc1.personne = pierref
    pierref_irc1.reseau = "irc.rezosup.net"
    pierref_irc1.nick = "pierref"
    pierref_irc1.canaux = "#ain7, #inp-net, #n7, #net7"
    pierref_irc1.save()    

    olivier = annuaire.Personne()
    olivier.user = User.objects.create_user("gauwino", "olivier.gauwin@laposte.net","gauwino")
    olivier.user.is_staff = True
    olivier.user.is_superuser = True
    olivier.user.save()
    olivier.prenom = "Olivier"
    olivier.nom = "Gauwin"
    olivier.filiere = 1
    olivier.promo = 2003
    olivier.nationalite = 62
    olivier.save()

    olivier_adresse = annuaire.Adresse()
    olivier_adresse.personne = olivier
    olivier_adresse.rue = "2 rue Charles Camichel"
    olivier_adresse.code_postal = "31000"
    olivier_adresse.ville = "Toulouse"
    olivier_adresse.pays = "France"
    olivier_adresse.type = 0
    olivier_adresse.save()

    olivier_irc1 = annuaire.IRC()
    olivier_irc1.personne = olivier
    olivier_irc1.reseau = "irc.rezosup.net"
    olivier_irc1.nick = "gauwino"
    olivier_irc1.canaux = "#ain7"
    olivier_irc1.save()    

    olivier_position1 = annuaire.Position()
    olivier_position1.personne = olivier
    olivier_position1.titre = "Titre 1 !"
    olivier_position1.societe = "Societe"
    olivier_position1.debut = date(2003,06,01)
    olivier_position1.fin = date(2005,06,01)
    olivier_position1.organisation_activite = 6
    olivier_position1.organisation_type = 2
    olivier_position1.organisation_taille = 3
    olivier_position1.description = "Très occupé"
    olivier_position1.save()

    olivier_position2 = annuaire.Position()
    olivier_position2.personne = olivier
    olivier_position2.titre = "Titre 2 !"
    olivier_position2.societe = "Societe 2"
    olivier_position2.debut = date(2005,06,01)
    olivier_position2.organisation_activite = 6
    olivier_position2.organisation_type = 2
    olivier_position2.organisation_taille = 3
    olivier_position2.description = "Très occupé aussi !"
    olivier_position2.save()

    alex = annuaire.Personne()
    alex.user = User.objects.create_user("alex", "zigouigoui.garnier@laposte.net","alex")
    alex.user.is_staff = True
    alex.user.is_superuser = True
    alex.user.save()
    alex.prenom = "Alexandre"
    alex.nom = "Garnier"
    alex.filiere = 1
    alex.promo = 2006
    alex.date_naissance = date(1984,03,20)
    alex.nationalite = 62
    alex.surnom = "Alex"
    alex.save()

    alex_adresse = annuaire.Adresse()
    alex_adresse.personne = alex
    alex_adresse.rue = "2 rue Charles Camichel"
    alex_adresse.code_postal = "31000"
    alex_adresse.ville = "Toulouse"
    alex_adresse.pays = "France"
    alex_adresse.type = 0
    alex_adresse.save()

    alex_position1 = annuaire.Position()
    alex_position1.personne = alex
    alex_position1.titre = "Titre !"
    alex_position1.societe = "Societe"
    alex_position1.debut = date(2005,06,01)
    alex_position1.organisation_activite = 6
    alex_position1.organisation_type = 2
    alex_position1.organisation_taille = 3
    alex_position1.description = "Très occupé aussi !"
    alex_position1.save()

    tvn7 = annuaire.Club()
    tvn7.nom = "TVn7"
    tvn7.description = "Le club vidéo de l'N7"
    tvn7.url = "http://www.tvn7.tv"
    tvn7.mail = "tvn7@lists.bde.enseeiht.fr"
    tvn7.date_creation = date(1992,01,01)
    tvn7.etablissement = 0
    tvn7.save()

    tvn7_lionel = annuaire.MembreClub()
    tvn7_lionel.club = tvn7
    tvn7_lionel.personne = lionel
    tvn7_lionel.save()

    tvn7_alex = annuaire.MembreClub()
    tvn7_alex.club = tvn7
    tvn7_alex.personne = alex
    tvn7_alex.position = "Secrétaire 2004-2005"
    tvn7_alex.save()

    net7 = annuaire.Club()
    net7.nom = "Net7"
    net7.description = "Le club informatique et réseau de l'N7"
    net7.url = "http://www.bde.enseeiht.fr"
    net7.mail = "net7@bde.enseeiht.fr"
    net7.date_creation = date(1992,01,01)
    net7.etablissement = 0
    net7.save()

    net7_lionel = annuaire.MembreClub()
    net7_lionel.club = net7
    net7_lionel.personne = lionel
    net7_lionel.save()

    net7_pierref = annuaire.MembreClub()
    net7_pierref.club = net7
    net7_pierref.personne = pierref
    net7_pierref.save()

    inpnet = annuaire.Club()
    inpnet.nom = "INP-net"
    inpnet.description = "Le club informatique et réseau de l'INP"
    inpnet.url = "http://www.inp-net.eu.org"
    inpnet.mail = "inp-net@bde.inp-toulouse.fr"
    inpnet.date_creation = date(2002,07,01)
    inpnet.etablissement = 1
    inpnet.save()

    inpnet_lionel = annuaire.MembreClub()
    inpnet_lionel.club = inpnet
    inpnet_lionel.personne = lionel
    inpnet_lionel.position = "Président 2002-2003 - Cofondateur du club"
    inpnet_lionel.save()

    inpnet_pierref = annuaire.MembreClub()
    inpnet_pierref.club = inpnet
    inpnet_pierref.personne = pierref
    inpnet_pierref.position = "Président 2006-2007"
    inpnet_pierref.save()

    ain7etudiants = groupes.Groupe()
    ain7etudiants.nom = "AIn7 Étudiants"
    ain7etudiants.responsable = lionel
    ain7etudiants.save()
    
    ain7etudiants_lionel = groupes.Membre()
    ain7etudiants_lionel.groupe = ain7etudiants
    ain7etudiants_lionel.membre = lionel
    ain7etudiants_lionel.save()

    ain7ecole = groupes.Groupe()
    ain7ecole.nom = "AIn7 École"
    ain7ecole.responsable = lionel
    ain7ecole.save()

    ain7entreprises = groupes.Groupe()
    ain7entreprises.nom = "AIn7 Entreprises"
    ain7entreprises.responsable = lionel
    ain7entreprises.save()

    ain7entreprisesemploi = groupes.Groupe()
    ain7entreprisesemploi.nom = "AIn7 Entreprises - Emplois Carrières"
    ain7entreprisesemploi.responsable = lionel
    ain7entreprisesemploi.save()

    ain7evenementiel = groupes.Groupe()
    ain7evenementiel.nom = "Événementiel"
    ain7evenementiel.responsable = lionel
    ain7evenementiel.save()

    groupesregionauxinter = groupes.Groupe()
    groupesregionauxinter.nom = "Groupes régionaux et international"
    groupesregionauxinter.responsable = lionel
    groupesregionauxinter.save()

    mediacomcanal = groupes.Groupe()
    mediacomcanal.nom = "Médias et Communications - Canal N7"
    mediacomcanal.responsable = lionel
    mediacomcanal.save()

    mediacomweb = groupes.Groupe()
    mediacomweb.nom = "Médias et Communications - Serveur Web / Internet"
    mediacomweb.responsable = lionel
    mediacomweb.save()

    mediacomannuaire = groupes.Groupe()
    mediacomannuaire.nom = "Médias et Communications - Annuaire"
    mediacomannuaire.responsable = lionel
    mediacomannuaire.save()

    relationscnisf = groupes.Groupe()
    relationscnisf.nom = "Relations avec le CNISF et les URIS"
    relationscnisf.responsable = lionel
    relationscnisf.save()

    ain7voyages = groupes.Groupe()
    ain7voyages.nom = "Relations avec le CNISF et les URIS"
    ain7voyages.responsable = lionel
    ain7voyages.save()

    sondage1 = sondages.Sondage()
    sondage1.question = "Quelle est votre couleur préférée ?"
    sondage1.date_publication = date(2007,04,05)
    sondage1.en_ligne = True
    sondage1.save()

    sondage1_choix1 = sondages.Choix()
    sondage1_choix1.sondage = sondage1
    sondage1_choix1.choix = "Bleu"
    sondage1_choix1.save()

    sondage1_choix2 = sondages.Choix()
    sondage1_choix2.sondage = sondage1
    sondage1_choix2.choix = "Vert"
    sondage1_choix2.save()

    sondage1_choix3 = sondages.Choix()
    sondage1_choix3.sondage = sondage1
    sondage1_choix3.choix = "Rouge"
    sondage1_choix3.save()

    news1 = news.Actualite()
    news1.titre = "Nouveau portail Web"
    news1.description = """L'AIn7 travaille actuellement sur l'élaboration d'un 
    nouveau portail. N'hésitez pas à apporter vos idées et vos commentaires."""
    news1.save()

    news2 = news.Actualite()
    news2.titre = "100 ans !"
    news2.description = """L'n7 fête cette année ces 100 ans et va  tout au
    long de l'année 2007 célébrer à travers différentes manifestations cet anniversaire"""
    news2.save()

    voyage1 = voyages.Voyage()
    voyage1.libelle = "Varsovie & croisière sur la Vistule"
    voyage1.date = "Juin 2007"
    voyage1.duree = 14
    voyage1.type_voyage = 2
    voyage1.lieux_visites = "de Gdansk à Kaliningrad"
    voyage1.prix = 2350
    voyage1.save()

    voyage2 = voyages.Voyage()
    voyage2.libelle = "Japon"
    voyage2.date = "Octobre 2007"
    voyage2.duree = 13
    voyage2.type_voyage = 0
    voyage2.lieux_visites = "Tokyo, Atami, Kyoto, Hiroshima, Nara, Osazka"
    voyage2.prix = 3890
    voyage2.save()

    voyage3 = voyages.Voyage()
    voyage3.libelle = "Birmanie"
    voyage3.date = "Février 2008"
    voyage3.type_voyage = 2
    voyage3.lieux_visites = "Ragoon, Pagan, Sagain, Mandalay"
    voyage3.prix = 3550
    voyage3.save()

    voyage4 = voyages.Voyage()
    voyage4.libelle = "Mongolie/ Pékin"
    voyage4.date = "Juin 2008"
    voyage4.duree = 15
    voyage4.type_voyage = 1
    voyage4.prix = 2760
    voyage4.save()

    voyage5 = voyages.Voyage()
    voyage5.libelle = "Inde - Penjab & Himachal Pradesh"
    voyage5.date = "Octobre 2008"
    voyage5.duree = 16
    voyage5.type_voyage = 1
    voyage5.lieux_visites = "Delhi, Amristar, Dharamsala, Manali, Simla"
    voyage5.prix = 1900
    voyage5.save()

