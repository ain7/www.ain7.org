# -*- coding: utf-8
#
# sitemaps.py
#
#   Copyright © 2007-2011 AIn7 Devel Team
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

from django.contrib.sitemaps import Sitemap

from ain7.pages.models import TextBlock
from ain7.news.models import NewsItem
from ain7.groups.models import Group
from ain7.voyages.models import Travel

class EventsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return NewsItem.objects.filter(date__gte=datetime.datetime.now() , status=1)

    def lastmod(self, obj):
        return obj.date

class TextsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return TextBlock.objects.all()

    def lastmod(self, obj):
        return obj.last_change_at

class NewsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return NewsItem.objects.all()

    def lastmod(self, obj):
        return obj.last_change_at

class GroupesProSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Group.objects.all()

    def lastmod(self, obj):
        return obj.last_change_at

class GroupesRegionauxSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Group.objects.all()

    def lastmod(self, obj):
        return obj.last_change_at

class TravelsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Travel.objects.all()

    def lastmod(self, obj):
        return obj.last_change_at

