# -*- coding: utf-8
#
# filldb.py
#
#   Copyright (C) 2007-2008 AIn7
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

from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site

import ain7.adhesions.models as adhesions
import ain7.association.models as association
import ain7.annuaire.models as annuaire
import ain7.groupes_professionnels.models as groupes_professionnels
import ain7.groupes_regionaux.models as groupes_regionaux
import ain7.sondages.models as sondages
import ain7.news.models as news
import ain7.voyages.models as voyages
import ain7.emploi.models as emploi
import ain7.evenements.models as evenements
import ain7.manage.models as manage
import ain7.search_engine.models as search_engine

import vobject
import sys
import os

def filldb():

    if os.path.exists('filldbain7'):
        print "Import des donnees privees AIn7"
        execfile('filldbain7/base.py')
        execfile('filldbain7/companies.py')
        for root, dirs, files in os.walk('filldbain7'):
           for filename in files:
              if filename != 'base.py' and filename != 'companies.py':
                 print filename
                 execfile(root + '/' + filename)
        return
    else:
        print "Pas de donnes privees AIn7, importation des donnees de demo"
        pass

    ######################  Fixed values  ##############################
    # Cette partie regroupe les valeurs fixes de la base,              #
    # que l'on s'autorise donc à tester en dur dans le code.           #
    # Merci d'y ajouter tous les champs que vous devez tester en dur.  #

    # Types
    activityUnKnown = annuaire.Activity(activity=u"Inconnue")
    activityUnKnown.save()

    activityKnown = annuaire.Activity(activity=u"Connue")
    activityKnown.save()

    activityStudent = annuaire.Activity(activity=u"Étudiant")
    activityStudent.save()

    activityRetired = annuaire.Activity(activity=u"Retraité")
    activityRetired.save()

    memberTypeActif = annuaire.MemberType(type=u"Membre actif")
    memberTypeActif.save()

    personTypeEngineer = annuaire.PersonType(type=u"Ingénieur")
    personTypeEngineer.save()

    personTypeStudent = annuaire.PersonType(type=u"Étudiant")
    personTypeStudent.save()

    personalAddressType = annuaire.AddressType(type=u"Personnelle")
    personalAddressType.save()

    parentalAddressType = annuaire.AddressType(type=u"Parentale")
    parentalAddressType.save()

    maritalstatus_1 = annuaire.MaritalStatus(status=u"Marié(e)")
    maritalstatus_1.save()

    maritalstatus_2 = annuaire.MaritalStatus(status=u"Célibataire")
    maritalstatus_2.save()

    maritalstatus_3 = annuaire.MaritalStatus(status=u"Divorcé(e)")
    maritalstatus_3.save()

    maritalstatus_4 = annuaire.MaritalStatus(status=u"Maritalement")
    maritalstatus_4.save()

    maritalstatus_5 = annuaire.MaritalStatus(status=u"Veuf(veuve)")
    maritalstatus_5.save()

    maritalstatus_7 = annuaire.MaritalStatus(status=u"Séparé(e)")
    maritalstatus_7.save()

    # Contributions
    poll_contrib = annuaire.UserContributionType(key=u'poll_register',name=u'Création d\'un sondage',points=10)
    poll_contrib.save()

    poll_vote_contrib = annuaire.UserContributionType(key=u'poll_vote',name=u'Vote pour un sondage',points=5)
    poll_vote_contrib.save()

    event_contrib = annuaire.UserContributionType(key=u'event_register',name=u'Ajout d\'un événement',points=20)
    event_contrib.save()

    event_subscription_contrib = annuaire.UserContributionType(key=u'event_subcription',name=u'Inscription à un événement',points=5)
    event_subscription_contrib.save()

    annuaireSearchEngine = search_engine.SearchEngine()
    annuaireSearchEngine.name = "annuaire"
    annuaireSearchEngine.save()

    orgSearchEngine = search_engine.SearchEngine()
    orgSearchEngine.name = "organization"
    orgSearchEngine.save()

    subscription_conf1 = adhesions.SubscriptionConfiguration(type=0, dues_amount=75, newspaper_amount=15)
    subscription_conf1.save()

    subscription_conf2 = adhesions.SubscriptionConfiguration(type=1, dues_amount=50, newspaper_amount=15)
    subscription_conf2.save()

    subscription_conf3 = adhesions.SubscriptionConfiguration(type=2, dues_amount=50, newspaper_amount=15)
    subscription_conf3.save()

    subscription_conf4 = adhesions.SubscriptionConfiguration(type=3, dues_amount=160, newspaper_amount=15)
    subscription_conf4.save()

    subscription_conf5 = adhesions.SubscriptionConfiguration(type=4, dues_amount=30)
    subscription_conf5.save()

    subscription_conf6 = adhesions.SubscriptionConfiguration(type=5, dues_amount=15, duration=3)
    subscription_conf6.save()

    subscription_conf7 = adhesions.SubscriptionConfiguration(type=6, dues_amount=10, duration=2)
    subscription_conf7.save()

    subscription_conf8 = adhesions.SubscriptionConfiguration(type=7, dues_amount=5)
    subscription_conf8.save()

    #                                                                  #
    ###################### End of fixed values #########################

    # fixons l'URL du site
    site = Site.objects.get(id=1)
    site.domain = 'localhost:8888'
    site.name = 'localhost:8888'
    site.save()

    # Country
    france = annuaire.Country(name=u"France", nationality=u"Française")
    france.save()

    england = annuaire.Country(name=u"Angleterre", nationality=u"Anglaise")
    england.save()

    # Decorations
    warCross = annuaire.Decoration(decoration=u"Croix de Guerre")
    warCross.save()

    # Decorations
    JCPrice = annuaire.CeremonialDuty(ceremonial_duty=u"Prix Joliot Curie")
    JCPrice.save()

    # School
    n7 = annuaire.School()
    n7.name = u"École national supérieure d'éléctronique, d'éléctrotechnique, d'informatique, d'hydraulique et des télécommunications"
    n7.initials = u"ENSEEIHT"
    n7.save()

    n7info = annuaire.Track()
    n7info.name = u"Informatique et Mathématiques Appliquées"
    n7info.initials = u"IN"
    n7info.school = n7
    n7info.active = True
    n7info.save()

    n7hydro = annuaire.Track()
    n7hydro.name = u"Hydraulique et Mécanique des Fluides"
    n7hydro.initials = u"HY"
    n7hydro.school = n7
    n7hydro.active = True
    n7hydro.save()

    n7tr = annuaire.Track()
    n7tr.name = u"Télécommunications et Réseaux"
    n7tr.initials = u"TR"
    n7tr.school = n7
    n7tr.active = True
    n7tr.save()

    annuaire.Track(name=u"Electrotechnique", initials="", school=n7).save()
    annuaire.Track(name=u"Mathématiques Appliquées", initials="", school=n7).save()
    annuaire.Track(name=u"Automatique", initials="", school=n7).save()
    annuaire.Track(name=u"Automatique Avancée", initials="", school=n7).save()
    annuaire.Track(name=u"Electrotechnique option Génie Energétique", initials="", school=n7).save()
    annuaire.Track(name=u"Méthodes & Applications Avancées en IN option F", initials="", school=n7).save()
    annuaire.Track(name=u"Electrotechnique option Electronique Industrielle", initials="", school=n7).save()
    annuaire.Track(name=u"Systèmes de Communication & des Réseaux", initials="", school=n7).save()
    annuaire.Track(name=u"Electrotechnique & Electronique de Puissance", initials="", school=n7).save()
    annuaire.Track(name=u"Méthodes & Applications Avancées en Informatiqi.", initials="", school=n7).save()
    annuaire.Track(name=u"Génie Energétique des Equipements Industriels", initials="", school=n7).save()
    annuaire.Track(name=u"Traitement du Signal et des Images", initials="", school=n7).save()
    annuaire.Track(name=u"Méthodes & Applications Avancées en IN option II", initials="", school=n7).save()
    annuaire.Track(name=u"Electronique de Puissance Avancée", initials="", school=n7).save()
    annuaire.Track(name=u"Méthodes & Applications Avancées en IN option?", initials="", school=n7).save()
    annuaire.Track(name=u"Section Spéciale Calcul Scientifique à Haute Performance", initials="", school=n7).save()
    annuaire.Track(name=u"Electronique et Traitement du Signal", initials="", school=n7).save()
    annuaire.Track(name=u"Génie Electrique et Automatique", initials="", school=n7).save()
    annuaire.Track(name=u"Section Spéciale Calcul Scientifique à Haute Performance", initials="", school=n7).save()
    annuaire.Track(name=u"Docteur Ingénieur", initials="", school=n7).save()
    annuaire.Track(name=u"Section Spéciale Génie Electrique et Automatique", initials="", school=n7).save()
    annuaire.Track(name=u"Section Spéciale Génie Electrique et Automatique", initials="", school=n7).save()
    annuaire.Track(name=u"Section Speciale Systèmes de Communications et Réseaux", initials="", school=n7).save()
    annuaire.Track(name=u"Section Speciale Systèmes de Communications et Réseaux", initials="", school=n7).save()
    annuaire.Track(name=u"Section Spéciale Traitement Avancé de l'Energie Electrique", initials="", school=n7).save()
    annuaire.Track(name=u"DHET Technologies Multimedia", initials="", school=n7).save()
    annuaire.Track(name=u"DHET Hydraulique", initials="", school=n7).save()
    annuaire.Track(name=u"DHET Systèmes de Communication et Réseaux", initials="", school=n7).save()
    annuaire.Track(name=u"DHET Génie Electrique et Automatique", initials="", school=n7).save()
    annuaire.Track(name=u"DHET Systèmes Electroniques", initials="", school=n7).save()
    annuaire.Track(name=u"DHET informatique fl.", initials="", school=n7).save()

    y2000 = annuaire.PromoYear(year='2000')
    y2000.save()

    y2001 = annuaire.PromoYear(year='2001')
    y2001.save()

    y2002 = annuaire.PromoYear(year='2002')
    y2002.save()

    y2003 = annuaire.PromoYear(year='2003')
    y2003.save()

    y2004 = annuaire.PromoYear(year='2004')
    y2004.save()

    y2005 = annuaire.PromoYear(year='2005')
    y2005.save()

    y2006 = annuaire.PromoYear(year='2006')
    y2006.save()

    y2007 = annuaire.PromoYear(year='2007')
    y2007.save()

    y2008 = annuaire.PromoYear(year='2008')
    y2008.save()

    n7hy2006 = annuaire.Promo(year=y2006, track=n7hydro)
    n7hy2006.save()

    n7in2006 = annuaire.Promo(year=y2006, track=n7info)
    n7in2006.save()

    n7in2003 = annuaire.Promo(year=y2003, track=n7info)
    n7in2003.save()

    n7in2008 = annuaire.Promo(year=y2008, track=n7info)
    n7in2008.save()

    n7tr2003 = annuaire.Promo(year=y2003, track=n7tr)
    n7tr2003.save()

    n7hy2003 = annuaire.Promo(year=y2003, track=n7hydro)
    n7hy2003.save()

    # Organizations
    infofield = emploi.ActivityField(field = u"Informatique", code=u"ZZ", label=u"Informatique")
    infofield.save()

    telecomfield = emploi.ActivityField(field = u"Telecom", code=u"TC", label=u"Télécom")
    telecomfield.save()

    babelstore = emploi.Organization(name=u"BABELSTORE", activity_field=infofield, size=2)
    babelstore.save()

    priceminister = emploi.Office(name=u"PriceMinister", organization=babelstore)
    priceminister.save()

    anyware = emploi.Organization(name=u"Anyware Technologies", activity_field=infofield)
    anyware.save()

    anywareoffice = emploi.Office(name=u"Toulouse Labège", organization=anyware)
    anywareoffice.save()

    anywareoffice = emploi.Office(name=u"Paris", organization=anyware)
    anywareoffice.save()

    schtroumpfland = emploi.Organization(name=u"Schtroumpfland", activity_field=infofield)
    schtroumpfland.save()

    lepaysdesschtroumpfs = emploi.Office(name=u"Mon champignon", organization=schtroumpfland)
    lepaysdesschtroumpfs.save()

    # Regional group
    gr1 = groupes_regionaux.Group(name=u"Alpes Côte d'Azur")
    gr1.save()
    gr2 = groupes_regionaux.Group(name=u"Centre")
    gr2.save()
    gr3 = groupes_regionaux.Group(name=u"Midi-Pyrénées")
    gr3.save()
    gr4 = groupes_regionaux.Group(name=u"Nord-Picardie")
    gr4.save()
    gr5 = groupes_regionaux.Group(name=u"Aquitaine")
    gr5.save()
    gr6 = groupes_regionaux.Group(name=u"Rhône-Alpes")
    gr6.save()
    gr7 = groupes_regionaux.Group(name=u"Est")
    gr7.save()
    gr8 = groupes_regionaux.Group(name=u"Ouest")
    gr8.save()
    gr9 = groupes_regionaux.Group(name=u"Marseille-Provence")
    gr9.save()
    gr10 = groupes_regionaux.Group(name=u"Normandie")
    gr10.save()
    gr11 = groupes_regionaux.Group(name=u"Région Parisienne")
    gr11.save()
    gr12 = groupes_regionaux.Group(name=u"Languedoc-Roussillon")
    gr12.save()


    # Groups / Roles
    ain7_admin = Group(name='ain7-admin')
    ain7_admin.save()
    ain7_devel = Group(name='ain7-devel')
    ain7_devel.save()
    ain7_bureau = Group(name='ain7-bureau')
    ain7_bureau.save()
    ain7_ca = Group(name='ain7-ca')
    ain7_ca.save()
    ain7_secretariat = Group(name='ain7-secretariat')
    ain7_secretariat.save()
    ain7_membre = Group(name='ain7-membre')
    ain7_membre.save()
    ain7_recruteur = Group(name='ain7-recruteur')
    ain7_recruteur.save()
    ain7_emploi = Group(name='ain7-emploi')
    ain7_emploi.save()
    ain7_voyages = Group(name='ain7-voyages')
    ain7_voyages.save()
    ain7_externe = Group(name='ain7-externe')
    ain7_externe.save()
    ain7_contrib = Group(name='ain7-contributeur')
    ain7_contrib.save()

    # Person
    lionel = annuaire.Person()
    lionel.user = User.objects.create_user("lionel", "lionel@ain7.org","lionel")
    lionel.user.is_staff = True
    lionel.user.is_superuser = True
    lionel.user.groups.add(ain7_admin)
    lionel.user.groups.add(ain7_devel)
    lionel.user.groups.add(ain7_ca)
    lionel.user.groups.add(ain7_membre)
    lionel.user.save()
    lionel.sex = 'M'
    lionel.first_name = "Lionel"
    lionel.last_name = "Porcheron"
    lionel.complete_name = "Lionel Porcheron"
    lionel.birth_date = date(1978,11,18)
    lionel.country = france
    lionel.save()

    # AIn7Member
    lionel_ain7member = annuaire.AIn7Member()
    lionel_ain7member.person = lionel
    lionel_ain7member.activity = activityKnown
    lionel_ain7member.member_type = memberTypeActif
    lionel_ain7member.person_type = personTypeEngineer
    lionel_ain7member.nick_name = "Yoyo"
    lionel_ain7member.blog = "http://www.porcheron.info"
    lionel_ain7member.blog_agrege_sur_le_planet = True
    lionel_ain7member.display_cv_in_directory = True
    lionel_ain7member.display_cv_in_job_section = True
    lionel_ain7member.receive_job_offers = False
    lionel_ain7member.cv_title = "Ingénieur ENSEEIHT Informatique"
    lionel_ain7member.marital_status = maritalstatus_2
    lionel_ain7member.save() # un premier save avant les many2many
    lionel_ain7member.promos.add(n7in2003)
    lionel_ain7member.save()

    lionel_adresse = annuaire.Address()
    lionel_adresse.person = lionel
    lionel_adresse.line1 = "2 rue Charles Camichel"
    lionel_adresse.zip_code = "31000"
    lionel_adresse.city = "Toulouse"
    lionel_adresse.country = france
    lionel_adresse.type = personalAddressType
    lionel_adresse.save()

    lionel_couriel1 = annuaire.Email()
    lionel_couriel1.person = lionel
    lionel_couriel1.email = "lionel@ain7.org"
    lionel_couriel1.preferred_email = True
    lionel_couriel1.save()

    lionel_couriel2 = annuaire.Email()
    lionel_couriel2.person = lionel
    lionel_couriel2.email = "lionel@porcheron.info"
    lionel_couriel2.confidentiality = 2
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
    lionel_site.type = 1
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
    lionel_position1.ain7member = lionel_ain7member
    lionel_position1.office = anywareoffice
    lionel_position1.fonction = "AdminSys"
    lionel_position1.start_date = date(2005,01,01)
    lionel_position1.end_date = date(2007,01,01)
    lionel_position1.save()

    lionel_position2 = emploi.Position()
    lionel_position2.ain7member = lionel_ain7member
    lionel_position2.office = anywareoffice
    lionel_position2.fonction = "Big boss"
    lionel_position2.start_date = date(2007,01,01)
    lionel_position2.save()

    lionel_subscription1 = adhesions.Subscription()
    lionel_subscription1.member = lionel_ain7member
    lionel_subscription1.start_year = 2003
    lionel_subscription1.end_year = 2005
    lionel_subscription1.dues_amount = 50
    lionel_subscription1.tender_type = 1
    lionel_subscription1.save()

    lionel_subscription2 = adhesions.Subscription()
    lionel_subscription2.member = lionel_ain7member
    lionel_subscription2.start_year = 2003
    lionel_subscription2.end_year = 2003
    lionel_subscription2.dues_amount = 50
    lionel_subscription2.newspaper_amount = 0
    lionel_subscription2.tender_type = 1
    lionel_subscription2.save()

    lionel_subscription3 = adhesions.Subscription()
    lionel_subscription3.member = lionel_ain7member
    lionel_subscription3.start_year = 2004
    lionel_subscription3.end_year = 2004
    lionel_subscription3.dues_amount = '50'
    lionel_subscription3.newspaper_amount = 15
    lionel_subscription3.tender_type = 0
    lionel_subscription3.save()

    lionel_subscription4 = adhesions.Subscription()
    lionel_subscription4.member = lionel_ain7member
    lionel_subscription4.start_year = 2005
    lionel_subscription4.end_year = 2005
    lionel_subscription4.dues_amount = '50'
    lionel_subscription4.newspaper_amount = 15
    lionel_subscription4.tender_type = 0
    lionel_subscription4.save()

    lionel_subscription5 = adhesions.Subscription()
    lionel_subscription5.member = lionel_ain7member
    lionel_subscription5.start_year = 2006
    lionel_subscription5.end_year = 2007
    lionel_subscription5.dues_amount = '50'
    lionel_subscription5.newspaper_amount = 15
    lionel_subscription5.tender_type = 0
    lionel_subscription5.save()

    pierref = annuaire.Person()
    pierref.user = User.objects.create_user("pierref", "pierre.fersing@inp-net.eu.org","pierref")
    pierref.user.is_staff = True
    pierref.user.is_superuser = True
    pierref.user.groups.add(ain7_admin)
    pierref.user.groups.add(ain7_devel)
    pierref.user.groups.add(ain7_membre)
    pierref.user.save()
    pierref.sex = 'M'
    pierref.first_name = "Pierre"
    pierref.last_name = "Fersing"
    pierref.complete_name = "Pierre Fersing"
    pierref.birth_date = date(1985,11,05)
    pierref.country = france
    pierref.save()

    pierref_ain7member = annuaire.AIn7Member()
    pierref_ain7member.person = pierref
    pierref_ain7member.activity = activityKnown
    pierref_ain7member.member_type = memberTypeActif
    pierref_ain7member.person_type = personTypeStudent
    pierref_ain7member.nick_name = "PierreF"
    pierref_ain7member.display_cv_in_directory = False
    pierref_ain7member.display_cv_in_job_section = True
    pierref_ain7member.receive_job_offers = False
    pierref_ain7member.cv_title = u"Élève Ingénieur ENSEEIHT Informatique"
    pierref_ain7member.marital_status = maritalstatus_2
    pierref_ain7member.save() # un premier save avant les many2many
    pierref_ain7member.promos.add(n7in2008)
    pierref_ain7member.save()

    pierref_adresse = annuaire.Address()
    pierref_adresse.person = pierref
    pierref_adresse.line1 = "2 rue Charles Camichel"
    pierref_adresse.zip_code = "31000"
    pierref_adresse.city = "Toulouse"
    pierref_adresse.country = france
    pierref_adresse.type = personalAddressType
    pierref_adresse.save()

    pierref_irc1 = annuaire.IRC()
    pierref_irc1.person = pierref
    pierref_irc1.network = "irc.rezosup.net"
    pierref_irc1.pseudo = "pierref"
    pierref_irc1.channels = "#ain7, #inp-net, #n7, #net7"
    pierref_irc1.save()

    olivier = annuaire.Person()
    olivier.user = User.objects.create_user("gauwino", "olivier.gauwin@laposte.net","gauwino")
    olivier.user.is_staff = True
    olivier.user.is_superuser = True
    olivier.user.groups.add(ain7_admin)
    olivier.user.groups.add(ain7_devel)
    olivier.user.groups.add(ain7_membre)
    olivier.user.save()
    olivier.sex = 'M'
    olivier.first_name = "Olivier"
    olivier.last_name = "Gauwin"
    olivier.complete_name = "Olivier Gauwin"
    olivier.birth_date = date(1955,12,9)
    olivier.country = france
    olivier.notes = u"Je ne sais pas à quoi sert ce champ mais je fais confiance à Alex!"
    olivier.save()

    olivier_ain7member = annuaire.AIn7Member()
    olivier_ain7member.person = olivier
    olivier_ain7member.activity = activityKnown
    olivier_ain7member.member_type = memberTypeActif
    olivier_ain7member.person_type = personTypeEngineer
    olivier_ain7member.display_cv_in_directory = True
    olivier_ain7member.display_cv_in_job_section = True
    olivier_ain7member.receive_job_offers = True
    olivier_ain7member.cv_title = u"Ingénieur ENSEEIHT et doctorant en Informatique"
    olivier_ain7member.marital_status = maritalstatus_2
    olivier_ain7member.save()
    olivier_ain7member.promos.add(n7in2003)
    olivier_ain7member.receive_job_offers_for_tracks.add(n7info)
    olivier_ain7member.save()

    olivier_adresse = annuaire.Address()
    olivier_adresse.person = olivier
    olivier_adresse.line1 = "2 rue Charles Camichel"
    olivier_adresse.zip_code = "31000"
    olivier_adresse.city = "Toulouse"
    olivier_adresse.country = france
    olivier_adresse.type = personalAddressType
    olivier_adresse.save()

    olivier_adresse2 = annuaire.Address()
    olivier_adresse2.person = olivier
    olivier_adresse2.line1 = "8 rue de nulle part"
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
    olivier_site.type = 0
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

    olivier_position1 = emploi.Position()
    olivier_position1.ain7member = olivier_ain7member
    olivier_position1.office = lepaysdesschtroumpfs
    olivier_position1.fonction = "Schtroumpf paresseux"
    olivier_position1.start_date = date(2003,01,01)
    olivier_position1.end_date = date(2007,01,01)
    olivier_position1.save()

    olivier_position2 = emploi.Position()
    olivier_position2.ain7member = olivier_ain7member
    olivier_position2.office = lepaysdesschtroumpfs
    olivier_position2.fonction = "Grand Schtroumpf"
    olivier_position2.start_date = date(2007,01,01)
    olivier_position2.save()

    olivier_education1 = emploi.EducationItem()
    olivier_education1.ain7member = olivier_ain7member
    olivier_education1.school = "ENSEEIHT"
    olivier_education1.diploma = u"Ingenieur en informatique et mathématiques appliquées"
    olivier_education1.details = u"Troisième année à la Technische Universität Darmstadt, Allemagne."
    olivier_education1.start_date = date(2001,1,11)
    olivier_education1.end_date = date(2003,8,23)
    olivier_education1.save()

    olivier_education2 = emploi.EducationItem()
    olivier_education2.ain7member = olivier_ain7member
    olivier_education2.school = "Université d'Artois"
    olivier_education2.diploma = u"DEA Systèmes intelligents et applications"
    olivier_education2.start_date = date(2003,9,1)
    olivier_education2.end_date = date(2004,8,23)
    olivier_education2.save()

    olivier_leisure1 = emploi.LeisureItem()
    olivier_leisure1.ain7member = olivier_ain7member
    olivier_leisure1.title = "Culture"
    olivier_leisure1.detail = u"Guitare, cinéma"
    olivier_leisure1.save()

    olivier_leisure2 = emploi.LeisureItem()
    olivier_leisure2.ain7member = olivier_ain7member
    olivier_leisure2.title = "Informatique"
    olivier_leisure2.detail = "Le site de l'AIn7 !!"
    olivier_leisure2.save()

    alex = annuaire.Person()
    alex.user = User.objects.create_user("alex", "zigouigoui.garnier@laposte.net","alex")
    alex.user.is_staff = True
    alex.user.is_superuser = True
    alex.user.groups.add(ain7_admin)
    alex.user.groups.add(ain7_devel)
    alex.user.groups.add(ain7_membre)
    alex.user.save()
    alex.sex = 'M'
    alex.first_name = "Alexandre"
    alex.last_name = "Garnier"
    alex.complete_name = "Alexandre Garnier"
    alex.birth_date = date(1984,03,14)
    alex.country = france
    alex.save()

    alex_ain7member = annuaire.AIn7Member()
    alex_ain7member.person = alex
    alex_ain7member.activity = activityKnown
    alex_ain7member.member_type = memberTypeActif
    alex_ain7member.person_type = personTypeEngineer
    alex_ain7member.nick_name = "Alex"
    alex_ain7member.display_cv_in_directory = False
    alex_ain7member.display_cv_in_job_section = False
    alex_ain7member.receive_job_offers = False
    alex_ain7member.cv_title = u"Ingénieur ENSEEIHT Informatique"
    alex_ain7member.marital_status = maritalstatus_2
    alex_ain7member.save()
    alex_ain7member.promos.add(n7in2006)
    alex_ain7member.save()

    alex_portable = annuaire.PhoneNumber()
    alex_portable.person = alex
    alex_portable.number = "0681901082"
    alex_portable.type = 3
    alex_portable.isConfidential = False
    alex_portable.save()

    alex_adresse1 = annuaire.Address()
    alex_adresse1.person = alex
    alex_adresse1.line1 = "79 rue Broca"
    alex_adresse1.line2 = u"1er étage gauche"
    alex_adresse1.zip_code = "75013"
    alex_adresse1.city = "Paris"
    alex_adresse1.country = france
    alex_adresse1.type = personalAddressType
    alex_adresse1.save()

    alex_adresse2 = annuaire.Address()
    alex_adresse2.person = alex
    alex_adresse2.line1 = "70 rue de Paris"
    alex_adresse2.zip_code = "95720"
    alex_adresse2.city = "Le Mesnil-Aubry"
    alex_adresse2.country = france
    alex_adresse2.type = parentalAddressType
    alex_adresse2.save()

    alexpos = emploi.Position()
    alexpos.ain7member = alex_ain7member
    alexpos.office = priceminister
    alexpos.fonction = "dev"
    alexpos.start_date = date(2006,8,17)
    alexpos.save()

    laurent = annuaire.Person()
    laurent.user = User.objects.create_user("laurent", "laurent07@gmail.com","laurent")
    laurent.user.is_staff = True
    laurent.user.is_superuser = True
    laurent.user.groups.add(ain7_admin)
    laurent.user.groups.add(ain7_devel)
    laurent.user.groups.add(ain7_membre)
    laurent.user.save()
    laurent.sex = 'M'
    laurent.first_name = "Laurent"
    laurent.last_name = "Bives"
    laurent.complete_name = "Laurent Bives"
    laurent.birth_date = date(1984,03,14)
    laurent.country = france
    laurent.save()

    laurent_ain7member = annuaire.AIn7Member()
    laurent_ain7member.person = laurent
    laurent_ain7member.activity = activityKnown
    laurent_ain7member.member_type = memberTypeActif
    laurent_ain7member.person_type = personTypeEngineer
    laurent_ain7member.nick_name = "Lau"
    laurent_ain7member.display_cv_in_directory = False
    laurent_ain7member.display_cv_in_job_section = False
    laurent_ain7member.receive_job_offers = False
    laurent_ain7member.cv_title = u"Ingénieur ENSEEIHT Télécommunications et Réseaux"
    laurent_ain7member.marital_status = maritalstatus_2
    laurent_ain7member.save()
    laurent_ain7member.promos.add(n7tr2003)
    laurent_ain7member.save()

    laurent_portable = annuaire.PhoneNumber()
    laurent_portable.person = laurent
    laurent_portable.number = "0600000000"
    laurent_portable.type = 3
    laurent_portable.isConfidential = False
    laurent_portable.save()

    laurent_adresse1 = annuaire.Address()
    laurent_adresse1.person = laurent
    laurent_adresse1.line1 = "2 rue Charles Camichel"
    laurent_adresse1.zip_code = "31071"
    laurent_adresse1.city = "Paris"
    laurent_adresse1.country = france
    laurent_adresse1.type = personalAddressType
    laurent_adresse1.save()

    laurent_adresse2 = annuaire.Address()
    laurent_adresse2.person = laurent
    laurent_adresse2.line1 = "2 rue Charles Camichel"
    laurent_adresse2.zip_code = "31071"
    laurent_adresse2.city = "Toulouse"
    laurent_adresse2.country = france
    laurent_adresse2.type = parentalAddressType
    laurent_adresse2.save()

    gui = annuaire.Person()
    gui.user = User.objects.create_user("gui", "gui@ain7.com","gui")
    gui.user.is_staff = True
    gui.user.is_superuser = True
    gui.user.groups.add(ain7_membre)
    gui.user.save()
    gui.sex = 'M'
    gui.first_name = "Guillaume"
    gui.last_name = "Bonnaffoux"
    gui.complete_name = "Guillaume Bonnaffoux"
    gui.birth_date = date(1980,06,9)
    gui.country = france
    gui.save()

    gui_ain7member = annuaire.AIn7Member()
    gui_ain7member.person = gui
    gui_ain7member.activity = activityKnown
    gui_ain7member.member_type = memberTypeActif
    gui_ain7member.person_type = personTypeEngineer
    gui_ain7member.nick_name = "Gui"
    gui_ain7member.display_cv_in_directory = False
    gui_ain7member.display_cv_in_job_section = False
    gui_ain7member.receive_job_offers = False
    gui_ain7member.cv_title = u"Ingénieur ENSEEIHT Cuicui les petits oiseaux"
    gui_ain7member.marital_status = maritalstatus_1
    gui_ain7member.save()
    gui_ain7member.promos.add(n7hy2003)
    gui_ain7member.save()

    gui_portable = annuaire.PhoneNumber()
    gui_portable.person = gui
    gui_portable.number = "0600000000"
    gui_portable.type = 3
    gui_portable.isConfidential = False
    gui_portable.save()

    gui_adresse1 = annuaire.Address()
    gui_adresse1.person = gui
    gui_adresse1.line1 = "2 rue Charles Camichel"
    gui_adresse1.zip_code = "31071"
    gui_adresse1.city = "Toulouse"
    gui_adresse1.country = france
    gui_adresse1.type = personalAddressType
    gui_adresse1.save()

    gui_adresse2 = annuaire.Address()
    gui_adresse2.person = gui
    gui_adresse2.line1 = "2 rue Charles Camichel"
    gui_adresse2.zip_code = "31071"
    gui_adresse2.city = "Toulouse"
    gui_adresse2.country = france
    gui_adresse2.type = parentalAddressType
    gui_adresse2.save()

    tvn7 = annuaire.Club()
    tvn7.name = "TVn7"
    tvn7.description = u"Le club vidéo de l'N7"
    tvn7.web_site = "http://www.tvn7.fr.st"
    tvn7.email = "tvn7@lists.bde.enseeiht.fr"
    tvn7.creation_date = date(1992,01,01)
    tvn7.school = n7
    tvn7.save()

    tvn7_lionel = annuaire.ClubMembership()
    tvn7_lionel.club = tvn7
    tvn7_lionel.member = lionel_ain7member
    tvn7_lionel.save()

    tvn7_alex = annuaire.ClubMembership()
    tvn7_alex.club = tvn7
    tvn7_alex.member = alex_ain7member
    tvn7_alex.fonction = u"Secrétaire 2004-2005"
    tvn7_alex.save()

    tvn7_gui = annuaire.ClubMembership()
    tvn7_gui.club = tvn7
    tvn7_gui.member = gui_ain7member
    tvn7_gui.fonction = "Président 2002-2003"
    tvn7_gui.save()

    net7 = annuaire.Club()
    net7.name = "Net7"
    net7.description = u"Le club informatique et réseau de l'N7"
    net7.web_site = "http://www.bde.enseeiht.fr"
    net7.email = "net7@bde.enseeiht.fr"
    net7.creation_date = date(1992,01,01)
    net7.school = n7
    net7.save()

    net7_lionel = annuaire.ClubMembership()
    net7_lionel.club = net7
    net7_lionel.member = lionel_ain7member
    net7_lionel.save()

    net7_pierref = annuaire.ClubMembership()
    net7_pierref.club = net7
    net7_pierref.member = pierref_ain7member
    net7_pierref.save()

    inpnet = annuaire.Club()
    inpnet.name = "INP-net"
    inpnet.description = u"Le club informatique et réseau de l'INP"
    inpnet.web_site = "http://www.inp-net.eu.org"
    inpnet.email = "inp-net@bde.inp-toulouse.fr"
    inpnet.creation_date = date(2002,07,01)
    inpnet.school = n7
    inpnet.save()

    inpnet_lionel = annuaire.ClubMembership()
    inpnet_lionel.club = inpnet
    inpnet_lionel.member = lionel_ain7member
    inpnet_lionel.fonction = "Président 2002-2003 - Cofondateur du club"
    inpnet_lionel.save()

    inpnet_pierref = annuaire.ClubMembership()
    inpnet_pierref.club = inpnet
    inpnet_pierref.member = pierref_ain7member
    inpnet_pierref.fonction = u"Président 2006-2007"
    inpnet_pierref.save()

    sylvie = annuaire.Person()
    sylvie.user = User.objects.create_user("sylvie", "noreply@ain7.info","sylvie")
    sylvie.user.groups.add(ain7_admin)
    sylvie.user.groups.add(ain7_secretariat)
    sylvie.user.save()
    sylvie.sex = 'F'
    sylvie.first_name = "Sylvie"
    sylvie.last_name = "H"
    sylvie.complete_name = "Sylvie H"
    sylvie.country = france
    sylvie.save()

    sylvie_adresse = annuaire.Address()
    sylvie_adresse.person = sylvie
    sylvie_adresse.line1 = "2 rue Charles Camichel"
    sylvie_adresse.zip_code = "31000"
    sylvie_adresse.city = "Toulouse"
    sylvie_adresse.country = france
    sylvie_adresse.type = personalAddressType
    sylvie_adresse.save()

    sylvie_couriel1 = annuaire.Email()
    sylvie_couriel1.person = sylvie
    sylvie_couriel1.email = "noreply@ain7.info"
    sylvie_couriel1.preferred_email = True

    frederique = annuaire.Person()
    frederique.user = User.objects.create_user("frederique", "noreply@ain7.info","frederique")
    frederique.user.groups.add(ain7_admin)
    frederique.user.groups.add(ain7_secretariat)
    frederique.user.groups.add(ain7_emploi)
    frederique.user.save()
    frederique.sex = 'F'
    frederique.first_name = "Frédérique"
    frederique.last_name = "F"
    frederique.complete_name = "Frédérique F"
    frederique.country = france
    frederique.save()

    frederique_adresse = annuaire.Address()
    frederique_adresse.person = frederique
    frederique_adresse.line1 = "2 rue Charles Camichel"
    frederique_adresse.zip_code = "31000"
    frederique_adresse.city = "Toulouse"
    frederique_adresse.country = france
    frederique_adresse.type = personalAddressType
    frederique_adresse.save()

    frederique_couriel1 = annuaire.Email()
    frederique_couriel1.person = frederique
    frederique_couriel1.email = "noreply@ain7.info"
    frederique_couriel1.preferred_email = True
    frederique_couriel1.save()

    recruteur = annuaire.Person()
    recruteur.user = User.objects.create_user("jeannot", "noreply@ain7.info","jeannot")
    recruteur.user.groups.add(ain7_recruteur)
    recruteur.user.groups.add(ain7_externe)
    recruteur.user.save()
    recruteur.sex = 'M'
    recruteur.first_name = "Jeannot"
    recruteur.last_name = "Lapin"
    recruteur.complete_name = "Jeannot Lapin"
    recruteur.country = france
    recruteur.save()

    recruteur_adresse = annuaire.Address()
    recruteur_adresse.person = recruteur
    recruteur_adresse.line1 = "2 rue Charles Camichel"
    recruteur_adresse.zip_code = "31000"
    recruteur_adresse.city = "Toulouse"
    recruteur_adresse.country = france
    recruteur_adresse.type = personalAddressType
    recruteur_adresse.save()

    recruteur_couriel1 = annuaire.Email()
    recruteur_couriel1.person = recruteur
    recruteur_couriel1.email = "noreply@ain7.info"
    recruteur_couriel1.preferred_email = True
    recruteur_couriel1.save()

    ain7tic = groupes_professionnels.GroupPro()
    ain7tic.name = "tic"
    ain7tic.description = "Technologies de l'Information et Communications"
    ain7tic.web_page = """<p>Ce groupe de travail s'adresse aux N7 dirigeants d'une petite entreprise / PME, PMI ou TPE. L'ingénieur N7, qu'il soit fraîchement diplômé ou chevronné, est confronté à un monde économique en profonde mutation qui se traduit en particulier par la création d'entreprise et par une accélération de leur renouvellement. Ce facteur est amplifié avec les opportunités qu'offre la nouvelle économie avec Internet.</p>

<p>Un certain nombre d'entre nous ont créé leur entreprise, et ce qui était rare jusqu'à un passé récent devient de plus en plus fréquent.</p>

<p>Dans l'esprit de convivialité et de solidarité qui la caractérise, l'AIN7 a donc proposé la création en son sein d'un groupe professionnel sur la création d'entreprise, persudée qu'il rencontrera de l'intérêt auprès de ses membres.</p>

<p>L'objectif visé est de faciliter les échanges entre les créateurs, qui ont donc des préoccupations communes, et aussi avec ceux d'entre nos camarades qui ont de tels projets.</p>

<p>De plus, ces travaux sont susceptibles d'intéresser nos camarades futurs diplômés pour les aider à trouver un écho pertinent auprès d'acteurs de la création d'entreprise et ils pourront faire des propositions à l'Ecole pour introduire, le cas échéant, des enseignements appropriés dans ses programmes, répondant ainsi à cette nouvelle demande.</p>"""
    ain7tic.save()
    ain7ticMS1 = groupes_professionnels.Membership()
    ain7ticMS1.group = ain7tic
    ain7ticMS1.member = olivier
    ain7ticMS1.save()
    ain7ticRole1 = groupes_professionnels.GroupProRole()
    ain7ticRole1.member = olivier
    ain7ticRole1.group = ain7tic
    ain7ticRole1.type = 0
    ain7ticRole1.save()

    ain7telecom = groupes_professionnels.GroupPro()
    ain7telecom.name = "telecom"
    ain7telecom.description = "Groupe Telecom"
    ain7telecom.web_page="""<p>Le Groupe professionnel TELECOM réunit les ingénieurs qui travaillent aux réseaux de Télécommunications.</p>

<p>Un noyau d'ingénieurs N7 animent le groupe, préparent les manifestations extérieures (N7à9, Manifestions de prestige…) et recherchent le cas échéant le financement de celles-ci.</p>

<p>Il est un des interlocuteurs de l'ENSEEIHT du Département "Télécommunications &amp; Réseaux".</p>

<p>Il a une couverture nationale.</p>

<p>Il participe dans son domaine à assurer la promotion de l'ENSEEIHT dans le cadre de l'AIN7 et en liaison avec la Direction de l'Ecole.</p>

<p>Il a vocation d'entraide pour la recherche d'emplois, en liaison avec les Correspondants d'Entreprises.</p>

<p>Il bénéficie de la logistique de l'AIN7.</p>

<p>La Communication du Groupe se fait par le canal de l'AIN7.</p>

<b>REALISATIONS</b>

<ul>
  <li>N7à9 du 5 juin 1997 " Les Métiers de France Télécom Mobiles"</li>
  <li>Table Ronde du 14 janvier 1999 "La Dérégulation des Télécoms, facteur de croissance"</li>
  <li>Colloque du 20 janvier 2000 : "La Future Génération des Ingénieurs Télécom", à l'ENSEEIHT</li>
  <li>N7à9 du 18 mai 2000 : "Compte-Rendu du Colloque du 20 janvier 2000 à Toulouse"</li>
</ul>

<b>PROGRAMME FUTUR</b>

Axes de réflexion:
<ul>
  <li>les clés de l'adaptation de l'ingénieur dans une Entreprise des télécommunications</li>
  <li>le phènomène INTERNET et/ou INTERNET Mobiles</li>
  <li>les technologies de l'Information</li>
  <li>l'UMTS</li>
</ul>

Prochaines manifestations
<ul>
  <li>Conférence-Débat sur le thème : "M-Commerce", dans le cadre de l'N7à9 du groupe parisien, mercredi 16 mai 2001 à 19 H 30 à l'USIC, 18 rue de Varenne PARIS, 7ème avec la participation de :
  <ul>
    <li>Philippe CROS (EN 80) – Les systèmes de paiement</li>
    <li>Francis BARRIER (EN 86) – Les mobiles et leurs technologies</li>
    <li>Roland DUBOIS (SEN 65) – Le marketing</li>
  </ul>
</ul>

<p>en 2002, manifestation de prestige à l'occasion de la sortie de la première promotion de la Filière "Télécommunications &amp; Réseaux". Programme de la manifestation en cours d'élaboration.</p>"""
    ain7telecom.save()

    ain7energie = groupes_professionnels.GroupPro()
    ain7energie.name = "energie"
    ain7energie.description = "Groupe Energie"
    ain7energie.web_page = "Issu du groupe \"Génie Electrique\", ce groupe est en cours de reconstitution et doit démarrer des activités élargies au printemps 2009."
    ain7energie.save()

    ain7aero = groupes_professionnels.GroupPro()
    ain7aero.name = "aero"
    ain7aero.description = "Groupe Aérospace"
    ain7aero.web_page = "Ce groupe résidant à Toulouse, organise régulièrement des rencontres et bénéficie notamment de la présence de nombreux ingénieurs ENSEEIHT au sein du pôle de compétitivité \"Aerospace Valley\"."
    ain7aero.save()

    # L'association
    councilRole0 = association.CouncilRole()
    councilRole0.member = lionel
    councilRole0.role = 0
    councilRole0.save()
    councilRole1 = association.CouncilRole()
    councilRole1.member = olivier
    councilRole1.role = 1
    councilRole1.save()
    boardRole0 = association.BoardRole()
    boardRole0.member = lionel
    boardRole0.role = 0
    boardRole0.save()
    boardRole1 = association.BoardRole()
    boardRole1.member = olivier
    boardRole1.role = 1
    boardRole1.save()

    sondage1 = sondages.Survey()
    sondage1.question = u"Quelle est votre couleur préférée ?"
    sondage1.start_date = datetime.now()
    sondage1.end_date = datetime.now() + timedelta(30)
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
    news1.description = u"""L'AIn7 travaille actuellement sur l'élaboration d'un
    nouveau portail. N'hésitez pas à apporter vos idées et vos commentaires."""
    news1.image = "data/www.jpg"
    news1.save()

    news2 = news.NewsItem()
    news2.title = "100 ans !"
    news2.description = u"""L'n7 fête cette année ces 100 ans et va  tout au
    long de l'année 2007 célébrer à travers différentes manifestations cet anniversaire"""
    news2.image = "data/Gala_N7.jpg"
    news2.save()

    looptravel = voyages.TravelType(type="Circuit")
    looptravel.save()

    boattravel = voyages.TravelType(type=u"Croisière")
    boattravel.save()

    loopandboattravel = voyages.TravelType(type=u"Circuit et croisière")
    loopandboattravel.save()

    travel1 = voyages.Travel()
    travel1.label = u"Varsovie & croisière sur la Vistule"
    travel1.start_date = date(2007,6,1)
    travel1.end_date = date(2007,6,15)
    travel1.date = "Juin 2007"
    travel1.term = 14
    travel1.type = loopandboattravel
    travel1.visited_places = "de Gdansk à Kaliningrad"
    travel1.thumbnail = "data/vistule.jpg"
    travel1.prix = 2350
    travel1.save()

    travel2 = voyages.Travel()
    travel2.label = "Japon"
    travel2.date = "Octobre 2007"
    travel2.start_date = date(2007,10,15)
    travel2.end_date = date(2007,10,27)
    travel2.term = 13
    travel2.type = looptravel
    travel2.visited_places = "Tokyo, Atami, Kyoto, Hiroshima, Nara, Osazka"
    travel2.thumbnail = "data/japon.jpg"
    travel2.prix = 3890
    travel2.description = \
u"""
<p><i>Temples et jardins, disséminés en
oasis d'ordre et de perfection formelle, dans un ruban baroque d'immenses
villes côtières conquises sur une nature omniprésente : le Japon cultive l'art
poussé à l'extrême de passer sans transition du calme absolu aux trépidations
continues de la modernité.</i></p>

<p style='text-align:center'>
<img width="287" height="190"
src="http://ain7.enseeiht.fr/Voyages/Programme%20Japon2007_fichiers/image002.gif" /></p>

<h2>15 OCTOBRE : PARIS - TOKYO</h2>

<p>Envol à 13H15 pour TOKYO sur JAPAN AIRLINES</p>

<h2>16 OCTOBRE : TOKYO</h2>

<p>Arrivée vers 11h00 dans le centre ville, et premier
aperçu de cette ville tentaculaire, en constante évolution, chaotique et
surprenante, où tradition et modernité se côtoient sans se heurter.</p>

<p>Vue sur le <b>Palais Impérial</b>. Résidence de la famille
impériale, le palais est ouvert deux fois par an&nbsp;: le jour du nouvel
et celui de l'anniversaire de l'empereur.</p>

<p>Déjeuner "&nbsp;shabu shabu&nbsp;"&nbsp;: sorte de
potée mongole à la japonaise.</p>

<p>L'après-midi, promenade dans le jardin <b>Koshikawa Korakuen</b>.
Puis, visite de la <b>Tour de Tokyo</b>, du haut de ses 333m, le
panorama sur la ville est impressionnant.</p>

<p style='text-align:center'><img width="154" height="195"
src="http://ain7.enseeiht.fr/Voyages/Programme%20Japon2007_fichiers/image004.jpg"/></p>

<h2>17 OCTOBRE : TOKYO</h2>

<p>Départ à 08h00 pour le tour de ville&nbsp;: Le matin
visite du <b>sanctuaire impériale</b> où sont
conservées les dépouilles de l'empereur Meiji et de sa femme&nbsp;; c'est sans
doute le lieu sacré shintoiste le plus important de Tokyo. Déjeuner dans une
école de Sumo (à confirmer) et visite du musée du Sumo.</p>

<p>L'après-midi, visite d'<b>Asakusa</b>, la ville basse, où se forgea la
première culture urbaine
et populaire du Japon ; ce quartier de commerces et de plaisirs accueillit les
premiers cabarets, maisons closes et cinémas ; au centre se trouve le temple
<b>Sensoji</b>, dédié à Kwannon la déesse de
la miséricorde, l'un des temples les plus fréquentés de la capitale. Puis,
visite du musée <b>Edo-Tokyo </b>qui retrace l'histoire de la ville.</p>

<p>Ou <b>croisière sur la Sumida.</b></p>

<h2>18 OCTOBRE : TOKYO - KAMAKURA - ATAMI</h2>

<p>Transfert des gros bagages à KYOTO. A 09h00, départ en bus pour KAMAKURA.
Située à une cinquantaine de kilomètres de Tokyo, cette station
balnéaire et populaire édifiée au milieu des collines verdoyantes,
capitale du Japon au XIIIème siècle abrite de nombreux temples bouddhistes
et sanctuaires shintoïstes.</p>

<p>Visite du temple <b>Kenkoji,</b> fondé au XIIIè siècle,
c'est le plus important des cinq grands temples de
Kamakura. Puis, visite du <b>sanctuaire Tsurugaoka</b>, l'un des plus beaux
sanctuaires shintoistes de la ville,
construit sur une colline au milieu de la ville et entouré d'autres édifices
interessants.</p>

<p>L'après-midi, visite du <b>Daibutsu,</b> grand
bouddha de onze mètres érigé au XIIe siècle, et d'autres temples plus sereins
comme le <b>Hokokuji</b> construit au milieu d'un bosquet de bambous.</p>

<p>Et départ en bus pour ATAMI, station thermale située à 1h30 de route.</p>

<h2>19 OCTOBRE : ATAMI - HAKONE - ATAMI</h2>

<p>Départ le matin en bus  pour HAKONE ; la ville est appréciée aussi bien pour ses nombreuses onsen que pour sa vue imprenable sur le Mont Fuji. Visite du <b>Musée de sculptures</b> en plein air.</p>

<p>Balade au milieu des fumerolles sulfureuses de la vallée de sources chaudes d'<b>Owakudani</b></p>

<p>Puis petite croisière sur le <b>lac Aishi</b>, d'où la vue sur le Mont Fujii est la plus spectaculaire, par temps clair.</p>

<p style='text-align:center'><img width="154" height="195"
src="http://ain7.enseeiht.fr/Voyages/Programme%20Japon2007_fichiers/image006.jpg"/></p>

<p>Déjeuner japonais dans un restaurant au bord du lac.
Dîner et bain japonais à l'hôtel.</p>

<h2>20 OCTOBRE : ATAMI - KYOTO</h2>

<p>Départ en train Shinkansen pour KYOTO. Déjeuner picnic à bord.</p>

<p>L'ancienne capitale de la période Heian (VIIIe - XIIe) a légué à notre
époque plus de 20 % des trésors du Japon : le plan en damier inspiré de celui
de la capitale des Tang, Chang'an, en est l'exemple ; Gion, le quartier des
plaisirs et ses très belles maisons de bois ; enfin, bien sûr les innombrables
temples, pavillons de thé et jardins.</p>

<p>L'après-midi, visites :</p>

<ul>
<li>Le temple du <b>Pavillon d'Or</b>, construit au XIVè siècle, dans un vaste
jardin, par un shogun rentré dans les ordres, le temple fut incendié en 1950
par, selon Mishima, un moine exalté par tant de beauté dans un monde si laid ;
5 ans plus tard, il fut reconstruit à l'identique selon les règles de l'art.
</li>
<li>Enfin, visite du <b>Ryoanji</b>, sans doute le plus connu et le plus pur
des jardins secs : 15 rochers entourés de sable fin.</li>
</ul>

<h2>21 OCTOBRE : KYOTO</h2>

<p>Le matin, visite du <b>château Nijo</b>, ; fondé au XVIIè, il est connu pour
la richesse de ses décors et ses parquets « rossignols », conçus pour avertir
les habitants de l'arrivée d'un intrus.</p>

<p>Puis, visite de la <b>villa Katsura</b> dont les bâtiments d'une sobriété
et d'une pureté étonnante s'intègrent magnifiquement dans ce que l'on peut
considérer parmi les plus beaux des jardins japonais.</p>

<p>En fin d'après-midi, visite du musée national connu pour ses collections de
peintures et sculptures de l'époque Heian.</p>

<h2>22 OCTOBRE : KYOTO</h2>

<p>Le matin, visite du <b>Pavillon d'Argent</b>, le Ginkakuji, construit au
XVè siècle par un shogun esthète, au milieu d'un jardin qui évoque des
paysages chinois. Puis, promenade sur le <b>chemin des philosophes</b> ;
il suit un canal bordé de cerisiers et de petits temples et sanctuaires.</p>

<p>Balade dans <b>Gion</b>, l'ancien quartier des plaisirs, où dans une
atmosphère traditionnelle se sont installés antiquaires et artisans.</p>

<p>En fin d'après-midi, montée au temple de <b>Kyomizu Dera</b>,
à la puissante armature de bois, qui offre un généreux panorama sur la ville.
</p>

<h2>23 OCTOBRE : KYOTO - HIMEJI - HIROSHIMA - MIYAJIMA</h2>

<p>Départ en train Shinkansen pour HIMEJI, visite du château avec guide
francophone, le plus grand des châteaux féodaux du Japon, inscrit au
patrimoine de l'UNESCO.</p>

<p>A 12H29, continuation en Shinkansen pour HIROSHIMA. Lunch box à bord.</p>

<p>Arrivée à 13h33 et continuation en train local pour l'embarcadère de
l'île sanctuaire de MIYAJIMA, connue pour son superbe torii vermillon érigé
dans la baie, à 150 mètres de la côte.</p>

<p>Visite du <b>sanctuaire Itsukushima</b>, dont les piliers à marée haute
semblent flotter sur l'eau ; promenade paysagère dans la vallée des Erables
et visite du jardin de l'écomusée. Croisière pour admirer le temple illuminé.
</p>

<h2>24 OCTOBRE : MIYAJIMA - HIROSHIMA - NARA</h2>

<p>Départ en train local pour HIROSHIMA.
Visite du parc et du mémorial de la Paix.</p>

<p style='text-align:center'><img width="154" height="195"
src="http://ain7.enseeiht.fr/Voyages/Programme%20Japon2007_fichiers/image008.gif"/></p>

<p>Départ en train Shinkansen  pour OSAKA</p>

<p>A l'arrivée à la gare de Shin Osaka, transfert en bus à Nara.</p>

<p style='text-align:center'><img width="154" height="195"
src="http://ain7.enseeiht.fr/Voyages/Programme%20Japon2007_fichiers/image010.jpg"/></p>

<h2>25 OCTOBRE : NARA</h2>

<p>Visite de NARA. Première capitale du pays, creuset de la civilisation
japonaise, à l'extrémité orientale de la route de la soie,
ses trésors reflètent l'influence de la Chine des Tang.</p>

<p>Promenade dans le sanctuaire shintoiste <b>Kasuga</b>, ensemble de 4
petits sanctuaires dédiés à 4 divinités différentes, dans un paysage
bucolique de collines boisées. Puis, visites du <b>Kokufuji</b>,
"le Temple Suscitant le Bonheur", qui héberge quelques bouddhas
sympathiques et bienveillants.</p>

<p>Et du <b>Todaiji</b>, dont on dit qu'il est le plus grand édifice en bois
du monde.</p>

<h2>26 OCTOBRE : NARA - MONT KOYA</h2>

<p>Départ en bus pour le MONT KOYA. Centre de pèlerinage, ce haut lieu du
bouddhisme japonais abrite dans un site exceptionnel une cinquantaine de
temples et monastères construits au IXè siècle, loin des fastes de la cour
de Kyoto.</p>

<p>Visite de la résidence du chef abbé, le temple <b>Konkobu ji</b>,
et du petit musée.</p>

<p>Et pèlerinage au <b>mausolée</b> du moine Kobo Daishi, fondateur du premier
monastère du site et inventeur de l'écriture phonétique. Et promenade dans
la grande nécropole du Koyasan, dans un bois d'arbres millénaires s'élèvent
quelques milliers de monuments à la mémoire de familles désireuses de
reposer auprès du maître.</p>

<p>Dîner végétarien et nuit au MONASTERE FUKUCHIIN</p>

<h2>27 OCTOBRE : MONT KOYA - OSAKA - PARIS</h2>

<p>Office du matin et petit déjeuner au monastère.</p>

<p>Transfert à l'aéroport ; construit il y a une dizaine d'années sur une
île artificielle par l'architecte Renzo Piano, magnifique exemple
d'architecture contemporaine.</p>

<p style='text-align:center'><b>CONDITIONS (au 15/12/2005)</b></p>

<h3>Prix par personne</h3>

<p>Prix base 16/20 personnes&nbsp;: 3 890 €</p>
<p>Supplément chambre seule&nbsp;: 350 €</p>

<h3>Ce prix comprend&nbsp;:</h3>

<ul>
<li>Les transports aériens internationaux sur JAPAN AIRLINES ou AIR France</li>
<li>Le logement en chambre double en bons hôtels de 3* et dans un monastère
(au Koyasan)</li>
<li>Les transferts en bus privé</li>
<li>Les transports en train en classe touriste comme indiqué au programme</li>
<li>La pension complète du déjeuner le jour 2 au dîner du jour 12</li>
<li>Les visites mentionnées avec guide parlant français</li>
<li>Les droits d'entrée sur les sites</li>
</ul>

<h3>Ce prix ne comprend pas&nbsp;:</h3>

<ul>
<li>Les taxes d'aéroport&nbsp;: 127 € à ce jour</li>
<li>Les boissons et dépenses personnelles &amp;
Les pourboires aux guides et aux chauffeurs</li>
<li>Les assurances</li>
</ul>

<h3>LES HOTELS</h3>

<p><b>TOKYO</b>&nbsp;: SUNSHINE CITY PRINCE HOTEL (3*) /
<a href="http://www.princehotelsjapan.com/sunshinecityprincehotel/">
http://www.princehotelsjapan.com/sunshinecityprincehotel/</a></p>

<p><b>ATAMI</b>: HOTEL IKEDA (3*) /
<a href="http://www.hotelikeda.co.jp/">http://www.hotelikeda.co.jp/</a></p>

<p><b>KYOTO</b>: KYOTO TOWER HOTEL (3*) /
<a href="http://www.asiarooms.com/japan/kyoto/tower.html">
http://www.asiarooms.com/japan/kyoto/tower.html</a></p>

<p><b>MIYAJIMA:</b>AKI GRAND HOTEL /
<a href="http://www.akigh.co.jp/">http://www.akigh.co.jp</a></p>

<p><b>NARA</b>: NARA HOTEL (3*) /
<a href="http://japaneseguesthouses.com/db/nara/narahotel.htm">
http://japaneseguesthouses.com/db/nara/narahotel.htm</a></p>

<p><b>KOYASAN</b>&nbsp;: MONASTERE FUKUCHIIN
<a href="http://www.nta-france.com/ryokanpass/fukuchiin.htm">
http://www.nta-france.com/ryokanpass/fukuchiin.htm</a></p>

"""
    travel2.save()

    travel3 = voyages.Travel()
    travel3.label = "Birmanie"
    travel3.date = u"Février 2008"
    travel3.start_date = date(2008,2,7)
    travel3.end_date = date(2008,2,20)
    travel3.term = 14
    travel3.type = loopandboattravel
    travel3.visited_places = "Ragoon, Pagan, Sagain, Mandalay"
    travel3.thumbnail = "data/birmanie.jpg"
    travel3.prix = 3550
    travel3.save()

    travel4 = voyages.Travel()
    travel4.label = u"Mongolie / Pékin"
    travel4.date = "Juin 2008"
    travel4.start_date = date(2008,6,8)
    travel4.end_date = date(2008,6,23)
    travel4.term = 15
    travel4.type = looptravel
    travel4.thumbnail = "data/mongolie.jpg"
    travel4.prix = 2760
    travel4.save()

    travel5 = voyages.Travel()
    travel5.label = "Inde - Penjab & Himachal Pradesh"
    travel5.date = "Octobre 2008"
    travel5.start_date = date(2008,10,27)
    travel5.end_date = date(2008,11,12)
    travel5.term = 17
    travel5.type = looptravel
    travel5.visited_places = "Delhi, Amristar, Dharamsala, Manali, Simla"
    travel5.thumbnail = "data/delhi.jpg"
    travel5.prix = 1900
    travel5.save()

    travel6 = voyages.Travel()
    travel6.label = "Mexique"
    travel6.start_date = date(2007,2,1)
    travel6.end_date = date(2007,2,15)
    travel6.date = "Février 2007"
    travel6.term = 15
    travel6.type = looptravel
    travel6.visited_places = "de Mexico à Cancun"
    travel6.thumbnail = "data/mexique.jpg"
    travel6.prix = 2430
    travel6.save()

    groupes_regionaux.GroupMembership(group=gr11, member=lionel).save()
    groupes_regionaux.GroupRole(group=gr11, member=lionel, type=0).save()
    groupes_regionaux.GroupMembership(group=gr11, member=alex).save()
    groupes_regionaux.GroupRole(group=gr11, member=alex, type=2).save()
    groupes_regionaux.GroupMembership(group=gr11, member=pierref).save()
    groupes_regionaux.GroupMembership(group=gr11, member=olivier).save()

    utc = vobject.icalendar.utc

    evenement1 = evenements.Event()
    evenement1.name = u"Réunion 100 ans"
    evenement1.date = datetime.now() + timedelta(10)
    evenement1.author = "Olivier Gauwin"
    evenement1.contact_email = "olivier.gauwin@alumni.enseeiht.fr"
    evenement1.location = "ENSEEIHT"
    evenement1.description = u"Organisation des événements liés au centenaire de l'ENSEEIHT."
    evenement1.publication_start = datetime.now()
    evenement1.publication_end = datetime.now() + timedelta(30)
    evenement1.image = "data/anniversaire.jpg"
    evenement1.save()
    evenement1.regional_groups.add(gr11)
    evenement1.save()

    evenement2 = evenements.Event()
    evenement2.name = u"Réunion CA"
    evenement2.date = datetime(2007, 11, 17, 10, 0)
    evenement2.author = "Lionel Porcheron"
    evenement2.contact_email = "lionel.porcheron@alumni.enseeiht.fr"
    evenement2.location = "ENSEEIHT"
    evenement2.description = "Conseil d'administration"
    evenement2.image = "data/conseil.jpg"
    evenement2.publication_start = datetime.now()
    evenement2.publication_end = datetime.now() + timedelta(30)
    evenement2.save()
    evenement2.regional_groups.add(gr11)
    evenement2.save()

    job1 = emploi.JobOffer()
    job1.reference = "XYZ270"
    job1.contact_name = "Lionel Porcheron"
    job1.contact_email = "lionel.porcheron@alumni.enseeiht.fr"
    job1.title = u"Ingénieur Java/J2EE"
    job1.description = u"""Pour l'un de nos clients Grand Compte, nous recherchons des Ingénieurs d'études Java/J2ee, sous la conduite d'un Chef de projet, vous aurez en charge la réalisation des études techniques et fonctionnelles, le développement des applications."""
    job1.experience = "1 à 2 ans"
    job1.contract_type = 0
    job1.is_opened = True
    job1.checked_by_secretariat = True
    job1.office = anywareoffice
    job1.save()
    job1.track.add(n7info)
    job1.save()

    job2 = emploi.JobOffer()
    job2.reference = "XYZ271"
    job2.title = u"Ingénieur d'études Oracle, UNIX Expérimenté"
    job2.description = u"""Nous recherchons un ingénieur d'étude et de développement expérimenté pour un client grand compte. Mission :
    - Maintenance et développement sur une application sensible.
    -Développement de nouvelles fonctionnalités."""
    job2.experience = "2 à 3 ans"
    job2.contract_type = 0
    job2.is_opened = True
    job2.checked_by_secretariat = True
    job2.office = priceminister
    job2.save()
    job2.track.add(n7info)
    job2.save()

    job3 = emploi.JobOffer()
    job3.reference = "XYZ272"
    job3.title = u"Ingénieur étude et développement décisionnel"
    job3.description = u"""Dans le cadre de nos projets réalisés pour nos clients grands comptes, sous la conduite d'un Chef de projet, vous serez chargé de réaliser des études techniques et fonctionnelles, de développer des applications, d'élaborer les plans d'intégration."""
    job3.experience = "1 à 2 ans"
    job3.contract_type = 1
    job3.is_opened = True
    job3.checked_by_secretariat = True
    job3.office = anywareoffice
    job3.save()
    job3.track.add(n7info)
    job3.save()

    job4 = emploi.JobOffer()
    job4.reference = "XYZ273"
    job4.title = u"Ingénieur SI support produit"
    job4.description = u"""Intégré au sein de l'équipe « Formes de Vente » (15 personnes) et sous la direction d'un Responsable d'Equipe, vous garantissez le bon fonctionnement des produits à votre charge dans le système d'information."""
    job4.experience = "1 à 2 ans"
    job4.contract_type = 2
    job4.is_opened = False
    job4.checked_by_secretariat = True
    job4.office = anywareoffice
    job4.save()
    job4.track.add(n7hydro)
    job4.save()

    job5 = emploi.JobOffer()
    job5.reference = "XYZ274"
    job5.title = u"Ingénieurs développement JAVA/J2EE"
    job5.description = u"""Nous souhaitons renforcer notre pôle de compétences NTIC Java J2EE : De formation informatique Bac+4/5, vous êtes aujourd'hui un Ingénieur débutant ou expérimenté et vous bénéficiez d'une réelle maîtrise des environnements de développement NTIC."""
    job5.experience = "0 à 3 ans"
    job5.contract_type = 2
    job5.is_opened = True
    job5.checked_by_secretariat = True
    job5.office = lepaysdesschtroumpfs
    job5.save()

    notif1 = manage.Notification()
    notif1.title = "Un exemple de notification !"
    notif1.details = "Ceci est une exemple de notification..."
    notif1.save()
