# -*- coding: utf-8
#
# feeds.py
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

from django.contrib.syndication.feeds import Feed
from ain7.evenements.models import Event

class LatestEvents(Feed):
    title = "AIn7 RSS"
    link = "/evenements/"
    description = "Evenements organises par l'AIn7 ou autour de l'AIn7"

    def items(self):
        return Event.objects.order_by('-publication_start')[:5]

class LatestEntriesByCategory(Feed):
    title = "AIn7 RSS"
    link = "/evenements/"
    description = "Evenements organises par l'AIn7 ou autour de l'AIn7"

    def items(self):
        return Event.objects.order_by('-publication_start')[:5]

