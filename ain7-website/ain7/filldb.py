# -*- coding: utf-8
#
# filldb.py
#
#   Copyright © 2007-2009 AIn7 Devel Team
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

import vobject
import sys
import os

from datetime import date, datetime, timedelta

from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site

import ain7.adhesions.models as adhesions
import ain7.annuaire.models as annuaire
import ain7.association.models as association
import ain7.emploi.models as emploi
import ain7.evenements.models as evenements
import ain7.groupes_professionnels.models as groupes_professionnels
import ain7.groupes_regionaux.models as groupes_regionaux
import ain7.manage.models as manage
import ain7.pages.models as pages
import ain7.news.models as news
import ain7.search_engine.models as search_engine
import ain7.sondages.models as sondages
import ain7.voyages.models as voyages


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

    subscription_conf9 = adhesions.SubscriptionConfiguration(type=9, dues_amount=160, newspaper_amount=15)
    subscription_conf9.save()

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

    olivier_diploma1 = emploi.DiplomaItem()
    olivier_diploma1.ain7member = olivier_ain7member
    olivier_diploma1.diploma = u"Diplôme d'ingenieur en informatique et mathématiques appliquées"
    olivier_diploma1.save()

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
    councilRole0.board_member = True
    councilRole0.save()
    councilRole1 = association.CouncilRole()
    councilRole1.member = olivier
    councilRole1.role = 1
    councilRole1.board_member = True
    councilRole1.save()

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

    text1 = pages.Text()
    text1.title = u"Le réseau AIN7 : une force collective et des atouts au service de chaque diplômé ENSEEIHT"
    text1.body = u"""<img src="/site_media/images/logo_ain7.png" class="image" alt="Big Image" />
<p>L'ENSEEIHT a fêté son centenaire en 2007. Naturellement issue des premières promotions 
d'ingénieurs de l'école, l'AIN7 a, au fil des décennies, toujours œuvré au service de tous 
les diplômés, elle a développé et entretient entre eux des liens professionnels et amicaux, 
elle contribue à des actions en profondeur, au sein de l'Ecole et dans le monde des affaires, 
pour améliorer et optimiser l'image et la notoriété de notre communauté.</p>
<p>12 000 ingénieurs ont reçu, depuis l'origine, le diplôme d'ingénieur. Près de 10 000 sont 
en activité… ceci dans tous les grands secteurs de l'Economie. Cela crée un potentiel de premier 
plan et l'AIN7 se place en véritable catalyseur…</p>
<p>En ce début de 21ème siècle, réseau est obligatoirement synonyme de web. Conscient de ce fait 
incontournable, l'AIN7 prend en ce début 2009 plusieurs initiatives majeures :</p>
<ul>
<li>une présence renforcée sur les principaux réseaux communautaires professionnels : en particulier 
Viadeo, qui va ouvrir une communauté officielle supportée par l'AIN7.</li>
<li>notre nouveau site, visitez le régulièrement : il vous tiendra informé de toutes nos initiatives… 
et n'oubliez pas, l'AIN7 c'est VOUS. Venez rejoindre le noyau de volontaires qui font vivre notre communauté, 
et si vous ne trouvez pas dans nos activités, celle que vous attendez, pourquoi ne pas venir la susciter 
en nous rejoignant ?</li>
</ul>

<p><b>Jean-François Perret<br/>
Président AIN7</b></p>
"""
    text1.save()

    text2 = pages.Text()
    text2.title = u"L'ENSEEIHT"
    text2.body = u"""<img src="/site_media/images/n7_small.png" class="image" alt="ENSEEIHT" />
<p>L'ENSEEIHT (prononcer « N7 ») est l'École nationale supérieure d'électrotechnique, d'électronique, 
d'informatique, d'hydraulique et des télécommunications. Elle appartient à l'Institut national polytechnique
de Toulouse.</p>
<p>École d'ingénieurs en convention avec l'École polytechnique, l'ENSEEIHT est actuellement structurée en cinq
filières, comprenant chacune un département de formation et un laboratoire de recherche étroitement lié.</p>
<p>Les cinq filières d'enseignement sont les suivantes :</p>
<ul style="list-style-type: square; margin: 1ex; margin-left: 4ex">
  <li>Génie électrique et automatique</li>
  <li>Électronique et Traitement du signal</li>
  <li>Informatique et Mathématiques appliquées</li>
  <li>Hydraulique et Mécanique des fluides</li>
  <li>Télécommunications et Réseaux</li>
</ul>
<p>L'ENSEEIHT fait partie du groupe des ENSI et est la plus importante ENSI en termes d'élèves diplomés chaque 
année (près de 400).</p>
"""
    text2.save()

    text3 = pages.Text()
    text3.title = u"L'AIn7..."
    text3.body = u"""<h4>Des offres d'emploi</h4>
<p>L'AIN7 gère un service Emplois-Carrières au bénéfice de l'Ecole et de ses membres :</p>
<ul>
<li>Mise à disposition des offres d'emploi et leur édition périodique,</li>
<li>Tenue à jour d'un fichier des ingénieurs en recherche de situation,</li>
<li>Réponse à des demandes ou des propositions urgentes.</li> 
</ul>
 
<h4>Une assistance personnalisée</h4>
<p>Les ingénieurs qui le souhaitent peuvent réaliser un auto bilan à l'aide d'un document élaboré par l'Association, leur donnant ainsi la possibilité d'affiner leur projet professionnel. Ils peuvent également solliciter les conseils d'anciens qui disposent de compétences dans les domaines d'activité concernés. Par ailleurs, l'Association peut apporter son soutien à ceux qui doivent faire face à des situations économiques difficiles.</p>

<h4>Des correspondants d'entreprise</h4>
<p>L'Association anime un réseau de correspondants d'entreprise constitué d'anciens élèves qui exercent des responsabilités dans des entreprises où l'on recense un nombre significatif d'ingénieurs ENSEEIHT. Ils y sont les interlocuteurs privilégiés de l'Association, notamment pour faciliter les échanges d'information avec leur entreprise ainsi que l'accès et l'intégration des nouveaux embauchés. Ils peuvent contribuer également à favoriser l'organisation et l'accueil de stages pour les élèves et la conclusion de contrats de recherche avec les laboratoires de l'Ecole.</p>

<h4>Des groupes professionnels</h4>
<p>Leur vocation est de permettre des échanges entre les ingénieurs exerçant leur activité dans une même spécialité (TIC, Energie,…). Des rencontres et des colloques facilitent la confrontation de leurs expériences et de leurs points de vue avec ceux d'intervenants extérieurs. Plus généralement, l'Association est attentive à ce que la meilleure osmose se fasse entre ses membres et leur environnement socio-professionnel.</p>

<p>L'Association est présente dans :</p>
<p><b>LES ORGANISMES REPRÉSENTATIFS DE LA PROFESSION D'INGÉNIEUR</b></p>
<p>L'Association est intégrée dans le tissu représentatif du monde des ingénieurs. Elle est membre du CNISF, Conseil National des Ingénieurs et Scientifiques de France, et participe aux travaux de ses Unions Régionales, les URIS. Cette présence au CNISF est particulièrement active depuis plusieurs années : un de nos camarades, Jean-Pierre Laborie a été Vice-Président du CNISF en charge des actions régionales… Actuellement, Jean-François Perret (Président de l'AI) et Isabelle Avenas (Présidente du Groupe Parisien) siègent au Conseil d'Administration du CNISF.</p>
<p>L'Association est particulièrement attachée à la valorisation du titre d'ingénieur et à sa reconnaissance au sein de l'Union Européenne. Elle est également attentive au respect de la place des Grandes Ecoles d'Ingénieurs dans l'évolution du système éducatif français. Les ingénieurs ENSEEIHT figurent dans le Répertoire Français des Ingénieurs, géré par le CNISF et accessible sur <a href="http://cnisf.org">le site Internet du CNISF</a>.</p>

<p><b>LES ENTREPRISES</b></p>
<p>Avec une approche dynamique du monde professionnel, l'Association offre aux entreprises désireuses d'attirer et de recruter des ingénieurs ENSEEIHT la possibilité de se faire mieux connaître par :</p>
<ul>
<li>des espaces publicitaires: dans son Annuaire, dans sa revue trimestrielle, CANAL N7, sur son site Internet,</li>
<li>des tables rondes réunissant professionnels, enseignants et élèves ingénieurs de l'Ecole,</li>
<li>des visites et des forums de recrutement, en liaison avec l'Ecole.</li>
</ul>

<p><b>LES MÉDIAS</b></p>
<p>Afin de développer l'image du diplôme, de l'Ecole et de ses ingénieurs, l'Association s'adresse, par l'intermédiaire de la presse spécialisée, à différents publics, acteurs directs ou prescripteurs, pour :</p>
<ul>
<li>actualiser l'information des élèves des classes préparatoires, de leurs parents et de leurs professeurs,</li>
<li>faciliter la recherche d'emploi et l'évolution des carrières vers des responsabilités toujours plus attractives et valorisantes,</li>
<li>délivrer aux responsables d'entreprises, directeurs des ressources humaines et aux cabinet spécialisés, les informations utiles pour leurs choix de recrutement.</li>
</ul>

<p>L'Association prête une attention soutenue à la vie de l'Ecole.</p>
<p>Elle est représentée au Conseil d'Administration de l'Ecole par 2 représentants (actuellement Michel Canon et Pierre Hugot) ; un ingénieur ENSEEIHT, Bernard Leblanc, président le Conseil d'Administration où elle apporte son expertise de la connaissance des besoins des entreprises en matière de qualification des ingénieurs. Elle est partie prenante dans l'évolution des enseignements, en participant notamment à des commissions thématiques de ce Conseil.</p>
<p>Elle organise des rencontres régulières avec les filières de l'Ecole et le Corps professoral, qui constituent un lieu d'échange et de meilleure compréhension réciproque. Cette dynamique va être renforcée en 2009 avec :</p>
<ul>
<li>Programme de participation de l'AIN7 à l'organisation d'informations sur les métiers d'ingénieurs à destination des élèves dans chaque filière</li>
<li>Participation active aux "mini-forums" Etudiants/Entreprises</li>
<li>Pour préparer leur recherche de stages ou d'un premier emploi, les élèves qui le souhaitent peuvent recourir à l'expérience de leurs aînés.</li>
<li>Réseaux d'accueil des élèves stagiaires ou débutants en entreprises</li>
<li>Afin de mener un dialogue sur son futur métier, chaque élève peut établir une relation interpersonnelle avec un de ses anciens.</li>
</ul>
<p>En outre, l'Association apporte son aide au Bureau des Elèves pour la recherche de partenaires associés aux manifestations et aux événements qu'organisent les étudiants : Festival N7, week-end d'intégration, tournois inter Grandes Ecoles, Junior-Entreprise, activités festives ou professionnelles,…</p>

<p>L'Association favorise le renforcement des liens entre tous ses membres.</p>
<p><b>AU PLAN NATIONAL</b></p>
<p>Des manifestations de prestige sont organisées régulièrement à Toulouse et à Paris, permettant notamment la rencontre de personnalités du monde de l'entreprise. En particulier, le diner-débat annuel co-organisé au Sénat par l'AIN7 et l'Ecole rencontrent chaque année un grand succès.</p>

<p><b>AU PLAN RÉGIONAL</b></p>
<p>Les adhérents d'une même région sont conviés à diverses activités : rencontres autour d'un thème, conférences, visites techniques et culturelles, repas conviviaux. Les initiatives sont riches et variées.</p>

<p><b>AU PLAN INTERNATIONAL</b></p>
<p>La communication entre ceux qui exercent leurs responsabilités professionnelles dans la même zone géographique est facilitée, leur donnant ainsi la possibilité d'échanger leurs expériences. Dans les pays où l'on dénombre la présence de nombreux ingénieurs ENSEEIHT, par exemple aux Etats-Unis et au Canada, des rencontres sont organisées. Cependant, de plus en plus, le web devient l'élément privilégié d'échange de nos communautés expatriées. En 2009, le lancement de plusieurs initiatives "web" va renforcer ce lien.</p>
<p>L'Association propose aussi des voyages qui sont autant d'occasions d'enrichir les relations entre les participants, dans un contexte particulièrement agréable et sympathique. La variété des destinations : Europe, Asie, Afrique, Amérique, le pittoresque des pays découverts sont autant d'atouts qui incitent ses membres à se retrouver et à partager émotions et souvenirs communs.</p>
"""

    text3.save()

    text4 = pages.Text()
    text4.title = u"Statuts de l'association"
    text4.body = u"""<h4>I - BUT ET COMPOSITION DE L'ASSOCIATION</h4>

<h5>Article premier</h5>

L'Association dite AIN7, ASSOCIATION des INGENIEURS de l'ECOLE NATIONALE SUPERIEURE d'ELECTROTECHNIQUE, d'ELECTRONIQUE, d'INFORMATIQUE et d'HYDRAULIQUE de TOULOUSE (ENSEEIHT-IET), fondée en 1912, a pour but :

<ul>
    <li>D'entretenir et de resserrer les liens d'amitié et de solidarité qui existaient à l'Ecole, et de relier les nouvelles promotions aux précédentes.</li>
    <li>De faciliter aux anciens élèves l'accès aux situations auxquelles ils peuvent prétendre. Dans ce but, tous les Membres de l'Association s'engagent à signaler à l’Association les emplois vacants qu'ils peuvent connaître.</li>
    <li>De procurer à ses Membres le moyen d'étendre leurs connaissances par les communications, travaux et documents qui seront présentés aux réunions et discutés s'il y a lieu.</li>
    <li>De développer l'action sociale au moyen de prêts gratuits ou de dons aux Membres de l'Association et le cas échéant, à leurs père, mère, veuf, veuve ou enfants dans le besoin.</li>
</ul>

Sa durée est illimitée.

Elle a son Siège à Toulouse, à l'ECOLE NATIONALE SUPERIEURE d'ELECTROTECHNIQUE, d'ELECTRONIQUE, d'INFORMATIQUE et d'HYDRAULIQUE.

<h5>Article 2</h5>

<p>Les moyens d'action de l'Association sont notamment : un annuaire, des moyens de diffusion d'information dont un journal périodique, l'animation de groupes régionaux et l'animation de manifestations visant à atteindre les objectifs visés à l'article 1.</p>

<h5>Article 3</h5>

<p>L'Association se compose de membres actifs, de membres associés, de membres affiliés et de membres d'honneur.</p>

<ul>
   <li>Sont MEMBRES ACTIFS les ingénieurs diplômés de l'IET, de l'ENSEEHT, de l'ENSEIHT ou de l'ENSEEIHT à jour de leur cotisation.</li>
   <li>Sont MEMBRES ASSOCIES les diplômés à la suite d'une des formations suivies à l'IET, l'ENSEEHT, l'ENSEIHT ou l'ENSEEIHT autres que celles sanctionnées par le diplôme d'ingénieur de l'Ecole et dont la liste est établie par l'Assemblée Générale ordinaire. Les diplômés d'une section spéciale de l'Ecole sont membres associés s'ils sont à jour de leur cotisation.</li>
   <li>Sont MEMBRES AFFILIES durant leur formation à l'ENSEEIHT, les étudiants préparant un diplôme qui leur permettra de devenir membre actif ou membre associé et payant la cotisation correspondante.</li>
   <li>Un membre actif ou associé peut, de plus, porter le titre de "BIENFAITEUR" si, pour l'année en cours, il verse la cotisation correspondante.</li>
   <li>Le montant des cotisations est fixé par l'Assemblée Générale.</li>
</ul>

<p>Le titre de MEMBRE d'HONNEUR peut être décerné par le Conseil d'Administration aux personnes qui rendent ou qui ont rendu des services signalés à l'Association. Ce titre confère aux personnes qui l'ont obtenu, le droit de faire partie de l'Assemblée Générale sans être tenues de payer une cotisation.</p>

<h5>Article 4</h5>

<p>La qualité de membre de l'Association se perd :</p>

<ul>
   <li>par la radiation prononcée pour motif grave par le Conseil d'Administration, sauf recours à l'Assemblée Générale. Le membre concerné est préalablement appelé à fournir ses explications ;</li>
   <li>par le non-paiement de la cotisation (sauf pour ceux qui en sont dispensés).</li>
</ul>

<h4>II - ADMINISTRATION ET FONCTIONNEMENT</h4>

<h5>Article 5</h5>

<p>L'Association est administrée par un Conseil composé de 18 à 24 membres élus par l'Assemblée Générale au scrutin secret pour 2 ans.</p>

<p>La composition de ce Conseil est la suivante :</p>

<ul>
    <li>18 à 22 membres élus parmi les membres actifs ;</li>
    <li>au plus 2 membres élus parmi les membres associés.</li>
</ul>

<p>Les membres sortants sont immédiatement rééligibles. Le renouvellement des membres élus a lieu par ouverture de 11 postes de membres actifs et 1 poste de membre associé tous les ans.</p>

<p>En cas de vacance provoquée par le départ d'un membre ou insuffisance de candidats conduisant à moins de 18 membres élus, le Conseil peut combler provisoirement chaque poste vacant par cooptation d'un nouveau membre actif ou associé. Son mandat prendra fin à l'époque où devrait normalement expirer le mandat du membre remplacé.</p>

<p>Le Conseil élit à bulletin secret, tous les ans, parmi ses membres, un bureau composé au moins d'un Président, de deux vice-présidents, d'un secrétaire, d'un trésorier et d'un trésorier-adjoint. Un même membre ne peut être Président plus de trois années consécutives. Le Président est obligatoirement un membre actif.</p>

<h5>Article 6</h5>

<p>Le Conseil se réunit une fois au moins tous les six mois et chaque fois qu'il est convoqué par son Président ou sur la demande du quart de ses membres.</p>

<p>La présence du tiers au moins des membres élus du Conseil d'Administration est nécessaire pour la validité des délibérations.</p>

<p>Chaque administrateur peut se faire représenter à une séance du Conseil par un autre administrateur. Les mandataires doivent être porteurs lors de chaque séance du Conseil d'un mandat écrit et nominatif. Un administrateur ne peut représenter qu'un seul membre absent.</p>

<p>Les Présidents de groupes régionaux dûment constitués peuvent participer au Conseil avec voix consultative.</p>

<p>Le Conseil peut appeler les personnes de son choix à assister avec voix consultative de façon régulière ou exceptionnelle à ses réunions.</p>

<p>Les agents rétribués de l'Association peuvent être appelés par le Président à assister avec voix consultative, aux séances de l'Assemblée Générale et du Conseil d'Administration.</p>

<p>Il est tenu procès-verbal des séances.</p>

<p>Les procès-verbaux sont signés par le Président et le Secrétaire. Ils sont établis sans blancs, ni ratures sur des feuilles numérotées et conservées au siège de l'Association.</p>

<h5>Article 7</h5>

<p>Les membres du Conseil d'Administration ne peuvent recevoir aucune rétribution en raison des fonctions qui leur sont confiées.</p>

<p>Des remboursements de frais sont seuls possibles. Ils doivent faire l'objet d'une décision expresse du Conseil d'Administration, statuant hors de la présence des intéressés : des justificatifs doivent être produits qui font l'objet de vérification.</p>

<h5>Article 8</h5>

<p>L'Assemblée Générale de l'Association comprend : les membres actifs et les membres associés avec voix délibérative. Les membres d’honneur et les membres affiliés peuvent assister à l’Assemblée Générale.</p>

<p>Elle se réunit au moins une fois par an et chaque fois qu'elle est convoquée par le Conseil d'Administration ou sur la demande au moins du quart de ses membres. Son ordre du jour est réglé par le Conseil d'Administration.</p>

<p>Son bureau est celui du Conseil.</p>

<p>Lors de l'Assemblée Générale, ses membres entendent les rapports sur la gestion du Conseil d'Administration, sur la situation financière de l'Association, approuvent les comptes de l'exercice clos, votent le budget de l'exercice suivant, délibèrent sur les questions mises à l'ordre du jour et pourvoient, s'il y a lieu, au renouvellement des membres du Conseil d'Administration.</p>

<p>Le rapport annuel et les comptes sont communiqués chaque année aux membres actifs et aux membres associés de l'Association.</p>

<p>Il est tenu procès verbal des séances. Les procès verbaux sont signés par le Président et le Secrétaire. Ils sont établis sans blancs ni ratures, sur des feuillets numérotés et conservés au siège de l'Association.</p>

<p>Chaque membre présent ne peut détenir plus d'un pouvoir en sus du sien.</p>

<p>En cas de partage des voix, celle du Président est prépondérante.</p>

<p>Sauf application des dispositions de l'article 6, les agents rétribués, non-membres de l'Association n'ont pas accès à l'Assemblée Générale.</p>

<h5>Article 9</h5>

<p>Le Président représente l'Association dans tous les actes de la vie civile. Il ordonnance les dépenses. Il peut donner délégation dans des conditions qui sont fixées par le règlement intérieur.</p>

<p>En cas de représentation en justice, le président ne peut être remplacé que par un mandataire agissant en vertu d'une procuration spéciale.</p>

<p>Les représentants de l'Association doivent jouir du plein exercice de leurs droits civils.</p>

<h5>Article 10</h5>

<p>Les délibérations du Conseil d'Administration relatives aux acquisitions, échanges et aliénations d'immeubles nécessaires au but poursuivi par l'association, constitutions d'hypothèques sur les dits immeubles, baux excédant neuf années, aliénations de biens rentrant dans la dotation et emprunts doivent être approuvés par l'Assemblée Générale.</p>

<h5>Article 11</h5>

<p>Les délibérations du Conseil d'Administration relatives à l'acceptation des dons et legs ne sont valables qu'après approbation administrative donnée dans les conditions prévues par l'article 910 du code civil, l'article 7 de la loi du 4 février 1901 et le décret n°66-388 du 13 juin 1966 modifiés.</p>

<p>Les délibérations de l'Assemblée Générale relatives aux aliénations de biens mobiliers et immobiliers dépendant de la dotation, à la constitution d'hypothèques et aux emprunts, ne sont valables qu'après approbation administrative.</p>

<h5>Article 12</h5>

<ul>
   <li>Des groupes régionaux sans autonomie officielle peuvent être créés à l'initiative de membres habitant une même région. Un même territoire ne peut être couvert que par un seul groupe régional. Dix membres actifs ou associés sont nécessaires pour constituer un groupe régional.</li>
   <li>La demande de création ou de modification de la couverture géographique d'un groupe régional doit être présentée:
   <ul>
       <li>en délimitant la région couverte par le groupe</li>
       <li>en décrivant la composition de son bureau et le mode de désignation de son président.</li>
   </ul>
   </li>
   <li>La création, la modification de la couverture géographique d'un groupe régional est votée par l'Assemblée Générale sur proposition du Conseil d'Administration de l'Association. Ce point doit figurer à l'ordre du jour de la convocation à l'Assemblée Générale ordinaire. La délibération doit être notifiée au Préfet dans le délai de huitaine.</li>
   <li>La composition du bureau doit être adressée tous les ans au Conseil d'Administration. Le Président du groupe régional participe au Conseil d'Administration avec voix consultative.</li>
   <li>Le groupe régional bénéficie du soutien logistique du secrétariat de l'Association. Il adresse au secrétaire du Conseil d'Administration copie de toutes les circulaires locales à l'attention des membres de son groupe.</li>
   <li>La présence d'un trésorier au sein de son bureau est un préalable à l'engagement de dépenses par un groupe régional. Les dépenses du groupe régional sont soumises à l'approbation du Conseil d'Administration. Le trésorier du groupe fait parvenir au Conseil d'Administration en décembre de chaque année le budget prévisionnel de son groupe pour l'année suivante et en janvier le bilan de l'année écoulée. Il fournit au trésorier de l'Association tous les éléments nécessaires à la tenue de la comptabilité du groupe régional.</li>
   <li>En cas de non respect de ces clauses, le Conseil d'Administration de l'Association peut proposer à l'Assemblée Générale la dissolution du groupe régional.</li>
</ul>

<h4>III - DOTATION, RESSOURCES ANNUELLES</h4>

<h5>Article 13</h5>

<p>La dotation comprend :</p>

<ol>
   <li>une somme de 3 000 F, constituée en valeurs nominatives placées conformément aux prescriptions de l'article suivant ;</li>
   <li>les immeubles nécessaires au but recherché par l'Association ainsi que des bois, forêts ou terrains à boiser ;</li>
   <li>les capitaux provenant des libéralités, à moins que l'emploi n'en ait été autorisé;</li>
   <li>le dixième au moins annuellement capitalisé, du revenu net des biens de l'Association ;</li>
   <li>la partie des excédents de ressources qui n'est pas nécessaire au fonctionnement de l'Association pour l'exercice suivant.</li>
</ol>

<h5>Article 14</h5>

<p>Tous les capitaux mobilisés, y compris ceux de la dotation, sont placés en titres nominatifs, en titres pour lesquels est établi le bordereau de références nominatives prévu à l'article 55 de la Loi 87-416 du 17 juin 1987 sur l'épargne ou en valeurs admises par la Banque de France en garantie d'avance.</p>

<h5>Article 15</h5>

<p>Les recettes annuelles de l'Association se composent :</p>

<ol>
   <li>du revenu de ses biens à l'exception de la fraction prévue a l'alinéa 4 de l'article 13 ;</li>
   <li>des cotisations et souscriptions de ses membres ;</li>
   <li>des subventions de l'Etat, des Régions, des Départements, des Communes et des Etablissements Publics ;</li>
   <li>du produit des libéralités dont l'emploi est autorisé au cours de l'exercice ;</li>
   <li>des ressources créées à titre exceptionnel et, s'il y a lieu, avec l'agrément de l'autorité compétente ;</li>
   <li>du produit des rétributions perçues pour service rendu.</li>
</ol>

<h5>Article 16</h5>

<p>Il est tenu une comptabilité faisant apparaître essentiellement un compte de résultat, un bilan et une annexe.</p>

<p>Chaque établissement de l'Association doit tenir une comptabilité distincte qui forme un chapitre spécial de la comptabilité d'ensemble de l'Association.</p>

<p>Il est justifié, chaque année auprès du préfet du département, du Ministre de l'Intérieur et du Ministre chargé de l’Enseignement Supérieur, de l'emploi des fonds provenant de toutes les subventions accordées au cours de l'exercice écoulé.</p>

<h4>IV - MODIFICATION DES STATUTS ET DISSOLUTION</h4>

<h5>Article 17</h5>

<p>Les statuts peuvent être modifiés par l'Assemblée Générale sur la proposition du conseil d'administration ou sur la proposition du dixième des membres dont se compose l'assemblée générale.</p>

<p>Dans l'un et l'autre cas, les propositions de modifications sont inscrites à l'ordre du jour de la prochaine Assemblée Générale, lequel doit être envoyé à tous les membres de l'assemblée au moins 30 jours à l'avance.</p>

<p>L'assemblée doit se composer du quart au moins, des membres en exercice. Si cette proportion n'est pas atteinte, l'assemblée est convoquée de nouveau, mais à quinze jours au moins d'intervalle, et cette fois, elle peut valablement délibérer, quel que soit le nombre des membres présents ou représentés.</p>

<p>Dans tous les cas, les statuts ne peuvent être modifiés qu'à la majorité des deux tiers des membres présents ou représentés.</p>

<h5>Article 18</h5>

<p>L'Assemblée Générale, appelée à se prononcer sur la dissolution de l'Association et convoquée spécialement à cet effet, dans les conditions prévues à l'article précédent, doit comprendre, au moins la moitié plus un, des membres en exercice.</p>

<p>Si cette proportion n'est pas atteinte, l'assemblée est convoquée de nouveau, mais à quinze jours au moins d'intervalle, et cette fois, elle peut valablement délibérer, quel que soit le nombre des membres présents ou représentés.</p>

<p>Dans tous les cas, la dissolution ne peut être votée qu'à la majorité des deux tiers des membres présents ou représentés.</p>

<h5>Article 19</h5>

<p>En cas de dissolution, l'Assemblée Générale désigne un ou plusieurs commissaires, chargés de la liquidation des biens de l'association. Elle attribue l'actif net à un ou plusieurs établissements analogues, publics, reconnus d'utilité publique ou à des établissements visés à l'article 6, alinéa 2 de la Loi du 1er juillet 1901 modifiée.</p>

<h5>Article 20</h5>

<p>Les délibérations de l'Assemblée Générale prévues aux articles 17, 18 et 19 sont adressées sans délai, au Ministre de l'Intérieur et au Ministre chargé de l’Enseignement Supérieur.</p>

<p>Elles ne sont valables qu'après l'approbation du Gouvernement.</p>

<h4>V - SURVEILLANCE ET REGLEMENT INTERIEUR</h4>

<h5>Article 21</h5>

<p>Le Président doit faire connaître dans les trois mois, à la Préfecture du Département ou à la Sous-Préfecture de l'Arrondissement où l'Association a son siège social, tous les changements survenus dans l'administration ou la direction de l'Association.</p>

<p>Les registres de l'Association et ses pièces de comptabilité sont présentées sans déplacement, sur toute réquisition du Ministre de l'Intérieur ou du Préfet, à eux-mêmes ou à leur délégué ou à tout fonctionnaire accrédité par eux.</p>

<p>Le rapport annuel et les comptes - y compris ceux des groupes régionaux - sont adressés chaque année au Préfet du Département, au Ministre de l'Intérieur et au Ministre chargé de l’Enseignement Supérieur.</p>

<h5>Article 22</h5>

<p>Le Ministre de l'Intérieur et le Ministre chargé de l’Enseignement Supérieur ont le droit de faire visiter par leurs délégués les établissements fondés par l'Association et de se faire rendre compte de leur fonctionnement.</p>

<h5>Article 23</h5>

<p>Le règlement intérieur préparé par le Conseil d'Administration et adopté par l'Assemblée Générale est adressé à la préfecture du département. Il ne peut entrer en vigueur ni être modifié qu'après approbation du Ministre de l’Intérieur.</p>
"""
    text4.save()

    text5 = pages.Text()
    text5.title = u"Le secrétariat permanant"
    text5.body = u"""<b>Coordonnées globales :</b>
<p>
A.I.N.7<br/>
2 rue Charles Camichel, BP 7122,<br/>
31071 Toulouse cedex 7</p>

<p>Fax : 05 61 62 09 76</p>
<p>Courriel : <a href="mailto:ain7@ain7.fr">ain7@ain7.fr</a></p>

<b>Nos deux secrétaires :</b>
<ul>
<li>Sylvie Henric - <a href="mailto:sylvie.henric@ain7.fr">sylvie.henric@ain7.fr</a> - Tél : 05 61 58 82 88</li>
<li>Frédérique Forestie - <a href="mailto:frederique.forestie@ain7.fr">frederique.forestie@ain7.fr</a> -  Tél : 05 61 58 82 13</li>
</ul>
"""
    text5.save()

    text6 = pages.Text()
    text6.title = u"A propos du site"
    text6.body = u"""<p>Pour remonter un problème au sujet du site contactez le <a href="mailto:webmaster@ain7.fr">webmaster</a>.</p>
<p>Pour de plus amples renseignements au sujet de ce site, n'hésitez pas à consulter la page <a href="/apropos/">a propos</a>.</p>
"""
    text6.save()

    text7 = pages.Text()
    text7.title = u"Les groupes régionaux"
    text7.body = u"""<h4>Présentation</h4>

<p>Le Groupe Régional est le représentant de l’association nationale dans la région. Il assure le relais des opérations de niveau national et développe les opérations de niveau régional.</p>
<p>Pour réaliser ses missions, le groupe dispose du soutien de l’association nationale.</p>
<ul>
<li>soutien financier par l’octroi d’un budget en appui d’un plan d’actions validé en conseil,</li>
<li> soutien matériel, par la mise à disposition du secrétariat, </li>
<li>soutien en informations, par la diffusion des comptes-rendus du conseil, du bureau, flash-infos, programmes et convocations des autres groupes régionaux.</li>
</ul>
<p>En contrepartie le groupe a un devoir d’information du conseil d’administration, de transparence et de rigueur.</p>
<p>Un groupe régional ne dispose pas de l’autonomie juridique ou financière : il s’agit par délégation de l’association nationale. Les Présidents des groupes régionaux sont invités aux réunions du conseil d’administration et donc associés aux débats d’orientation de la vie de l’association.</p>
<p>Chaque groupe régional, en fonction de sa taille, du profil de ses adhérents (demandeurs d’emploi, actifs, retraités…), des partenariats qu’il peut établir (existence d’une maison des ingénieurs) choisit son plan d’action. Sont énumérés, ci-après, des thèmes d’actions qui pourraient être communs à tous les groupes.</p>

<h4>Représentation</h4>
<p>Le groupe régional assure le relais en région de l’association nationale.</p>
<p>Le Président et le bureau du groupe informent le secrétariat de l’association nationale de leurs actions et communiquent un compte-rendu des réunions de bureau, manifestations et assemblés générales.</p>

<h4>Adhésion</h4>
<p>Le secrétariat de l’AIN7 adresse régulièrement aux groupes régionaux des listes à jour (membres actifs, associés et autres).</p>
<p>Tout cotisant à l’association, ainsi que chaque élève de 3ième année est informé de l’existence et des coordonnées de son groupe régional.</p>
<p>Chaque groupe a un devoir de développement du nombre des adhérents.</p>

<h4>Finances</h4>
<p>L’association nationale peut ouvrir un compte par groupe régional avec délégation au Président et au Trésorier du groupe. Le conseil d’administration arrête le budget annuel du groupe sur proposition du bureau.</p>

<p>Le budget est destiné :</p>
<ul>
<li>au développement du groupe,</li>
<li>à l’aide aux demandeurs d’emploi : participations aux opérations régionales, invitations aux manifestations,</li>
<li>aux frais de fonctionnement.</li>
</ul>

<h4>Accueil solidarité</h4>
<p>Le groupe est la structure d’accueil des ingénieurs en région :</p>
<ul>
<li>accueil des nouveaux diplômés,</li>
<li>accueil des ingénieurs mutés,</li>
<li>échange d’informations entre actifs,</li>
<li>point de rencontre des retraités.</li>
</ul>

<h4>Emloi</h4>
<p>Chaque groupe reçoit le fichier des demandeurs d’emploi et s’associe aux initiatives diverses régionales.</p>

<h4>Animation manifestations</h4>
<p>Le groupe a la responsabilité de l’aimation et de l’information régionales : organisation de rencontres, visites, manifestations.</p>

<h4>Organisation statutaire</h4>
<p>Chaque année est organisée une assemblée générale du groupe avec élection d’un bureau composé au minimum d’un Président, d’un Trésorier et d’un Secrétaire.</p>
"""
    text7.save()

    text8 = pages.Text()
    text8.title = u"Relations école et étudiants"
    text8.body = u"""Text à faire => Lionel
Voilà.
"""
    text8.save()

    text9 = pages.Text()
    text9.title = u"Groupes professionnels"
    text9.body = u"""<p>Au fil des dernières années, l'AIN7 a suscité la création de groupes professionnels. Chaque Groupe Professionnel réunit les ingénieurs N7 qui travaillent dans le même domaine industriel.</p>
<p>Il est animé par un noyau de quelques ingénieurs N7 qui contribue à l'animation et prépare les manifestations du groupe.</p>
<p>Il a une couverture nationale.</p>
<p>Il a vocation à être un des interlocuteurs de l'ENSEEIHT pour l'évolution de ses filières d'enseignement et une source privilégiée d'informations et de proposition.</p>
<p>Il contribue dans son domaine à assurer la promotion de l'ENSEEIHT dans le cadre de l'AIN7 et en liaison avec la Direction de l'ENSEEIHT.</p>
<p>Il a vocation d'entraide pour la recherche d'emplois.</p>
<p>Il bénéficie de la logistique de l'AIN7 (mailing – Web – Groupes régionaux….)</p>
<p>L'action des Groupes professionnels se fait en liaison avec celles des Correspondants d'Entreprises qui, dans leurs domaines, sont des invités permanents dans chaque groupe.</p>
<p>La Communication des Groupes professionnels vers le monde extérieur se fait par le canal de l'AIN7.</p>
<p>3 groupes professionnels sont actifs :</p>
<h4>Groupe TIC (animateur : Eric Nizard - eric.nizard@lic.fr)</h4>
<p>Issu du groupe professionnel Telecom qui a été depuis 2000 le plus actif, ce groupe a désormais élargi ses activités à l'informatique et plus généralement aux métiers issus des technologies de l'information et de la communication.</p>
<p>Le groupe TIC organise régulièrement des conférences à Paris, dans le cadre du Groupe Parisien. Il est par ailleurs, le correspondant AIN7 au sein de <a href="http://www.g9plus.org">l'Institut G9+</a> qui rassemble les représentants "TIC" de 17 grandes Associations d'Ingénieurs (X, Centrales, Mines, Supélec…) et de Management (HEC, ESCP, ESSEC,…).</p>
<h4>Groupe Aerospace (animateur : Yann Guerin – yannguer@yahoo.fr)</h4>
<p>Ce groupe résidant à Toulouse, organise régulièrement des rencontres et bénéficie notamment de la présence de nombreux ingénieurs ENSEEIHT au sein du pôle de compétitivité "Aerospace Valley".</p>
<h4>Groupe Energie (renseignements : Maryse Lemmet - maryse.lemmet@orange.fr)</h4>
<p>Issu du groupe "Génie Electrique", ce groupe est en cours de reconstitution et doit démarrer des activités élargies au printemps 2009.</p>
"""
    text9.save()

    text10 = pages.Text()
    text10.title = u"Les publications de l'AIn7"
    text10.body = u"""<p>La Communication, Interne aux adhérents de l’AIN7, est réalisée par les 3 vecteurs suivants, en complément des moyens classiques (courrier, mail, téléphone, fax …)</p>

<p>En Projet:</p>
<ul>
<li>Newsletter</li>
<li>Communauté AIN7/Viadeo</li>
</ul>

<p>Newsletter : répond à un besoin de diffuser des informations rapides et sous format électronique. 10 parutions annuelles envisagées.</p>
<p>Communauté AIN7/Viadeo : dans le cadre d'un protocole d'accord en cours de négociation, le réseau Viadeo mettra à la disposition de l'AIN7 un espace communautaire privatif qui a vocation à devenir le forum privilégié de dialogue entre les N7.</p>

<p>Communication</p>
<p>Des supports de communication interactifs</p>
<p><b>L'ANNUAIRE : PUBLICATION DE BASE DE L'ASSOCIATION</b></p>
<p>C'est un moyen privilégié de communication entre tous les membres. Plus de 15000 adresses personnelles et professionnelles y sont répertoriées.</p>
<p>Réalisé avec le plus grand soin, c'est un outil précieux à la fois pour l'activité professionnelle et les relations conviviales.</p>
<p>Il est également apprécié des entreprises et des cabinets de recrutement et contribue à la notoriété de l'Association et des ingénieurs ENSEEIHT.</p>
<p>Il est librement accessible sur le site AIN7 aux adhérents de l'AI.</p>


<p><b>CANAL N7 : REVUE TRIMESTRIELLE A VOCATION SCIENTIFIQUE, TECHNIQUE INDUSTRIELLE ET SOCIETALE</b></p>
<p>Constituant un lien régulier entre les membres de l'Association, elle est aussi diffusée, par abonnement, à des lecteurs extérieurs.</p>
<p>Sa première partie est consacrée à des articles à vocation scientifique, technique et industrielle, mais aussi aux aspects socio-économiques, environnementaux, humains.</p>
<p>La seconde partie est consacrée à la vie de la Communauté ENSEEIHT et en particulier de l'Association, avec des informations sur les activités du Conseil d'Administration, des différentes Commissions et Délégations, des Groupes régionaux et internationaux, ainsi que sur la vie de l'Ecole.</p>
<p>Au printemps 2009, un nouveau format de Canal N7, plus moderne, facilitant la lecture, va apparaître. Nous attendions vos avis avec impatience.</p>

<ul>
<li><a href="{% url ain7.media_communication.views.canal_n7 %}">Canal N7</a>, la revue trimestrielle de l'association</li>
<li><a href="{% url ain7.media_communication.views.website %}">Site internet</a>, lieu de recontre électronique de toutes les générations</li>
<li><a href="/annuaire/">L'Annuaire</a>, l'annuaire de tous les anciens édité tous les ans au mois de juillet</li>
</ul>
"""
    text10.save()

    text11 = pages.Text()
    text11.title = u"Présentation de canal N7"
    text11.body = u"""<p>Journal trimestriel de l'ASSOCIATION des INGENIEURS de l'ENSEEIHT.</p>

<ul>
<li><b>Régie Publicitaire :</b> MAZARINE Partenaires, Paris</li>
<li><b>Contact :</b> Carole Néhmé c.nehme@mazarine.com</li>
<li><b>Tél :</b> 01 58 05 49 17</li>
<li><b>Commission paritaire</b> (en cours de renouvellement)</li>
<li><b>Prix au numéro :</b> 9 €</li>
<li><b>Abonnement extérieur :</b> 30,50 € (1an)</li>
<li><b>Abonnement adhérents :</b> 12,20 €</li>
</ul>
"""
    text11.save()

    text12 = pages.Text()
    text12.title = u"L'équipe de la rédaction"
    text12.body = u"""<ul>
<li>Directeur de publication: <a href="/annuaire/1/">Michel Canon</a> (SET 1969)</li>
<li>Rédacteur en chef : <a href="/annuaire/1/">Claude Thirriot</a> (1955)</li>
<li>Secrétaire de rédaction : Sylvie Henric</li>
</ul>
"""
    text12.save()

    text13 = pages.Text()
    text13.title = u"Le magazine"
    text13.body = u"""<p>Depuis Novembre 1986, le bulletin d’information de l’AIN7 est réellement devenu le journal de l’Association avec des articles à portée scientifique , socio- économique ou culturelle.</p>

<p>On y retrouve trois parties :</p>
<ul>
<li><b>Le Dossier :</b> partie rédactionnelle comprenant les articles techniques,</li>
<li><b>Le Forum des lecteurs</b>,</li>
<li><b>La Vie de l'Association</b>, incluant des informations sur les activités des groupes régionaux, de l'école et des élèves.</li>
</ul>

<p>De manière générale, chaque numéro est organisé autour d’un thème (…La Qualité, Sécurité et simulation, Communication, Biomécanique, Microsystèmes, Véhicules électriques, 3ième millénaire, Ingéniérie du sport, Télecoms,…..).</p>

<p>La liste complète des numéros est disponible auprés du secrétariat de l’AIN7.</p>

<p>Vous pourrez consulter le sommaire des derniers numéros en cliquant sur la photo du numéro correspondant.</p>
"""
    text13.save()

    text14 = pages.Text()
    text14.title = u"Au sommaire du dernier numéro"
    text14.body = u"""<ul>
      <li><a href="/media_communication/canal_n7/edito/">Editorial</a></li>
      <li>Le mot du président</li>
      <li>Vestiges historiques</li>
      <li>Naissance de FEST'INP, le nouveau gala des étudiants des trois écoles toulousaines de l'INPT</li>
      <li>Le Fest'INP, une inauguration réussie !</li>
      <li>Bureau du Développement Durable</li>
      <li>La certification des compétences, un futur inéluctable</li>
      <li>Forum des lecteurs</li>
      <li>Quelques nouvelles de l'ENSEEIHT</li>
      <li>Souvenir de Jean-Louis Amalric</li>
      <li>Skype</li>
      <li>Assemblée générale 2008</li>
      <li>Commission voyage</li>
   </ul>
"""
    text14.save()

    text15 = pages.Text()
    text15.title = u"Éditorial"
    text15.body = u"""<p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Curabitur sit amet turpis non augue commodo tincidunt. Nulla commodo convallis neque. Donec elementum, justo ut dapibus dictum, nibh felis fringilla magna, ut rhoncus neque purus sed tortor. Donec sollicitudin. Cras lacus dolor, rhoncus vel, semper gravida, molestie quis, pede. Cras risus risus, mollis ac, sollicitudin sed, tempor ac, arcu. Aenean augue ipsum, convallis sit amet, luctus sit amet, scelerisque in, sem. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Mauris quis metus ut leo congue varius. Duis euismod nisi varius justo rhoncus vestibulum.</p>

<p>Nunc nulla. Vestibulum ante. Praesent fringilla vestibulum lorem. Duis vel dolor. Phasellus lobortis tincidunt dolor. Mauris et sapien sollicitudin odio tincidunt gravida. Etiam enim. Mauris ut metus id lacus dapibus consectetuer. Maecenas eu pede ut leo faucibus dictum. Praesent nec nisi at leo egestas euismod. Nunc varius erat vitae lacus. Nam leo risus, vehicula nec, molestie vel, rhoncus nec, libero. Cras velit.</p>

<p>Curabitur sit amet arcu in leo scelerisque pellentesque. Sed lobortis, nunc sed gravida vehicula, nulla sem porta sapien, vel eleifend sapien leo ac justo. Donec pharetra, ante et mattis auctor, sapien ipsum luctus tellus, eu euismod leo tellus non tellus. Praesent urna. Aliquam bibendum odio. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Vestibulum neque. Quisque tincidunt. Pellentesque in purus. Aliquam volutpat. Mauris id velit in purus congue convallis. Phasellus nec nisl. Quisque nisl. Praesent viverra. Pellentesque tristique. Sed sed justo a mi pulvinar cursus.</p>

<p>Quisque vel tortor ac neque feugiat feugiat. Proin laoreet eleifend augue. Etiam ut nisi vitae sapien molestie vehicula. Aenean mattis purus eget velit. Nulla sapien tellus, venenatis quis, consequat vel, tincidunt eget, neque. Fusce egestas. Curabitur ipsum leo, dignissim ac, sodales nec, tincidunt vel, ipsum. Duis laoreet nunc eget quam. Proin ac dui convallis leo accumsan ultrices. Pellentesque a sapien sit amet lorem bibendum consectetuer. Fusce sodales, purus eget fringilla iaculis, felis orci mattis orci, vitae tristique mi risus at lectus. Cras nec lorem eu dolor consequat pellentesque. Morbi pulvinar pede quis mauris. Fusce sit amet augue.</p>

<p>Cras faucibus vehicula nisl. Quisque in velit. Sed augue. Vestibulum eu orci et mi porttitor commodo. Mauris malesuada, elit ac sagittis pharetra, odio sapien commodo lectus, sit amet mollis odio mauris eget tortor. Donec facilisis bibendum diam. Morbi accumsan. Nullam massa orci, luctus nec, tristique posuere, eleifend sed, urna. Nunc felis lectus, suscipit id, auctor at, hendrerit vitae, massa. Suspendisse malesuada erat ac augue. Sed nibh.</p>
"""
    text15.save()

    text16 = pages.Text()
    text16.title = u"Site Internet AIn7"
    text16.body = u"""<p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Curabitur sit amet turpis non augue commodo tincidunt. Nulla commodo convallis neque. Donec elementum, justo ut dapibus dictum, nibh felis fringilla magna, ut rhoncus neque purus sed tortor. Donec sollicitudin. Cras lacus dolor, rhoncus vel, semper gravida, molestie quis, pede. Cras risus risus, mollis ac, sollicitudin sed, tempor ac, arcu. Aenean augue ipsum, convallis sit amet, luctus sit amet, scelerisque in, sem. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Mauris quis metus ut leo congue varius. Duis euismod nisi varius justo rhoncus vestibulum.</p>

<p>Nunc nulla. Vestibulum ante. Praesent fringilla vestibulum lorem. Duis vel dolor. Phasellus lobortis tincidunt dolor. Mauris et sapien sollicitudin odio tincidunt gravida. Etiam enim. Mauris ut metus id lacus dapibus consectetuer. Maecenas eu pede ut leo faucibus dictum. Praesent nec nisi at leo egestas euismod. Nunc varius erat vitae lacus. Nam leo risus, vehicula nec, molestie vel, rhoncus nec, libero. Cras velit.</p>

<p>Curabitur sit amet arcu in leo scelerisque pellentesque. Sed lobortis, nunc sed gravida vehicula, nulla sem porta sapien, vel eleifend sapien leo ac justo. Donec pharetra, ante et mattis auctor, sapien ipsum luctus tellus, eu euismod leo tellus non tellus. Praesent urna. Aliquam bibendum odio. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Vestibulum neque. Quisque tincidunt. Pellentesque in purus. Aliquam volutpat. Mauris id velit in purus congue convallis. Phasellus nec nisl. Quisque nisl. Praesent viverra. Pellentesque tristique. Sed sed justo a mi pulvinar cursus.</p>

<p>Quisque vel tortor ac neque feugiat feugiat. Proin laoreet eleifend augue. Etiam ut nisi vitae sapien molestie vehicula. Aenean mattis purus eget velit. Nulla sapien tellus, venenatis quis, consequat vel, tincidunt eget, neque. Fusce egestas. Curabitur ipsum leo, dignissim ac, sodales nec, tincidunt vel, ipsum. Duis laoreet nunc eget quam. Proin ac dui convallis leo accumsan ultrices. Pellentesque a sapien sit amet lorem bibendum consectetuer. Fusce sodales, purus eget fringilla iaculis, felis orci mattis orci, vitae tristique mi risus at lectus. Cras nec lorem eu dolor consequat pellentesque. Morbi pulvinar pede quis mauris. Fusce sit amet augue.</p>

<p>Cras faucibus vehicula nisl. Quisque in velit. Sed augue. Vestibulum eu orci et mi porttitor commodo. Mauris malesuada, elit ac sagittis pharetra, odio sapien commodo lectus, sit amet mollis odio mauris eget tortor. Donec facilisis bibendum diam. Morbi accumsan. Nullam massa orci, luctus nec, tristique posuere, eleifend sed, urna. Nunc felis lectus, suscipit id, auctor at, hendrerit vitae, massa. Suspendisse malesuada erat ac augue. Sed nibh.</p>
"""
    text16.save()

    text17 = pages.Text()
    text17.title = u"L'international à l'AIn7"
    text17.body = u"""Texte à définir.
"""
    text17.save()
