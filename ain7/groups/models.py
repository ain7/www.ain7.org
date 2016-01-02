# -*- coding: utf-8
"""
 ain7/groups/models.py
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

import datetime

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _
from django.utils import timezone

from ain7.annuaire.models import Person
from ain7.utils import LoggedClass

class GroupAccess(LoggedClass):
    """Stock group access level"""

    name = models.CharField(max_length=20)
    description = models.CharField(max_length=200, blank=True, null=True)

    def __unicode__(self):
        return self.name

class GroupType(LoggedClass):
    """Define the type of the group"""

    name = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    access = models.ForeignKey('groups.GroupAccess', null=True, blank=True)
    group_name_prefix = models.CharField(max_length=20, null=True, blank=True)

    def __unicode__(self):
        return self.name

class Member(LoggedClass):
    """Store a person membership in a group"""

    group = models.ForeignKey('groups.Group', verbose_name=_('group'),
        related_name='members')
    member = models.ForeignKey('annuaire.Person', verbose_name=_('member'),
        related_name='groups')
    is_administrator = models.BooleanField(default=False)

    start_date = models.DateField(verbose_name=_('start date'),
        default=timezone.now(), blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True,
        null=True)
    expiration_date = models.DateField(verbose_name=_('expiration date'), blank=True,
        null=True)

    def __unicode__(self):
        return self.member.complete_name

class GroupManager(models.Manager):

    def get_by_type(self, type):
        return Group.objects.filter(type__name=type)

    def active(self):
        return Group.objects.filter(is_active=True)

class GroupRole(models.Model):

    name =  models.CharField(verbose_name=_('name'), max_length=100)
    rank = models.IntegerField(verbose_name=_('default rank'))

    def __unicode__(self):
        return self.name

class GroupHead(models.Model):

    group = models.OneToOneField('groups.Group', verbose_name=_('group'))
    name = models.CharField(verbose_name=_('name'), max_length=100)
    access = models.ForeignKey('groups.GroupAccess', null=True, blank=True)

    def __unicode__(self):
        return self.name+' '+self.group.name

class GroupLeader(models.Model):

    grouphead = models.ForeignKey('groups.GroupHead', verbose_name=_('council'))
    role = models.ForeignKey('groups.GroupRole', verbose_name=_('role'))
    person = models.ForeignKey(Person, verbose_name=_('member'),
        related_name='council_roles')

    start_date = models.DateField(verbose_name=_('start date'),
        default=timezone.now(), blank=True, null=True)
    end_date = models.DateField(verbose_name=_('end date'),
        blank=True, null=True)
    board_member = models.BooleanField(default=False)

    rank = models.IntegerField(verbose_name=_('rank'), null=True, blank=True)
    title = models.CharField(verbose_name=_('title'), max_length=100, \
        null=True, blank=True)

    def get_title(self):
        if self.title:
            return self.title
        else:
            return self.role.name 

    def get_by_category(self, category):
        return self.objects.filter(grouphead__group__type=category)


class Group(LoggedClass):
    """Regional Group"""

    slug = models.CharField(verbose_name=_('slug'), max_length=50,
        unique=True)
    name = models.CharField(verbose_name=_('name'), max_length=100)
    about = models.TextField(verbose_name=_('description'), blank=True,
        null=True)

    is_active = models.BooleanField(verbose_name=_('active'), default=True)

    type = models.ForeignKey('groups.GroupType', null=True, blank=True)
    access = models.ForeignKey('groups.GroupAccess', null=True, blank=True)
    private = models.BooleanField(default=False)

    web_site = models.URLField(verbose_name=_('web site'), max_length=50,
        blank=True, null=True)
    email = models.EmailField(verbose_name=_('email'), max_length=50,
         blank=True, null=True)
    icon = models.ImageField(verbose_name=_('icon'), upload_to='data/',
         blank=True, null=True)

    # forum = forum point
    # album = photo album
    # links =
    # videos =
    # wall =

    objects = GroupManager()

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


    def get_absolute_url(self):
        return reverse('ain7.groups.views.details', args=[self.id])

    def has_for_member(self, person):
        """professionnal group membership test"""
        return self.members.filter(member=person)\
            .exclude(end_date__isnull=False,\
            end_date__lte=timezone.now())\
            .filter(start_date__lte=timezone.now())\
            .count() != 0

    def active_members(self):
        """current group members"""
        from django.db.models import Q
        return [ ms.member for ms in self.members.filter(Q(start_date__lte=\
            datetime.date.today()), Q(end_date__gte=datetime.date.today()) \
            | Q(end_date__isnull=True)) ]

    def all_members(self):
        """all group members"""
        from django.db.models import Q
        return [ ms.member for ms in self.members.all() ]

    def has_for_board_member(self, person):
        """check board member for a regional group"""
        has_role = False
        if self.grouphead:
            for role in self.grouphead.groupleader_set.filter(person=person)\
               .filter(start_date__lte=timzone.now()):
                if not role.end_date or role.end_date > timezone.now():
                    has_role = True
        return has_role

    def board_members(self):
        return self.members

    def add(self, person):
        member = Member()
        member.group = self
        member.member = person
        member.start_date = datetime.date.today()
        member.save()

    def remove(self, person):
        try:
            member = Member.objects.get(group=self, member=person)
            member.end_date = datetime.date.today()
            member.save()
        except Member.DoesNotExist:
            pass
        except Member.MultipleObjectsReturned:
            # FIXME: wtf!
            pass

    def get_group_head(self):
        from django.db.models import Q 
        return [ {'id': rol.id, 'title': rol.get_title(), 'person': rol.person} for rol in GroupLeader.objects.filter(Q(grouphead__group=self), Q(start_date__lte=datetime.date.today()), Q(end_date__gte=datetime.date.today()) | Q(end_date__isnull=True)).order_by('rank', 'role__rank', 'person__last_name', 'person__first_name') ] 

    def get_group_head_history(self):
        from django.db.models import Q 
        return [ {'id': rol.id, 'title': rol.get_title(), 'person': rol.person} for rol in GroupLeader.objects.filter(grouphead__group=self).order_by('rank', 'role__rank', 'person__last_name', 'person__first_name') ] 

