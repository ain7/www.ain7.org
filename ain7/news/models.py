# -*- coding: utf-8
"""
 ain7/news/models.py
"""
#
#   Copyright © 2007-2017 AIn7 Devel Team
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

from django.core.urlresolvers import reverse
from django.db import models
from django.template import defaultfilters
from django.utils.translation import ugettext as _

from ain7.annuaire.models import Person
from ain7.utils import LoggedClass


class EventOrganizer(models.Model):
    """event organizer"""

    event = models.ForeignKey('news.NewsItem', verbose_name=_('event'),
        related_name='event_organizers')
    organizer = models.ForeignKey(Person, verbose_name=_('organizer'),
        related_name='organized_events')
    send_email_for_new_subscriptions = models.BooleanField(default=False,
            verbose_name=_('send email for new subscription'))

class RSVPAnswer(models.Model):

    person = models.ForeignKey('annuaire.Person')
    event = models.ForeignKey('news.NewsItem')
    yes = models.BooleanField(default=False)
    no = models.BooleanField(default=False)
    maybe = models.BooleanField(default=False)
    number = models.IntegerField(verbose_name=_('number of persons'), default=1)
    payment = models.ForeignKey('shop.Payment', null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('annuaire.Person', related_name='rsvpanswers_created')
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey('annuaire.Person', related_name='rsvpanswers_updated')

    def answer(self):
       if self.yes:
           return _('yes')
       if self.no:
           return _('no')
       if self.maybe:
           return _('maybe')


class NewsItemManager(models.Manager):
    """news item manager"""

    def next_events(self):
        """Returns all future events."""
        return self.filter(date__gte=datetime.datetime.now())


class NewsItem(LoggedClass):
    """news item"""

    STATUS = (
              (0,_('project')),
              (1,_('confirmed')),
              (2,_('cancel')),
              )

    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(verbose_name=_('title'), max_length=100, unique=True)
    body = models.TextField(verbose_name=_('body'))
    shorttext = models.CharField(verbose_name=_('short text'), max_length=500,
        blank=True, null=True)
    image = models.ImageField(verbose_name=_('image'), upload_to='data',
        blank=True, null=True)
    creation_date = models.DateTimeField(verbose_name=_('date'),
        default=datetime.datetime.today, editable=False)
    front_page_presence = models.BooleanField(_('Front Page Presence'), default=True)

    # to which group we should link this news
    groups = models.ManyToManyField('groups.Group',
         verbose_name=_('groups'), related_name='events',
         blank=True)

    # those fields are only present for an event
    date = models.DateTimeField(verbose_name=_('date'), blank=True, null=True)
    location = models.CharField(verbose_name=_('location'), max_length=60,
        blank=True, null=True)
    status = models.IntegerField(verbose_name=_('status'), choices=STATUS,
        blank=True, null=True)
    contact_email = models.EmailField(verbose_name=_('contact email'),
        max_length=50, blank=True, null=True)

    link = models.CharField(verbose_name=_('external link'), max_length=60,
        blank=True, null=True)

#   organizers = models.ManyToManyField(Person, verbose_name=_('organizers'),
#         related_name='events', blank=True, null=True, through='EventOrganizer')
    pictures_gallery = models.CharField(verbose_name=_('Pictures gallery'),
         max_length=100, blank=True, null=True)

    package = models.ForeignKey('shop.Package', blank=True, null=True)

    rsvp_question = models.CharField(verbose_name=_('extra question'), 
        max_length=100, blank=True, null=True)
    rsvp_begin = models.DateField(verbose_name=_('rsvp begin'), 
        blank=True, null=True)
    rsvp_end = models.DateField(verbose_name=_('rsvp end'), 
        blank=True, null=True)
    rsvp_multiple = models.BooleanField(default=True)

    objects = NewsItemManager()


    def __unicode__(self):
        """news item unicode method"""
        return self.title

    def get_absolute_url(self):
        """news item url"""
        if self.date:
            return reverse('event-details', args=[self.id])
        else:
            return reverse('news-details', args=[self.slug])

    def save(self):
        """news item save method"""
        if self.pictures_gallery:
            if not self.pictures_gallery.startswith('http://'):
                self.pictures_gallery = 'http://'+self.pictures_gallery
        self.slug = defaultfilters.slugify(self.title)
        super(NewsItem, self).save()

    def rsvp_answer(self, person, yes=False, no=False, maybe=False):
        """define a rsvp answer to an event"""

        rsvp = None

        if RSVPAnswer.objects.filter(person=person, event=self).count() == 1:
            rsvp = RSVPAnswer.objects.get(person=person, event=self)
            rsvp.no = no
            rsvp.yes = yes
            rsvp.maybe = maybe
            rsvp.updated_by = person
        else:
            rsvp = RSVPAnswer(person=person, event=self,
                 created_by=person, updated_by=person,
                 no=no, yes=yes, maybe=maybe, number=0)

        if yes:
            rsvp.number = 1
        rsvp.save()
        return rsvp

    def attendees(self):
        """return event attendees"""
        return self.RSVAnswers.filter(yes=True)

    def attendeees_number(self):
        """Renvoie le nombre de participants à l'événement."""
        nbpart = 0
        for sub in self.RSVPAnswers.filter(yes=True):
            nbpart += sub.number
        return nbpart

    class Meta:
        """news item meta information"""
        ordering = ['-creation_date']
        verbose_name = _('news item')

