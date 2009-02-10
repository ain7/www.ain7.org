# -*- coding: utf-8 
#
# admin.py
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

from django.contrib import admin

import ain7.manage.models as manage
import ain7.adhesions.models as adhesions
import ain7.annuaire.models as annuaire
import ain7.emploi.models as emploi
import ain7.evenements.models as evenements
import ain7.voyages.models as voyages
import ain7.news.models as news
import ain7.groupes_professionnels.models as groupes_professionnels
import ain7.groupes_regionaux.models as groupes_regionaux

admin.site.register(manage.Notification)

admin.site.register(adhesions.Subscription)

admin.site.register(annuaire.Country)
admin.site.register(annuaire.PersonType)
admin.site.register(annuaire.MemberType)
admin.site.register(annuaire.Activity)
admin.site.register(annuaire.MaritalStatus)
admin.site.register(annuaire.Decoration)
admin.site.register(annuaire.CeremonialDuty)
admin.site.register(annuaire.School)
admin.site.register(annuaire.Track)
admin.site.register(annuaire.PromoYear)
admin.site.register(annuaire.Promo)
admin.site.register(annuaire.Person)
admin.site.register(annuaire.AIn7Member)
admin.site.register(annuaire.AddressType)
admin.site.register(annuaire.Club)

admin.site.register(emploi.ActivityField)
admin.site.register(emploi.Organization)
admin.site.register(emploi.OrganizationProposal)
admin.site.register(emploi.Office)
admin.site.register(emploi.OfficeProposal)
admin.site.register(emploi.PublicationItem)
admin.site.register(emploi.JobOffer)

admin.site.register(evenements.Event)
admin.site.register(evenements.EventSubscription)

admin.site.register(voyages.TravelType)
admin.site.register(voyages.Travel)

admin.site.register(news.NewsItem)

admin.site.register(groupes_professionnels.GroupPro)

admin.site.register(groupes_regionaux.Group)

