# -*- coding: utf-8
"""
 ain7/news/urls_events.py
"""
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

from django.conf.urls.defaults import patterns


urlpatterns = patterns('ain7.news.views',
    # Evenements
    (r'^$', 'event_index'),
    (r'^ical/$', 'ical'),
    (r'^new/$', 'event_edit'),
    (r'^search/$', 'event_search'),
    (r'^(?P<event_id>\d+)/$', 'event_details'),
    (r'^(?P<event_id>\d+)/edit/$', 'event_edit'),
    (r'^(?P<event_id>\d+)/image/delete/$', 'event_image_delete'),
    (r'^(?P<event_id>\d+)/contact/$', 'event_contact'),
    (r'^(?P<event_id>\d+)/organizer/add/$', 'event_organizer_add'),
    (r'^(?P<event_id>\d+)/organizer/(?P<organizer_id>\d+)/delete/$',
        'event_organizer_delete'),
    (r'^(?P<event_id>\d+)/organizer/(?P<organizer_id>\d+)/swap_email_notif/$',
        'event_swap_email_notif'),
    (r'^(?P<event_id>\d+)/yes/$', 'event_attend_yes'),
    (r'^(?P<event_id>\d+)/no/$', 'event_attend_no'),
    (r'^(?P<event_id>\d+)/maybe/$', 'event_attend_maybe'),
    (r'^(?P<event_id>\d+)/attendees/$', 'event_attendees'),
    (r'^(?P<event_id>\d+)/rsvp/(?P<rsvp_id>\d+)/$', 'event_rsvp'),
    (r'^(?P<event_id>\d+)/rsvp/add/$', 'event_rsvp'),

)
