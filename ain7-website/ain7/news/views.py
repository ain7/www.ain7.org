# -*- coding: utf-8
#
# news/views.py
#
#   Copyright (C) 2007-2008 AIn7
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
from django.core.paginator import ObjectPaginator, InvalidPage
from django import newforms as forms
from django.http import HttpResponseRedirect
from django.template import RequestContext

from ain7.news.models import NewsItem
from ain7.utils import ain7_render_to_response, ImgUploadForm, form_callback
from ain7.decorators import confirmation_required


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
   image = news_item.image

   NewsForm = forms.models.form_for_instance(news_item,
                                             formfield_callback=_form_callback)

   if request.method == 'POST':
        f = NewsForm(request.POST.copy())
        if f.is_valid():
            f.clean_data['image'] = image
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

@confirmation_required(lambda news_id=None, object_id=None : '', 'base.html', _('Do you really want to delete the image of this news'))
@login_required
def image_delete(request, news_id):

    news_item = get_object_or_404(NewsItem, pk=news_id)
    news_item.image = None
    news_item.save()

    request.user.message_set.create(message=
        _('The image of this news item has been successfully deleted.'))
    return HttpResponseRedirect('/actualites/%s/edit/' % news_id)

@login_required
def write(request):

    NewsForm = forms.models.form_for_model(NewsItem,
                                           formfield_callback=_form_callback)

    if request.method == 'POST':
        f = NewsForm(request.POST.copy())
        if f.is_valid():
            f.clean_data['image'] = None
            f.save()

        request.user.message_set.create(message=_('News successfully added.'))

        #return HttpResponseRedirect('/evenements/%s/' % (f.id))
        return HttpResponseRedirect('/actualites/')

    f = NewsForm()

    return ain7_render_to_response(request, 'news/write.html', {'form': f})

def search(request):

    form = SearchNewsForm()
    nb_results_by_page = 25
    list_news = False
    paginator = ObjectPaginator(NewsItem.objects.none(),nb_results_by_page)
    page = 1

    if request.method == 'POST':
        form = SearchNewsForm(request.POST)
        if form.is_valid():
            list_news = NewsItem.objects.filter(title__icontains=form.clean_data['title'],
                                                        description__icontains=form.clean_data['content'])

            paginator = ObjectPaginator(list_news,nb_results_by_page)

            try:
                page = int(request.GET.get('page', '1'))
                list_news = paginator.get_page(page - 1)

            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'news/search.html',
                                {'form': form, 'list_news': list_news,
                                 'request': request,'paginator': paginator, 'is_paginated': paginator.pages > 1,
                                 'has_next': paginator.has_next_page(page - 1),
                                 'has_previous': paginator.has_previous_page(page - 1),
                                 'current_page': page,
                                 'next_page': page + 1,
                                 'previous_page': page - 1,
                                 'pages': paginator.pages,
                                 'first_result': (page - 1) * nb_results_by_page +1,
                                 'last_result': min((page) * nb_results_by_page, paginator.hits),
                                 'hits' : paginator.hits,})

# une petite fonction pour exclure certains champs
# des formulaires crees avec form_for_model et form_for_instance
def _form_callback(f, **args):
  exclude_fields = ('image')
  if f.name in exclude_fields:
    return None
  return form_callback(f, **args)
