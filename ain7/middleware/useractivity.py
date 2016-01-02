# -*- coding: utf-8
"""
 ain7/middleware/useractivity.py
"""
#
#   Copyright © 2009-2016 AIn7 Devel Team
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

#
# idea taken from:
# http://www.arnebrodowski.de/blog/482-Tracking-user-activity-with-Django.html
#

import datetime

from django.utils import timezone

from ain7.annuaire.models import Person, UserActivity


class UserActivityMiddleware(object):
    """
    User activity middleware. We track when a user was last active in the
    site and store this information in the database.
    """

    def process_request(self, request):
        """process request"""
        if request.user.is_authenticated():
            try:
                person = Person.objects.get(user=request.user)
            except Person.DoesNotExist:
                # can't find the Person... we can do nothing, finish
                return

            now = timezone.now()
            time_delta = datetime.timedelta(hours=4)

            user_activities = UserActivity.objects.filter(person=person)\
                .reverse()

            if (
                len(user_activities) < 1 or
                now - user_activities[0].date > time_delta
            ):
                user_activity = UserActivity()
                user_activity.person = person
                user_activity.date = now
                if 'REMOTE_HOST' in request.META.keys():
                    user_activity.client_address = request.META['REMOTE_HOST']
                if 'HTTP_USER_AGENT' in request.META.keys():
                    user_activity.browser_info = (
                        request.META['HTTP_USER_AGENT']
                    )
                user_activity.save()
