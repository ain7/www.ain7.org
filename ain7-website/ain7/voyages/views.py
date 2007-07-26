# -*- coding: utf-8
#
# voyages/views.py
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
from django import newforms as forms
from django.newforms import widgets
from django.http import HttpResponseRedirect
from datetime import datetime
from django.contrib.auth.decorators import login_required
from ain7.decorators import confirmation_required
from ain7.utils import ain7_render_to_response, ImgUploadForm

from ain7.voyages.models import Travel, Subscription, TravelResponsible
from ain7.annuaire.models import Person

class SearchTravelForm(forms.Form):
    label = forms.CharField(label=_('label').capitalize(),
                            max_length=50, required=False)
    date  = forms.CharField(label=_('date').capitalize(),
                            max_length=50, required=False)
    visited_places = forms.CharField(label=_('visited places').capitalize(),
                                     max_length=50, required=False)

    def __init__(self, *args, **kwargs):
        super(SearchTravelForm, self).__init__(*args, **kwargs)

    def search(self):
        criteria={
            'label__contains':self.clean_data['label'],
            'date__contains':self.clean_data['date'],
            'visited_places__contains':self.clean_data['visited_places']}
        return Travel.objects.filter(**criteria)


def index(request):
    next_travels = Travel.objects.filter(start_date__gte=datetime.now())
    prev_travels = Travel.objects.filter(start_date__lt=datetime.now())[:5]
    return ain7_render_to_response(request, 'voyages/index.html',
                            {'next_travels': next_travels,
                             'previous_travels': prev_travels})

@login_required
def add(request):
    TravelForm = forms.models.form_for_model(Travel,
                                             formfield_callback=_edit_callback)
    TravelForm.base_fields['description'].widget = \
        forms.widgets.Textarea(attrs={'rows':10, 'cols':90})
    TravelForm.base_fields['report'].widget = \
        forms.widgets.Textarea(attrs={'rows':15, 'cols':90})
    form = TravelForm()
    if request.method == 'POST':
        form = TravelForm(request.POST)
        if form.is_valid():
            form.clean_data['thumbnail'] = None
            form.save()
            request.user.message_set.create(
                message=_('The travel has been successfully created.'))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.')+str(form.errors))
        return HttpResponseRedirect('/voyages/')
    return ain7_render_to_response(request, 'voyages/edit.html',
                                   {'form': form, 'action': 'add'})

@confirmation_required(
    lambda user_id=None,
    travel_id=None: str(get_object_or_404(Travel, pk=travel_id)),
    'voyages/base.html',
    _('Do you REALLY want to delete this travel'))
@login_required
def delete(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)
    travel.delete()
    return HttpResponseRedirect('/voyages/')

def detail(request,travel_id):
    t = get_object_or_404(Travel, pk=travel_id)
    past = t in Travel.objects.filter(start_date__lt=datetime.now())
    return ain7_render_to_response(request, 'voyages/details.html',
                            {'travel': t, 'past': past})

def list(request):
    return ain7_render_to_response(request, 'voyages/list.html',
                            {'travels': Travel.objects.all()})

def search(request):
    if request.method == 'GET':
        form = SearchTravelForm()
        return ain7_render_to_response(request, 'voyages/search.html', {'form': form})
    else:
        form = SearchTravelForm(request.POST)
        if form.is_valid():
            return ain7_render_to_response(request, 'voyages/search.html',
                                    {'travels': form.search(), 'form': form,
                                     'request': request})

@login_required
def edit(request, travel_id=None):
    travel = Travel.objects.get(pk=travel_id)
    thumbnail = travel.thumbnail
    TravelForm = forms.models.form_for_instance(travel,
        formfield_callback=_edit_callback)
    TravelForm.base_fields['description'].widget = \
        forms.widgets.Textarea(attrs={'rows':15, 'cols':90})
    TravelForm.base_fields['report'].widget = \
        forms.widgets.Textarea(attrs={'rows':15, 'cols':90})
    form = TravelForm()
    if request.method == 'POST':
        form = TravelForm(request.POST)
        if form.is_valid():
            form.clean_data['thumbnail'] = thumbnail
            form.save()
            request.user.message_set.create(
                message=_("Modifications have been successfully saved."))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.')+str(form.errors))
        return HttpResponseRedirect('/voyages/%s/' % (travel.id))
    return ain7_render_to_response(request, 'voyages/edit.html',
        {'form': form, 'action': 'edit', 'travel': travel})

@login_required
def thumbnail_edit(request, travel_id):

    travel = get_object_or_404(Travel, pk=travel_id)

    if request.method == 'GET':
        form = ImgUploadForm()
        filename = None
        if travel.thumbnail:
            filename = '/site_media/%s' % travel.thumbnail
        return ain7_render_to_response(request, 'pages/image.html',
            {'section': 'voyages/base.html',
             'name': _("thumbnail").capitalize(), 'form': form,
             'filename': filename})
    else:
        post = request.POST.copy()
        post.update(request.FILES)
        form = ImgUploadForm(post)
        if form.is_valid():
            travel.save_thumbnail_file(
                form.clean_data['img_file']['filename'],
                form.clean_data['img_file']['content'])
            request.user.message_set.create(message=_("The picture has been successfully changed."))
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done.")+str(form.errors))
        return HttpResponseRedirect('/voyages/%s/edit/' % travel_id)

@confirmation_required(lambda travel_id=None, object_id=None : '', 'voyages/base.html', _('Do you really want to delete the thumbnail of this travel'))
@login_required
def thumbnail_delete(request, travel_id):

    travel = get_object_or_404(Travel, pk=travel_id)
    travel.thumbnail = None
    travel.save()
    
    request.user.message_set.create(message=
        _('The thumbnail of this travel has been successfully deleted.'))
    return HttpResponseRedirect('/voyages/%s/edit/' % travel_id)

@login_required
def join(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)
    person = request.user.person

    if request.method == 'GET':
        # on vérifie que la personne n'est pas déjà inscrite
        already_subscribed = False 
        for subscription in person.travel_subscriptions.all():
            if subscription.travel == travel:
                already_subscribed = True
        if already_subscribed:
            request.user.message_set.create(message=_('You have already subscribed to this travel.'))
            return HttpResponseRedirect('/voyages/%s/' % (travel.id))
        JoinTravelForm = forms.models.form_for_model(Subscription,
            formfield_callback=_join_callback)
        f = JoinTravelForm()
        return ain7_render_to_response(request, "voyages/join.html",
                                {'form': f, 'travel': travel})
    
    if request.method == 'POST':
        JoinTravelForm = forms.models.form_for_model(Subscription,
            formfield_callback=_join_callback)
        f = JoinTravelForm(request.POST.copy())
        if f.is_valid():
            f.clean_data['subscriber'] = person
            f.clean_data['travel'] = travel
            f.save()
            request.user.message_set.create(message=_('You have been successfully subscribed to this travel.'))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.')+str(f.errors))
        return HttpResponseRedirect('/voyages/%s/' % (travel.id))


@login_required
def subscribe(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)

    if request.method == 'GET':
        SubscribeTravelForm = forms.models.form_for_model(Subscription,
            formfield_callback=_subscribe_callback)
        f = SubscribeTravelForm()
        # TODO : AJAX pour sélectionner une personne plutôt qu'une liste
        return ain7_render_to_response(request, "voyages/join.html",
                                {'form': f, 'travel': travel})
    
    if request.method == 'POST':
        SubscribeTravelForm = forms.models.form_for_model(Subscription,
            formfield_callback=_subscribe_callback)
        f = SubscribeTravelForm(request.POST.copy())
        person = Person.objects.filter(pk=request.POST['subscriber'])[0]
        # on vérifie que la personne n'est pas déjà inscrite
        already_subscribed = False 
        for subscription in person.travel_subscriptions.all():
            if subscription.travel == travel:
                already_subscribed = True
        if already_subscribed:
            request.user.message_set.create(message=_('This person is already subscribed to this travel.'))
            return ain7_render_to_response(request, 'voyages/participants.html',
                                    {'travel': travel})
        else:
            if f.is_valid():
                f.clean_data['travel'] = travel
                f.save()
                request.user.message_set.create(message=_('You have successfully subscribed someone to this travel.'))
            else:
                request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.')+str(f.errors))
            return ain7_render_to_response(request, 'voyages/participants.html',
                                    {'travel': travel})
    return HttpResponseRedirect('/voyages/%s/' % (travel.id))

@confirmation_required(
    lambda user_id=None, travel_id=None, participant_id=None:
    str(get_object_or_404(Person, pk=participant_id)),
    'voyages/base.html',
    _('Do you really want to unsubscribe this participant'))
@login_required
def unsubscribe(request, travel_id, participant_id):
    travel = get_object_or_404(Travel, pk=travel_id)
    participant = get_object_or_404(Person, pk=participant_id)
    subscription = get_object_or_404(Subscription, travel=travel, subscriber=participant_id)
    subscription.delete()
    return ain7_render_to_response(request, 'voyages/participants.html',
                            {'travel': travel})

@login_required
def participants(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)
    return ain7_render_to_response(request, 'voyages/participants.html',
                            {'travel': travel})

@login_required
def responsibles(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)
    return ain7_render_to_response(request, 'voyages/responsibles.html',
                            {'travel': travel})

@login_required
def responsibles_add(request, travel_id):
    travel = get_object_or_404(Travel, pk=travel_id)

    if request.method == 'GET':
        TravelResponsibleForm = forms.models.form_for_model(TravelResponsible,
            formfield_callback=_subscribe_callback)
        f = TravelResponsibleForm()
        # TODO : AJAX pour sélectionner une personne plutôt qu'une liste
        return ain7_render_to_response(request, "voyages/join.html",
                                {'form': f, 'travel': travel})
    
    if request.method == 'POST':
        TravelResponsibleForm = forms.models.form_for_model(TravelResponsible,
            formfield_callback=_subscribe_callback)
        f = TravelResponsibleForm(request.POST.copy())
        person = Person.objects.filter(pk=request.POST['responsible'])[0]
        # on vérifie que la personne n'est pas déjà inscrite
        already_responsible = False 
        for responsibility in person.travel_responsibilities.all():
            if responsibility.travel == travel:
                already_responsible = True
        if already_responsible:
            request.user.message_set.create(message=_('This person is already responsible of this travel.'))
            return ain7_render_to_response(request, 'voyages/responsibles.html',
                                    {'travel': travel})
        else:
            if f.is_valid():
                f.clean_data['travel'] = travel
                f.save()
                request.user.message_set.create(message=_('You have successfully added someone to responsibles of this travel.'))
            else:
                request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.')+str(f.errors))
            return ain7_render_to_response(request, 'voyages/responsibles.html',
                                    {'travel': travel})
    return HttpResponseRedirect('/voyages/%s/' % (travel.id))

@confirmation_required(
    lambda user_id=None, travel_id=None, responsible_id=None:
    str(get_object_or_404(Person, pk=responsible_id)),
    'voyages/base.html',
    _('Do you really want this person not to be responsible of this travel'))
@login_required
def responsibles_delete(request, travel_id, responsible_id):
    travel = get_object_or_404(Travel, pk=travel_id)
    responsible = get_object_or_404(Person, pk=responsible_id)
    travelResponsible = get_object_or_404(TravelResponsible,
        responsible=responsible, travel=travel)
    travelResponsible.delete()
    return ain7_render_to_response(request, 'voyages/responsibles.html',
                            {'travel': travel})

# une petite fonction pour exclure certains champs
# des formulaires créés avec form_for_model et form_for_instance
def _edit_callback(f, **args):
    exclude_fields = ('thumbnail')
    if f.name in exclude_fields:
        return None
    return f.formfield(**args)

def _join_callback(f, **args):
    exclude_fields = ('subscriber', 'travel')
    if f.name in exclude_fields:
        return None
    return f.formfield(**args)

def _subscribe_callback(f, **args):
    exclude_fields = ('travel')
    if f.name in exclude_fields:
        return None
    return f.formfield(**args)

