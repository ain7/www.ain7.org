# -*- coding: utf-8
"""
 ain7/forums/models.py
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

import datetime

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.template.defaultfilters import truncatewords
from django.utils.translation import ugettext as _

from ain7.utils import LoggedClass, isAdmin


class ForumAccess(models.Model):
    group = models.ForeignKey('groups.Group')
    level = models.IntegerField(default=0)
    description = models.CharField(max_length=200, blank=True, null=True)

    def __unicode__(self):
         return self.description

class Forum(models.Model):
    name = models.CharField(max_length = 100)
    group = models.ForeignKey('groups.Group')
    access = models.ForeignKey('forums.ForumAccess')

    def __unicode__(self):
        return self.name

class SuperCategory(models.Model):
    forum = models.ForeignKey('forums.Forum')
    name = models.CharField(max_length = 100)
    description = models.TextField(default='')
    rank = models.PositiveIntegerField(default = 1)

    access = models.ForeignKey('forums.ForumAccess')
    
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='forum_super_categories_created')
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='forum_super_categories_updated')

    class Meta:
        verbose_name = "Super Category"
        verbose_name_plural = "Super Categories"
        ordering = ('-rank', 'created_on')
        
    def __unicode__(self):
        return self.name


class ForumCategory(models.Model):
    super_category = models.ForeignKey(SuperCategory)    
    name = models.CharField(max_length = 100)
    slug = models.SlugField(max_length = 110)
    description = models.TextField(default='')
    rank = models.PositiveIntegerField(default = 1)

    moderated_by = models.ManyToManyField(User, related_name='moderaters')
    access = models.ForeignKey('forums.ForumAccess')
    
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='forum_categories_created')
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='forum_categories_updated')

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ('rank','-created_on' )    
    
    
    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.name)
            same_slug_count = Category.objects.filter(slug__startswith = slug).count()
            if same_slug_count:
                slug = slug + str(same_slug_count)
            self.slug = slug
        super(Category, self).save(*args, **kwargs)


class ForumTopic(models.Model):
    category = models.ForeignKey('forums.ForumCategory')
    
    subject = models.CharField(max_length=999)
    slug = models.SlugField(max_length = 200, db_index = True) 
    message = models.TextField()
    file = models.FileField(upload_to='data/forum/files',default='',null=True,blank=True)
    attachment_type = models.CharField(max_length=20,default='nofile')
    filename = models.CharField(max_length=100,default="dummyname.txt")
    viewcount = models.IntegerField(default=0)
    replies = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='forum_topics_created')
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='forum_topics_updated')
    
    last_reply_on = models.DateTimeField(auto_now_add=True)
    num_replies = models.PositiveSmallIntegerField(default = 0)
    
    #Moderation features
    announcement_flag = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    is_sticky = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    class Meta:
        ordering = ('-is_sticky', '-last_reply_on',)
        get_latest_by = ('created_on')
        verbose_name = "Topic"
        verbose_name_plural = "Topics"
        
    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.subject)
            slug = slug[:198]
            same_slug_count = Ftopics.objects.filter(slug__startswith = slug).count()
            if same_slug_count:
                slug = slug + str(same_slug_count)
            self.slug = slug
        super(Ftopics, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.subject
    
class ForumReply(models.Model):
    topic = models.ForeignKey('forums.ForumTopic')
    
    message = models.TextField()
    file = models.FileField(upload_to='data/forum/files',default='',null=True,blank=True)
    attachment_type = models.CharField(max_length=20,default='nofile')
    filename = models.CharField(max_length=100,default="dummyname.txt")
    
    is_hidden = models.BooleanField(default=False)
    reply_number = models.SmallIntegerField()

    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='forum_replies_created')
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name='forum_replies_updated')
    
    
    class Meta:
        verbose_name = "Reply"
        verbose_name_plural = "Replies"
        ordering = ('created_on',)
        get_latest_by = ('created_on', )
        
    def save(self, *args, **kwargs):
        if not self.pk:
            self.reply_number = self.topic.reply_set.all().count() + 1
        super(Reply, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return truncatewords(self.message, 10)

