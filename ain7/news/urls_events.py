# -*- coding: utf-8
"""
 ain7/news/urls_events.py
"""
#
#   Copyright © 2007-2016 AIn7 Devel Team
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

from django.conf.urls import url

from ain7.news import views


urlpatterns = [
    # Evenements
    url(r'^$', views.event_index, name='events-index'),
    url(r'^ical/$', views.ical),
    url(r'^new/$', views.event_edit),
    url(r'^search/$', views.event_search),
    url(r'^(?P<event_id>\d+)/$', views.event_details, name='event-details'),
    url(r'^(?P<event_id>\d+)/edit/$', views.event_edit),
    url(r'^(?P<event_id>\d+)/contact/$', views.event_contact),
    url(r'^(?P<event_id>\d+)/organizer/add/$', views.event_organizer_add),
    url(r'^(?P<event_id>\d+)/organizer/(?P<organizer_id>\d+)/delete/$', views.event_organizer_delete),
    url(r'^(?P<event_id>\d+)/organizer/(?P<organizer_id>\d+)/swap_email_notif/$', views.event_swap_email_notif),
    url(r'^(?P<event_id>\d+)/yes/$', views.event_attend_yes),
    url(r'^(?P<event_id>\d+)/no/$', views.event_attend_no),
    url(r'^(?P<event_id>\d+)/maybe/$', views.event_attend_maybe),
    url(r'^(?P<event_id>\d+)/attendees/$', views.event_attendees),
    url(r'^(?P<event_id>\d+)/rsvp/(?P<rsvp_id>\d+)/$', views.event_rsvp),
    url(r'^(?P<event_id>\d+)/rsvp/add/$', views.event_rsvp, { 'rsvp_id':None }),
]
