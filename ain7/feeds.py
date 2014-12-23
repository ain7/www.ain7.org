# -*- coding: utf-8
"""
 ain7/feeds.py
"""
#
#   Copyright © 2007-2015 AIn7 Devel Team
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

from django.contrib.syndication.views import Feed
from django.utils.translation import ugettext as _

from ain7.news.models import NewsItem

class LatestsEvents(Feed):
    """
    Return latest events from AIn7
    """
    title = "AIn7 Events RSS"
    link = "/evenements/"
    description = _("AIn7 organized events")

    def items(self):
        """
        Item of Events RSS stream
        """
        return NewsItem.objects.filter(date__isnull=False).order_by('-date')[:20]

class LatestsNews(Feed):
    """
    Return latest news from AIn7
    """
    title = "AIn7 News RSS"
    link = "/actualites/"
    description = _("AIn7 news")

    def items(self):
        """
        Item of News RSS stream
        """
        return NewsItem.objects.order_by('-creation_date')[:20]

