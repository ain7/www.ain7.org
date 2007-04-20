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
from django.contrib.auth.models import User

class Personne(models.Model):

    CHOIX_NATIONALITES = (
        (1,'Afghane'),
        (2,'Albanaise'),
        (3,'Algérienne'),
        (4,'Allemande'),
        (5,'Américaine'),
        (6,'Andorrane'),
        (7,'Angolaise'),
        (8,'Antiguaise et Barbudienne'),
        (9,'Argentine'),
        (10,'Arménienne'),
        (11,'Australienne'),
        (12,'Autrichienne'),
        (13,'Azerbaïdjanaise'),
        (14,'Bahamienne'),
        (15,'Bahreïnienne'),
        (16,'Bangladaise'),
        (17,'Barbadienne'),
        (18,'Belge'),
        (19,'Belizienne'),
        (20,'Beninoise'),
        (21,'Bhoutanaise'),
        (22,'Biélorusse'),
        (23,'Birmanne'),
        (24,'Bolivienne'),
        (25,'Bosniaque'),
        (26,'Botswanaise'),
        (27,'Brésilienne'),
        (28,'Britannique'),
        (29,'Bulgare'),
        (30,'Burkinaise'),
        (31,'Burundaise'),
        (32,'Cambodgienne'),
        (33,'Camerounaise'),
        (34,'Canadienne'),
        (35,'Cap-Verdienne'),
        (36,'Centrafricaine'),
        (37,'Chilienne'),
        (38,'Chinoise'),
        (39,'Chypriote'),
        (40,'Colombienne'),
        (41,'Comorienne'),
        (42,'Congolaise'),
        (43,'Nord-Coréenne'),
        (44,'Sud-Coréenne'),
        (45,'Costaricaine'),
        (46,'Ivorienne'),
        (47,'Croate'),
        (48,'Cubaine'),
        (49,'Danoise'),
        (50,'Djiboutienne'),
        (51,'Dominicaine'),
        (52,'Dominiquaise'),
        (53,'Egyptienne'),
        (54,'Emirienne'),
        (55,'Equatorienne'),
        (56,'Erythréenne'),
        (57,'Espagnole'),
        (58,'Estonienne'),
        (59,'Éthiopiene'),
        (60,'Fidjienne'),
        (61,'Finlandaise'),
        (62,'Française'),
        (63,'Gabonnaise'),
        (64,'Gambienne'),
        (65,'Georgienne'),
        (66,'Ghanéenne'),
        (67,'Grecque'),
        (68,'Grenadienne'),
        (69,'Guatémaltèque'),
        (70,'Guinéenne'),
        (71,'Bissau-Guinéenne'),
        (72,'Equato-Guinéenne'),
        (73,'Guyanienne'),
        (74,'Haïtienne'),
        (75,'Hondurienne'),
        (76,'Hongroise'),
        (77,'Indienne'),
        (78,'Indonésienne'),
        (79,'Iranienne'),
        (80,'Irakienne'),
        (81,'Irlandaise'),
        (82,'Islandaise'),
        (83,'Israélienne'),
        (84,'Italienne'),
        (85,'Jamaïcaine'),
        (86,'Japonaise'),
        (87,'Jordanienne'),
        (88,'Kazakhe'),
        (89,'Kenyane'),
        (90,'Kirghize'),
        (91,'Kiribatienne'),
        (92,'Kittitienne'),
        (93,'et'),
        (94,'Névicienne'),
        (95,'Koweïtienne'),
        (96,'Laotienne'),
        (97,'Lesothane'),
        (98,'Lettonne'),
        (99,'Libanaise'),
        (100,'Libérienne'),
        (101,'Libyenne'),
        (102,'Liechtensteinoise'),
        (103,'Lituanienne'),
        (104,'Luxembourgeoise'),
        (105,'Macédonienne'),
        (106,'Malaisienne'),
        (107,'Malawite'),
        (108,'Maldivienne'),
        (109,'Malgache'),
        (110,'Malienne'),
        (111,'Maltaise'),
        (112,'Marocainne'),
        (113,'Marshallaise'),
        (114,'Mauricienne'),
        (115,'Mauritanienne'),
        (116,'Mexicainne'),
        (117,'Micronésienne'),
        (118,'Moldave'),
        (119,'Monégasque'),
        (120,'Mongole'),
        (121,'Mozambicaine'),
        (122,'Namibienne'),
        (123,'Nauruane'),
        (124,'Néerlandaise'),
        (125,'Neo-Zélandaise'),
        (126,'Népalaise'),
        (127,'Nicaraguayenne'),
        (128,'Nigérienne'),
        (129,'Nigériane'),
        (130,'Norvégienne'),
        (131,'Omanaise'),
        (132,'Ougandaise'),
        (133,'Ouzbeke'),
        (134,'Pakistanaise'),
        (135,'Panaméenne'),
        (136,'Papouane-Neo-Guinéenne'),
        (137,'Paraguayenne'),
        (138,'Péruvienne'),
        (139,'Philippinne'),
        (140,'Polonaise'),
        (141,'Portugaise'),
        (142,'Qatarienne'),
        (143,'Tchèque'),
        (144,'Roumaine'),
        (145,'Russe'),
        (146,'Rwandaise'),
        (147,'Saint-Lucienne'),
        (148,'Saint-Marinaise'),
        (149,'Saint-Vincentaise'),
        (150,'et'),
        (151,'Grenadine'),
        (152,'Salomonaise'),
        (153,'Salvadorienne'),
        (154,'Samoane'),
        (155,'Santoméenne'),
        (156,'Saoudienne'),
        (157,'Sénégalaise'),
        (158,'Serbe'),
        (159,'Seychelloise'),
        (160,'Sierra-Léonaise'),
        (161,'Singapourienne'),
        (162,'Slovaque'),
        (163,'Slovène'),
        (164,'Somalienne'),
        (165,'Soudanaise'),
        (166,'Sri'),
        (167,'Lankaise'),
        (168,'Sud-Africaine'),
        (169,'Suèdoise'),
        (170,'Suisse'),
        (171,'Surinamienne'),
        (172,'Swazie'),
        (173,'Syrienne'),
        (174,'Tadjike'),
        (175,'Taïwanaise'),
        (176,'Tanzanienne'),
        (177,'Tchadienne'),
        (178,'Thaïlandaise'),
        (179,'Togolaise'),
        (180,'Tonguienne'),
        (181,'Trinidadienne'),
        (182,'Tunisienne'),
        (183,'Turkmène'),
        (184,'Turque'),
        (185,'Tuvaluane'),
        (186,'Ukranienne'),
        (187,'Uruguayenne'),
        (188,'Vanatuane'),
        (189,'Vaticane'),
        (190,'Vénézuélienne'),
        (191,'Viêtnamienne'),
        (192,'Yémenite'),
        (193,'Zambienne'),
        (194,'Zimbabwéenne'),
    )

    FILIERES = (
        (1,'Informatique et Mathématiques Appliquées'),
        (2,'Hydraulique et Mécanique des Fluides'),
        (3,'Électronique'),
        (4,'Génie Électrique et Automatique'),
        (5,'Télécommunications et Réseaux'),
        )

    CHOIX_PROMO = (
       (2003,'2003'),
       (2004,'2004'),
       (2005,'2005'),
       (2006,'2006'),
       (2007,'2007'),
       (2008,'2008'),
      )

    user = models.OneToOneField(User)
    nom = models.CharField(maxlength=50)
    prenom = models.CharField(maxlength=50)
    nom_jeune_fille = models.CharField(maxlength=100,blank=True,null=True)
    filiere = models.IntegerField(choices=FILIERES)
    promo = models.IntegerField(choices=CHOIX_PROMO)
    date_naissance = models.DateField(blank=True,null=True)
    date_deces = models.DateField(blank=True,null=True)
    nationalite = models.IntegerField(choices=CHOIX_NATIONALITES)
    nombre_enfants = models.IntegerField(blank=True,null=True)
    avatar = models.ImageField(upload_to='data',blank=True,null=True)
    surnom = models.CharField(maxlength=50,blank=True,null=True)
    blog = models.URLField(maxlength=80,verify_exists=True,blank=True,core=True)
    blog_agrege_sur_le_planet = models.BooleanField(core=True,default=False)

    date_creation =  models.DateTimeField(editable=False)
    date_modification = models.DateTimeField(editable=False)
    modifie_par = models.IntegerField(editable=False)

    def __str__(self):
        return self.prenom+" "+self.nom

    def save(self):
        if not self.date_creation:
             self.date_creation = datetime.date.today()
        self.date_modification = datetime.datetime.today()
	self.modifie_par = 1
        return super(Personne, self).save()

    class Admin:
         list_display = ('nom', 'prenom','promo','filiere')
	 list_filter = ['promo']
	 search_fields = ['nom','prenom','promo']

class Adresse(models.Model):
    TYPE_ADRESSE = (
        (1,'Personnelle'),
        (2,'Professionnelle'),
        (3,'Parentale'),
        )
    personne = models.ForeignKey(Personne, edit_inline=models.STACKED, num_in_admin=2)
    rue = models.CharField(maxlength=100,core=True)
    rue_2e_ligne = models.CharField(maxlength=100,null=True,blank=True)
    code_postal = models.CharField(maxlength=20)
    ville = models.CharField(maxlength=50)
    pays = models.CharField(maxlength=50)
    type = models.IntegerField(choices=TYPE_ADRESSE)

class Position(models.Model):

    CHOIX_ACTIVITE_ORGA = (
        (1,'Aviation'),
        (2,'Medical'),
	(3,'Automobile'),
	(4,'Banque'),
	(5,'Biotechnologies'),
	(6,'Informatique'),
	)

    CHOIX_TYPE_ORGA = (
       (1,'Organisme publique'),
       (2,'Organisme privé'),
       (3,'Organisme à but non lucratif'),
       (4,'Agence gouvernementale'),
       (5,'Indépendant'),
       (6,'Éducation'),
       )

    CHOIX_TAILLE_ORGA = (
       (1,'Unipersonnelle'),
       (2,'1-10 employés'),
       (3,'11-50 employés'),
       (4,'51-200 employés'),
       (5,'201-500 employés'),
       (6,'501-1000 employés'),
       (7,'1001-5000 employés'),
       (8,'5001-10000 employés'),
       (9,'plus de 10000 employés'),
       )

    TYPE = (
       (0,'Professionelle'),
       (1,'Associative'),
    )

    personne = models.ForeignKey(Personne, edit_inline=models.STACKED, num_in_admin=1)
    titre = models.CharField(maxlength=100,core=True)
    societe = models.CharField(maxlength=100,core=True)
    debut = models.DateField(blank=True, null=True)
    fin = models.DateField(blank=True, null=True)
    position_actuelle = models.BooleanField()
    organisation_activite = models.IntegerField(choices=CHOIX_ACTIVITE_ORGA, blank=True, null=True)
    organisation_type = models.IntegerField(choices=CHOIX_TYPE_ORGA, blank=True, null=True)
    organisation_taille = models.IntegerField(choices=CHOIX_TAILLE_ORGA, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    type = models.IntegerField()

class Couriel(models.Model):
    TYPE_MAIL = (
        (1,'Personnelle'),
        (2,'Professionnelle'),
        )

    personne = models.ForeignKey(Personne, edit_inline=models.STACKED, num_in_admin=1)
    adresse = models.EmailField(core=True)
    type = models.IntegerField(choices=TYPE_MAIL,core=True)

class Messagerie(models.Model):

    TYPE_IM = (
	(1,'ICQ'),
	(2,'MSN'),
	(3,'AIM'),
	(4,'Yahoo'),
	(5,'Jabber'),
	(6,'Gadu-Gadu'),
	(7,'Skype'),
	)

    personne = models.ForeignKey(Personne, edit_inline=models.STACKED, num_in_admin=1)
    type_im = models.IntegerField(choices=TYPE_IM,core=True)
    valeur = models.CharField(maxlength=40,core=True)

class IRC(models.Model):
    personne = models.ForeignKey(Personne, edit_inline=models.STACKED, num_in_admin=1)
    reseau = models.CharField(maxlength=50,core=True)
    nick = models.CharField(maxlength=20,core=True)
    canaux = models.CharField(maxlength=100)

class SiteWeb(models.Model):
    personne = models.ForeignKey(Personne, edit_inline=models.STACKED, num_in_admin=1)
    url = models.CharField(maxlength=100,core=True)

class Club(models.Model):

    ETABLISSEMENT = (
         (0,'ENSEEIHT'),
         (1,'INP'),
    )

    nom = models.CharField(maxlength=20)
    description = models.CharField(maxlength=100)
    url = models.URLField(maxlength=50, blank=True, null=True)
    mail = models.EmailField(maxlength=50, blank=True, null=True)
    date_creation = models.DateField(blank=True, null=True)
    date_fin = models.DateField(blank=True, null=True)
    etablissement = models.IntegerField(choices=ETABLISSEMENT)

    def __str__(self):
        return self.nom

    class Admin:
        pass

class MembreClub(models.Model):
    club = models.ForeignKey(Club, edit_inline=models.STACKED, num_in_admin=1, core=True)
    personne = models.ForeignKey(Personne, edit_inline=models.STACKED, num_in_admin=1, core=True)
    position = models.CharField(maxlength=50, blank=True, null=True)

