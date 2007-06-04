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

from datetime import date, datetime, timedelta

from django.core import validators
from django.contrib.auth.models import User

import ain7.annuaire.models as annuaire
import ain7.groupes.models as groupes
import ain7.groupes_regionaux.models as groupes_regionaux
import ain7.sondages.models as sondages
import ain7.news.models as news
import ain7.voyages.models as voyages
import ain7.emploi.models as emploi
import ain7.evenements.models as evenements

import sys

def filldb():

    # Country
    france = annuaire.Country(name="France", nationality="Française")
    france.save()

    england = annuaire.Country(name="Angleterre", nationality="Anglaise")
    england.save()

    # Types
    activityKnown = annuaire.Activity(activity="Connue")
    activityKnown.save()

    activityRetired = annuaire.Activity(activity="Retraité")
    activityRetired.save()

    memberTypeActif = annuaire.MemberType(type="Membre actif")
    memberTypeActif.save()

    personTypeIngeneer = annuaire.PersonType(type="Ingénieur")
    personTypeIngeneer.save()

    personTypeStudent = annuaire.PersonType(type="Etudiant")
    personTypeStudent.save()

    personnalAddressType = annuaire.AddressType(type="Personnelle")
    personnalAddressType.save()

    parentalAddressType = annuaire.AddressType(type="Parentale")
    parentalAddressType.save()

    # Diplomas
    bac = annuaire.Diploma(diploma="Baccalauréat", initials="Bac")
    bac.save()

    # Decorations
    warCross = annuaire.Decoration(decoration="Croix de Guerre")
    warCross.save()

    # Decorations
    JCPrice = annuaire.CeremonialDuty(ceremonial_duty="Prix Joliot Curie")
    JCPrice.save()

    # School
    n7 = annuaire.School()
    n7.name = "Ecole national supérieure d'éléctronique, d'éléctrotechnique, d'informatique, d'hydraulique et des télécommunications"
    n7.initials = "ENSEEIHT"
    n7.save()

    n7info = annuaire.Track()
    n7info.name = "Informatique et Mathématiques Appliquées"
    n7info.initials = "IN"
    n7info.school = n7
    n7info.save()

    n7hydro = annuaire.Track()
    n7hydro.name = "Hydraulique et Mécanique des Fluides"
    n7hydro.initials = "HY"
    n7hydro.school = n7
    n7hydro.save()

    n7hy2006 = annuaire.Promo(year=2006, track=n7hydro)
    n7hy2006.save()

    n7in2006 = annuaire.Promo(year=2006, track=n7info)
    n7in2006.save()

    n7in2003 = annuaire.Promo(year=2003, track=n7info)
    n7in2003.save()
    
    n7in2008 = annuaire.Promo(year=2008, track=n7info)
    n7in2008.save()

    # Companies
    infofield = emploi.CompanyField(field = "Informatique")
    infofield.save()

    babelstore = emploi.Company(name="BABELSTORE", field=infofield, size=2)
    babelstore.save()

    priceminister = emploi.Office(name="PriceMinister", company=babelstore)
    priceminister.save()

    anyware = emploi.Company(name="Anyware", field=infofield)
    anyware.save()

    anywareoffice = emploi.Office(name="Bureau de Toulouse", company=anyware)
    anywareoffice.save()

    schtroumpfland = emploi.Company(name="Schtroumpfland", field=infofield)
    schtroumpfland.save()

    lepaysdesschtroumpfs = emploi.Office(name="Mon champignon", company=schtroumpfland)
    lepaysdesschtroumpfs.save()

    # Regional group
    idfgroup = groupes_regionaux.Group(name="Ile de France")
    idfgroup.save()

    # Person
    lionel = annuaire.Person()
    lionel.user = User.objects.create_user("lionel", "lionel@ain7.org","lionel")
    lionel.user.is_staff = True
    lionel.user.is_superuser = True
    lionel.user.save()
    lionel.activity = activityRetired
    lionel.member_type = memberTypeActif
    lionel.person_type = personTypeIngeneer
    lionel.sex = 'M'
    lionel.first_name = "Lionel"
    lionel.last_name = "Porcheron"
    lionel.promos.add(n7in2003)
    lionel.birth_date = date(1978,11,18)
    lionel.country = france
    lionel.nick_name = "Yoyo"
    lionel.blog = "http://www.porcheron.info"
    lionel.blog_agrege_sur_le_planet = True
    lionel.display_cv_in_directory = True
    lionel.receive_job_offers = False
    lionel.save()

    lionel_adresse = annuaire.Address()
    lionel_adresse.person = lionel
    lionel_adresse.number = "2"
    lionel_adresse.street = "rue Charles Camichel"
    lionel_adresse.zip_code = "31000"
    lionel_adresse.city = "Toulouse"
    lionel_adresse.country = france
    lionel_adresse.type = personnalAddressType
    lionel_adresse.save()

    lionel_couriel1 = annuaire.Email()
    lionel_couriel1.person = lionel
    lionel_couriel1.email = "lionel@ain7.org"
    lionel_couriel1.save()

    lionel_couriel2 = annuaire.Email()
    lionel_couriel2.person = lionel
    lionel_couriel2.email = "lionel@porcheron.info"
    lionel_couriel2.is_confidential = True
    lionel_couriel2.save()

    lionel_messagerie1 = annuaire.InstantMessaging()
    lionel_messagerie1.person = lionel
    lionel_messagerie1.type = 5
    lionel_messagerie1.identifier = "lionel@ain7.org"
    lionel_messagerie1.save()    

    lionel_messagerie2 = annuaire.InstantMessaging()
    lionel_messagerie2.person = lionel
    lionel_messagerie2.type = 1
    lionel_messagerie2.identifier = "12345"
    lionel_messagerie2.save()    
    
    lionel_messagerie3 = annuaire.InstantMessaging()
    lionel_messagerie3.person = lionel
    lionel_messagerie3.type = 2
    lionel_messagerie3.identifier = "lionel@ain7.org"
    lionel_messagerie3.save()    

    lionel_site = annuaire.WebSite()
    lionel_site.person = lionel
    lionel_site.url = "http://www.porcheron.info"
    lionel_site.save()

    lionel_irc1 = annuaire.IRC()
    lionel_irc1.person = lionel
    lionel_irc1.network = "irc.rezosup.net"
    lionel_irc1.pseudo = "lionel"
    lionel_irc1.channels = "#ain7, #inp-net, #net7, #n7"
    lionel_irc1.save()    

    lionel_irc2 = annuaire.IRC()
    lionel_irc2.person = lionel
    lionel_irc2.network = "irc.freenode.net"
    lionel_irc2.pseudo = "lionel"
    lionel_irc2.channels = "#hive, #ubuntu-motu, #ubuntu-server"
    lionel_irc2.save()


    lionel_position1 = emploi.Position()
    lionel_position1.person = lionel
    lionel_position1.office = anywareoffice
    lionel_position1.fonction = "AdminSys"
    lionel_position1.start_date = date(2005,01,01)
    lionel_position1.end_date = date(2007,01,01)
    lionel_position1.save()

    lionel_position2 = emploi.Position()
    lionel_position2.person = lionel
    lionel_position2.office = anywareoffice
    lionel_position2.fonction = "Big boss"
    lionel_position2.start_date = date(2007,01,01)
    lionel_position2.save()

    lionel_ain7member = annuaire.AIn7Member()
    lionel_ain7member.person = lionel
    lionel_ain7member.cvTitle = "Ingénieur ENSEEIHT Informatique"    
    lionel_ain7member.save()

    pierref = annuaire.Person()
    pierref.user = User.objects.create_user("pierref", "pierre.fersing@inp-net.eu.org","pierref")
    pierref.user.is_staff = True
    pierref.user.is_superuser = True
    pierref.user.save()
    pierref.activity = activityKnown
    pierref.member_type = memberTypeActif
    pierref.person_type = personTypeStudent
    pierref.sex = 'M'
    pierref.first_name = "Pierre"
    pierref.last_name = "Fersing"
    pierref.promos.add(n7in2008)
    pierref.birth_date = date(1985,11,05)
    pierref.country = france
    pierref.nick_name = "PierreF"
    pierref.display_cv_in_directory = False
    pierref.receive_job_offers = False
    pierref.save()

    pierref_adresse = annuaire.Address()
    pierref_adresse.person = pierref
    pierref_adresse.number = "2"
    pierref_adresse.street = "rue Charles Camichel"
    pierref_adresse.zip_code = "31000"
    pierref_adresse.city = "Toulouse"
    pierref_adresse.country = france
    pierref_adresse.type = personnalAddressType
    pierref_adresse.save()

    pierref_irc1 = annuaire.IRC()
    pierref_irc1.person = pierref
    pierref_irc1.network = "irc.rezosup.net"
    pierref_irc1.pseudo = "pierref"
    pierref_irc1.channels = "#ain7, #inp-net, #n7, #net7"
    pierref_irc1.save()    

    pierref_ain7member = annuaire.AIn7Member()
    pierref_ain7member.person = pierref
    pierref_ain7member.cvTitle = "Élève Ingénieur ENSEEIHT Informatique"
    pierref_ain7member.save()

    olivier = annuaire.Person()
    olivier.user = User.objects.create_user("gauwino", "olivier.gauwin@laposte.net","gauwino")
    olivier.user.is_staff = True
    olivier.user.is_superuser = True
    olivier.user.save()
    olivier.activity = activityKnown
    olivier.member_type = memberTypeActif
    olivier.person_type = personTypeIngeneer
    olivier.sex = 'M'
    olivier.first_name = "Olivier"
    olivier.last_name = "Gauwin"
    olivier.birth_date = date(1955,12,9)
    olivier.promos.add(n7in2003)
    olivier.country = france
    olivier.display_cv_in_directory = True
    olivier.receive_job_offers = True
    olivier.save()

    olivier_adresse = annuaire.Address()
    olivier_adresse.person = olivier
    olivier_adresse.number = "2"
    olivier_adresse.street = "rue Charles Camichel"
    olivier_adresse.zip_code = "31000"
    olivier_adresse.city = "Toulouse"
    olivier_adresse.country = france
    olivier_adresse.type = personnalAddressType
    olivier_adresse.save()

    olivier_adresse2 = annuaire.Address()
    olivier_adresse2.person = olivier
    olivier_adresse2.number = "8"
    olivier_adresse2.street = "rue de nulle part"
    olivier_adresse2.zip_code = "30001"
    olivier_adresse2.city = "Lille"
    olivier_adresse2.country = france
    olivier_adresse2.type = parentalAddressType
    olivier_adresse2.save()

    olivier_couriel1 = annuaire.Email()
    olivier_couriel1.person = olivier
    olivier_couriel1.email = "olivier@somewhere.org"
    olivier_couriel1.save()

    olivier_messagerie1 = annuaire.InstantMessaging()
    olivier_messagerie1.person = olivier
    olivier_messagerie1.type = 5
    olivier_messagerie1.identifier = "olivier@somewhere.jabber"
    olivier_messagerie1.save()    

    olivier_irc1 = annuaire.IRC()
    olivier_irc1.person = olivier
    olivier_irc1.network = "irc.rezosup.net"
    olivier_irc1.pseudo = "gauwino"
    olivier_irc1.channels = "#ain7"
    olivier_irc1.save()

    olivier_site = annuaire.WebSite()
    olivier_site.person = olivier
    olivier_site.url = "http://www.ain7.com/"
    olivier_site.save()

    olivier_bigophone1 = annuaire.PhoneNumber()
    olivier_bigophone1.person = olivier
    olivier_bigophone1.number = "0345678900"
    olivier_bigophone1.type = 1
    olivier_bigophone1.isConfidential = False
    olivier_bigophone1.save()

    olivier_bigophone2 = annuaire.PhoneNumber()
    olivier_bigophone2.person = olivier
    olivier_bigophone2.number = "0606060606"
    olivier_bigophone2.type = 3
    olivier_bigophone2.isConfidential = False
    olivier_bigophone2.save()

    olivier_ain7member = annuaire.AIn7Member()
    olivier_ain7member.person = olivier
    olivier_ain7member.cvTitle = "Ingénieur ENSEEIHT et doctorant en Informatique"    
    olivier_ain7member.save()
    
    olivier_position1 = emploi.Position()
    olivier_position1.person = olivier
    olivier_position1.office = lepaysdesschtroumpfs
    olivier_position1.fonction = "Schtroumpf paresseux"
    olivier_position1.start_date = date(2003,01,01)
    olivier_position1.end_date = date(2007,01,01)
    olivier_position1.save()

    olivier_position2 = emploi.Position()
    olivier_position2.person = olivier
    olivier_position2.office = lepaysdesschtroumpfs
    olivier_position2.fonction = "Grand Schtroumpf"
    olivier_position2.start_date = date(2007,01,01)
    olivier_position2.save()

    olivier_education1 = emploi.EducationItem()
    olivier_education1.person = olivier
    olivier_education1.school = "ENSEEIHT"
    olivier_education1.diploma = "Ingenieur en informatique et mathématiques appliquées"
    olivier_education1.details = "Troisième année à la Technische Universität Darmstadt, Allemagne."
    olivier_education1.start_date = date(2001,1,11)
    olivier_education1.end_date = date(2003,8,23)
    olivier_education1.save()

    olivier_leisure1 = emploi.LeisureItem()
    olivier_leisure1.person = olivier
    olivier_leisure1.title = "Culture"
    olivier_leisure1.detail = "Guitare, cinéma"
    olivier_leisure1.save()

    olivier_leisure2 = emploi.LeisureItem()
    olivier_leisure2.person = olivier
    olivier_leisure2.title = "Informatique"
    olivier_leisure2.detail = "Le site de l'AIn7 !!"
    olivier_leisure2.save()

    alex = annuaire.Person()
    alex.user = User.objects.create_user("alex", "zigouigoui.garnier@laposte.net","alex")
    alex.user.is_staff = True
    alex.user.is_superuser = True
    alex.user.save()
    alex.activity = activityKnown
    alex.member_type = memberTypeActif
    alex.person_type = personTypeIngeneer
    alex.sex = 'M'
    alex.first_name = "Alexandre"
    alex.last_name = "Garnier"
    alex.promos.add(n7in2006)
    alex.birth_date = date(1984,03,14)
    alex.country = france
    alex.nick_name = "Alex"
    alex.display_cv_in_directory = False
    alex.receive_job_offers = False
    alex.save()

    alex_portable = annuaire.PhoneNumber()
    alex_portable.person = alex
    alex_portable.number = "0681901082"
    alex_portable.type = 3
    alex_portable.isConfidential = False
    alex_portable.save()

    alex_adresse1 = annuaire.Address()
    alex_adresse1.person = alex
    alex_adresse1.number = "79"
    alex_adresse1.street = "rue Broca"
    alex_adresse1.zip_code = "75013"
    alex_adresse1.city = "Paris"
    alex_adresse1.country = france
    alex_adresse1.type = personnalAddressType
    alex_adresse1.save()

    alex_adresse2 = annuaire.Address()
    alex_adresse2.person = alex
    alex_adresse2.number = "70"
    alex_adresse2.street = "rue de Paris"
    alex_adresse2.zip_code = "95720"
    alex_adresse2.city = "Le Mesnil-Aubry"
    alex_adresse2.country = france
    alex_adresse2.type = parentalAddressType
    alex_adresse2.save()

    alexpos = emploi.Position()
    alexpos.person = alex
    alexpos.office = priceminister
    alexpos.fonction = "dev"
    alexpos.start_date = date(2006,8,17)
    alexpos.save()

    alex_ain7member = annuaire.AIn7Member()
    alex_ain7member.person = alex
    alex_ain7member.cvTitle = "Ingénieur ENSEEIHT Informatique"
    alex_ain7member.save()

    tvn7 = annuaire.Club()
    tvn7.name = "TVn7"
    tvn7.description = "Le club vidéo de l'N7"
    tvn7.web_site = "http://www.tvn7.fr.st"
    tvn7.email = "tvn7@lists.bde.enseeiht.fr"
    tvn7.creation_date = date(1992,01,01)
    tvn7.school = n7
    tvn7.save()

    tvn7_lionel = annuaire.ClubMembership()
    tvn7_lionel.club = tvn7
    tvn7_lionel.member = lionel
    tvn7_lionel.save()

    tvn7_alex = annuaire.ClubMembership()
    tvn7_alex.club = tvn7
    tvn7_alex.member = alex
    tvn7_alex.fonction = "Secrétaire 2004-2005"
    tvn7_alex.save()

    net7 = annuaire.Club()
    net7.name = "Net7"
    net7.description = "Le club informatique et réseau de l'N7"
    net7.web_site = "http://www.bde.enseeiht.fr"
    net7.email = "net7@bde.enseeiht.fr"
    net7.creation_date = date(1992,01,01)
    net7.school = n7
    net7.save()

    net7_lionel = annuaire.ClubMembership()
    net7_lionel.club = net7
    net7_lionel.member = lionel
    net7_lionel.save()

    net7_pierref = annuaire.ClubMembership()
    net7_pierref.club = net7
    net7_pierref.member = pierref
    net7_pierref.save()

    inpnet = annuaire.Club()
    inpnet.name = "INP-net"
    inpnet.description = "Le club informatique et réseau de l'INP"
    inpnet.web_site = "http://www.inp-net.eu.org"
    inpnet.email = "inp-net@bde.inp-toulouse.fr"
    inpnet.creation_date = date(2002,07,01)
    inpnet.school = n7
    inpnet.save()

    inpnet_lionel = annuaire.ClubMembership()
    inpnet_lionel.club = inpnet
    inpnet_lionel.member = lionel
    inpnet_lionel.fonction = "Président 2002-2003 - Cofondateur du club"
    inpnet_lionel.save()

    inpnet_pierref = annuaire.ClubMembership()
    inpnet_pierref.club = inpnet
    inpnet_pierref.member = pierref
    inpnet_pierref.fonction = "Président 2006-2007"
    inpnet_pierref.save()

    ain7etudiants = groupes.Group()
    ain7etudiants.name = "AIn7 Étudiants"
    ain7etudiants.administrator = lionel
    ain7etudiants.save()
    
    ain7etudiants_lionel = groupes.Membership()
    ain7etudiants_lionel.group = ain7etudiants
    ain7etudiants_lionel.member = lionel
    ain7etudiants_lionel.is_administrator = True
    ain7etudiants_lionel.save()

    ain7ecole = groupes.Group()
    ain7ecole.name = "AIn7 École"
    ain7ecole.administrator = lionel
    ain7ecole.save()

    ain7entreprises = groupes.Group()
    ain7entreprises.name = "AIn7 Entreprises"
    ain7entreprises.administrator = lionel
    ain7entreprises.save()

    ain7entreprisesemploi = groupes.Group()
    ain7entreprisesemploi.name = "AIn7 Entreprises - Emplois Carrières"
    ain7entreprisesemploi.administrator = lionel
    ain7entreprisesemploi.save()

    ain7evenementiel = groupes.Group()
    ain7evenementiel.name = "Événementiel"
    ain7evenementiel.administrator = lionel
    ain7evenementiel.save()

    groupesregionauxinter = groupes.Group()
    groupesregionauxinter.name = "Groupes régionaux et international"
    groupesregionauxinter.administrator = lionel
    groupesregionauxinter.save()

    mediacomcanal = groupes.Group()
    mediacomcanal.name = "Médias et Communications - Canal N7"
    mediacomcanal.administrator = lionel
    mediacomcanal.save()

    mediacomweb = groupes.Group()
    mediacomweb.name = "Médias et Communications - Serveur Web / Internet"
    mediacomweb.administrator = lionel
    mediacomweb.save()

    mediacomannuaire = groupes.Group()
    mediacomannuaire.name = "Médias et Communications - Annuaire"
    mediacomannuaire.administrator = lionel
    mediacomannuaire.save()

    relationscnisf = groupes.Group()
    relationscnisf.name = "Relations avec le CNISF et les URIS"
    relationscnisf.administrator = lionel
    relationscnisf.save()

    ain7voyages = groupes.Group()
    ain7voyages.name = "Relations avec le CNISF et les URIS"
    ain7voyages.administrator = lionel
    ain7voyages.save()

    sondage1 = sondages.Survey()
    sondage1.question = "Quelle est votre couleur préférée ?"
    sondage1.publication_date = datetime.now()
    sondage1.is_online = True
    sondage1.save()

    sondage1_choix1 = sondages.Choice()
    sondage1_choix1.survey = sondage1
    sondage1_choix1.choice = "Bleu"
    sondage1_choix1.save()

    sondage1_choix2 = sondages.Choice()
    sondage1_choix2.survey = sondage1
    sondage1_choix2.choice = "Vert"
    sondage1_choix2.save()

    sondage1_choix3 = sondages.Choice()
    sondage1_choix3.survey = sondage1
    sondage1_choix3.choice = "Rouge"
    sondage1_choix3.save()

    news1 = news.NewsItem()
    news1.title = "Nouveau portail Web"
    news1.description = """L'AIn7 travaille actuellement sur l'élaboration d'un 
    nouveau portail. N'hésitez pas à apporter vos idées et vos commentaires."""
    news1.save()

    news2 = news.NewsItem()
    news2.title = "100 ans !"
    news2.description = """L'n7 fête cette année ces 100 ans et va  tout au
    long de l'année 2007 célébrer à travers différentes manifestations cet anniversaire"""
    news2.save()

    looptravel = voyages.TravelType(type="Circuit")
    looptravel.save()

    boattravel = voyages.TravelType(type="Croisière")
    boattravel.save()

    travel1 = voyages.Travel()
    travel1.label = "Varsovie & croisière sur la Vistule"
    travel1.date = "Juin 2007"
    travel1.term = 14
    travel1.type = looptravel
    travel1.visited_places = "de Gdansk à Kaliningrad"
    travel1.prix = 2350
    travel1.save()

    travel2 = voyages.Travel()
    travel2.label = "Japon"
    travel2.date = "Octobre 2007"
    travel2.term = 13
    travel2.type = looptravel
    travel2.visited_places = "Tokyo, Atami, Kyoto, Hiroshima, Nara, Osazka"
    travel2.prix = 3890
    travel2.save()

    travel3 = voyages.Travel()
    travel3.label = "Birmanie"
    travel3.date = "Février 2008"
    travel3.type = looptravel
    travel3.visited_places = "Ragoon, Pagan, Sagain, Mandalay"
    travel3.prix = 3550
    travel3.save()

    travel4 = voyages.Travel()
    travel4.label = "Mongolie/ Pékin"
    travel4.date = "Juin 2008"
    travel4.term = 15
    travel4.type = boattravel
    travel4.prix = 2760
    travel4.save()

    travel5 = voyages.Travel()
    travel5.label = "Inde - Penjab & Himachal Pradesh"
    travel5.date = "Octobre 2008"
    travel5.term = 16
    travel5.type = boattravel
    travel5.visited_places = "Delhi, Amristar, Dharamsala, Manali, Simla"
    travel5.prix = 1900
    travel5.save()

    groupes_regionaux.GroupMembership(group=idfgroup, member=lionel, type=0).save()
    groupes_regionaux.GroupMembership(group=idfgroup, member=alex, type=2).save()
    groupes_regionaux.GroupMembership(group=idfgroup, member=pierref, type=7).save()
    groupes_regionaux.GroupMembership(group=idfgroup, member=olivier, type=7).save()

    evenement1 = evenements.Event()
    evenement1.name="Réunion 100 ans"
    evenement1.start_date=datetime.now()
    evenement1.end_date=datetime.now() + timedelta(30)
    evenement1.author="Moi"
    evenement1.contact_email="a@b.fr"
    evenement1.place="Ailleurs"
    evenement1.publication_start=datetime.now()
    evenement1.publication_end=datetime.now() + timedelta(30)
    evenement1.save()
    evenement1.regional_groups.add(idfgroup)
    evenement1.save()

    job1 = emploi.JobOffer()
    job1.reference = "XYZ270"
    job1.title = "Ingénieur Java/J2EE"
    job1.description = """Pour l'un de nos clients Grand Compte, nous recherchons des Ingénieurs d'études Java/J2ee, sous la conduite d'un Chef de projet, vous aurez en charge la réalisation des études techniques et fonctionnelles, le développement des application."""
    job1.experience = "1 à 2 ans"
    job1.contract_type = 0
    job1.is_opened = True
    job1.office = anywareoffice
    job1.save()

    job2 = emploi.JobOffer()
    job2.reference = "XYZ271"
    job2.title = "Ingénieur d'études Oracle, UNIX Expérimenté"
    job2.description = """Nous recherchons un ingénieur d'étude et de développement expérimenté pour un client grand compte. Mission :
    - Maintenance et développement sur une application sensible.
    -Développement de nouvelles fonctionnalités."""
    job2.experience = "2 à 3 ans"
    job2.contract_type = 0
    job2.is_opened = True
    job2.office = priceminister
    job2.save()

    job3 = emploi.JobOffer()
    job3.reference = "XYZ272"
    job3.title = "Ingénieur étude et développement décisionnel"
    job3.description = """Dans le cadre de nos projets réalisés pour nos clients grands comptes, sous la conduite d'un Chef de projet, vous serez chargé de réaliser des études techniques et fonctionnelles, de développer des applications, d'élaborer les plans d'intégration."""
    job3.experience = "1 à 2 ans"
    job3.contract_type = 1
    job3.is_opened = True
    job3.office = anywareoffice
    job3.save()

    job4 = emploi.JobOffer()
    job4.reference = "XYZ273"
    job4.title = "Ingénieur SI support produit"
    job4.description = """Intégré au sein de l'équipe « Formes de Vente » (15 personnes) et sous la direction d'un Responsable d'Equipe, vous garantissez le bon fonctionnement des produits à votre charge dans le système d'information."""
    job4.experience = "1 à 2 ans"
    job4.contract_type = 3
    job4.is_opened = False
    job4.office = anywareoffice
    job4.save()
    
    job5 = emploi.JobOffer()
    job5.reference = "XYZ274"
    job5.title = "Ingénieurs développement JAVA/J2EE"
    job5.description = """Nous souhaitons renforcer notre pôle de compétences NTIC Java J2EE : De formation informatique Bac+4/5, vous êtes aujourd'hui un Ingénieur débutant ou expérimenté et vous bénéficiez d'une réelle maîtrise des environnements de développement NTIC."""
    job5.experience = "0 à 3 ans"
    job5.contract_type = 3
    job5.is_opened = True
    job5.office = lepaysdesschtroumpfs
    job5.save()
