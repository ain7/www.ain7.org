# -*- coding: utf-8
#
# news/views.py
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

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django import newforms as forms
from django.http import HttpResponseRedirect
from django.template import RequestContext

from ain7.news.models import NewsItem
from ain7.utils import ain7_render_to_response, ImgUploadForm


class SearchNewsForm(forms.Form):
    title = forms.CharField(label=_('News title'), max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))
    date = forms.DateField(label=_('Date'), required=False, widget=forms.TextInput(attrs={'size':'50'}))
    content = forms.CharField(label=_('News content'), max_length=50, required=False, widget=forms.TextInput(attrs={'size':'50'}))


def index(request):
    news = NewsItem.objects.all().order_by('-creation_date')[:20]
    return ain7_render_to_response(request, 'news/index.html', {'news': news })

def details(request, news_id):
    news_item = get_object_or_404(NewsItem, pk=news_id)
    return ain7_render_to_response(request, 'news/details.html',
                            {'news_item': news_item})


@login_required
def edit(request, news_id):

   news_item = get_object_or_404(NewsItem, pk=news_id)

   NewsForm = forms.models.form_for_instance(news_item,
                                             formfield_callback=_form_callback)

   if request.method == 'POST':
        f = NewsForm(request.POST.copy(), formfield_callback=_form_callback)
        if f.is_valid():
            f.save()

        request.user.message_set.create(message=_('News successfully updated.'))

        return HttpResponseRedirect('/actualites/%s/' % (news_item.id))

   f = NewsForm()

   return ain7_render_to_response(request, 'news/edit.html', 
                           {'form': f, 'news_item':news_item})

@login_required
def image_edit(request, news_id):

    news_item = get_object_or_404(NewsItem, pk=news_id)

    if request.method == 'GET':
        form = ImgUploadForm()
        filename = None
        if news_item.image:
            filename = '/site_media/%s' % news_item.image
        return ain7_render_to_response(request, 'pages/image.html',
            {'section': 'base.html', 'name': _("image").capitalize(),
             'form': form, 'filename': filename})
    else:
        post = request.POST.copy()
        post.update(request.FILES)
        form = ImgUploadForm(post)
        if form.is_valid():
            news_item.save_image_file(
                form.clean_data['img_file']['filename'],
                form.clean_data['img_file']['content'])
            request.user.message_set.create(message=_("The picture has been successfully changed."))
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))
        return HttpResponseRedirect('/actualites/%s/edit/' % news_item.id)

@login_required
def write(request):

    NewsForm = forms.models.form_for_model(NewsItem,
                                           formfield_callback=_form_callback)

    if request.method == 'POST':
        f = NewsForm(request.POST.copy(), formfield_callback=_form_callback)
        if f.is_valid():
            f.save()

        request.user.message_set.create(message=_('Event successfully added.'))

        #return HttpResponseRedirect('/evenements/%s/' % (f.id))
        return HttpResponseRedirect('/actualites/')

    f = NewsForm()

    return ain7_render_to_response(request, 'news/write.html', {'form': f})

def search(request):

    if request.method == 'POST':
        form = SearchNewsForm(request.POST)
        if form.is_valid():
                    list_news = NewsItem.objects.filter(title__icontains=form.clean_data['title'],
                                                        description__icontains=form.clean_data['content'])

        return ain7_render_to_response(request, 'news/search.html', 
                                {'form': form, 'list_news': list_news, 
                                 'request': request})

    else:
        f = SearchNewsForm()
        return ain7_render_to_response(request, 'news/search.html', {'form': f})


# une petite fonction pour exclure certains champs
# des formulaires crees avec form_for_model et form_for_instance
def _form_callback(f, **args):
  exclude_fields = ('image')
  if f.name in exclude_fields:
    return None
  return f.formfield(**args)
