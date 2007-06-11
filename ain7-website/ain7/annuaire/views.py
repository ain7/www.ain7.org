# -*- coding: utf-8
#
# annuaire/views.py
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

from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django import newforms as forms

from ain7.annuaire.models import Person, AIn7Member, Address, PhoneNumber
from ain7.annuaire.models import Track, Email, ClubMembership
from ain7.annuaire.models import Promo

class SearchPersonForm(forms.Form):
    last_name = forms.CharField(label=_('Last name'), max_length=50, required=False)
    first_name = forms.CharField(label=_('First name'), max_length=50, required=False)
    promo = forms.IntegerField(label=_('Promo'), required=False)
    track = forms.IntegerField(label=_('Track'), required=False)

@login_required
def detail(request, person_id):
    p = get_object_or_404(Person, pk=person_id)
    ain7member = get_object_or_404(AIn7Member, person=p)
    return render_to_response('annuaire/details.html', 
                             {'person': p, 'user': request.user,
                              'ain7member': ain7member}, 
                              context_instance=RequestContext(request))

@login_required
def search(request):
    maxTrackId=Track.objects.order_by('-id')[0].id+1
    trackList=[(maxTrackId,'Toutes')]
    for track in Track.objects.all():
        trackList.append((track.id,track.name))
    SearchPersonForm.base_fields['track'].widget=\
        forms.Select(choices=trackList)

    if request.method == 'POST':
        form = SearchPersonForm(request.POST)
        if form.is_valid():

            # criteres sur le nom et prenom
            criteria={'person__last_name__contains':form.clean_data['last_name'],\
                      'person__first_name__contains':form.clean_data['first_name']}
            # ici on commence par rechercher toutes les promos
            # qui concordent avec l'annee de promotion et la filiere
            # saisis par l'utilisateur.
            promoCriteria={}
            if form.clean_data['promo']!=None:
                promoCriteria['year']=form.clean_data['promo']
            if form.clean_data['track']!=maxTrackId:
                promoCriteria['track']=\
                    Track.objects.get(id=form.clean_data['track'])
                
            # on ajoute ces promos aux critères de recherche
            # si elle ne sont pas vides
            if len(promoCriteria)!=0:
                criteria['promos__in']=Promo.objects.filter(**promoCriteria)
                
            ain7members = AIn7Member.objects.filter(**criteria)

            return render_to_response('annuaire/index.html', 
                                     {'ain7members': ain7members,
                                      'user': request.user},
                                      context_instance=RequestContext(request))

    else:
        f = SearchPersonForm()
        return render_to_response('annuaire/search.html', 
                                 {'form': f , 'user': request.user},
                                 context_instance=RequestContext(request))

@login_required
def edit(request, person_id=None):

    p = get_object_or_404(Person, pk=person_id)
    ain7member = get_object_or_404(AIn7Member, person=p)
    return render_to_response('annuaire/edit.html',
                              {'person': p, 'user': request.user,
                               'ain7member': ain7member},
                              context_instance=RequestContext(request))

@login_required
def person_edit(request, user_id=None):

    if user_id is None:
        PersonForm = forms.models.form_for_model(Person,
            formfield_callback=form_callback)
        form = PersonForm()

    else:
        person = Person.objects.get(user=user_id)
        PersonForm = forms.models.form_for_instance(person,
            formfield_callback=form_callback)
        PersonForm.base_fields['sex'].widget=\
            forms.Select(choices=Person.SEX)
        form = PersonForm(auto_id=False)

        if request.method == 'POST':
             form = PersonForm(request.POST)
             if form.is_valid():
                 form.clean_data['user'] = person.user
                 form.save()
                 request.user.message_set.create(message=_("Modifications have been successfully saved."))
                 return HttpResponseRedirect('/annuaire/%s/edit' % (person.user.id))
    return render_to_response('annuaire/edit_form.html', 
                             {'form': form, 'user': request.user,
                              'action_title': _("Modification of personal data")},
                             context_instance=RequestContext(request))

@login_required
def ain7member_edit(request, user_id=None):

    if user_id is None:
        PersonForm = forms.models.form_for_model(AIn7Member,
            formfield_callback=form_callback)
        form = PersonForm()

    else:
        person = Person.objects.get(user=user_id)
        ain7member = get_object_or_404(AIn7Member, person=person)
        PersonForm = forms.models.form_for_instance(ain7member,
            formfield_callback=form_callback)
        form = PersonForm(auto_id=False)

        if request.method == 'POST':
             form = PersonForm(request.POST)
             if form.is_valid():
                 form.clean_data['person'] = person
                 form.save()
                 request.user.message_set.create(message=_("Modifications have been successfully saved."))
                 return HttpResponseRedirect('/annuaire/%s/edit' % (person.user.id))
    return render_to_response('annuaire/edit_form.html', 
                             {'form': form, 'user': request.user,
                              'action_title':
                              _("Modification of personal data for ") +
                              str(person)},
                             context_instance=RequestContext(request))

@login_required
def generic_edit(request, user_id, object_id, object_type,
                  person, ain7member, action_title, msg_done):

    obj = get_object_or_404(object_type, pk=object_id)

    # 1er passage : on propose un formulaire avec les données actuelles
    if request.method == 'GET':
        PosForm = forms.models.form_for_instance(obj,
            formfield_callback=form_callback)
        f = PosForm()
        return render_to_response('annuaire/edit_form.html',
                                 {'form': f, 'user': request.user, 
                                  'action_title': action_title},
                                  context_instance=RequestContext(request))
    
    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        PosForm = forms.models.form_for_instance(obj,
            formfield_callback=form_callback)
        f = PosForm(request.POST.copy())
        if f.is_valid():
            if person is not None:
                f.clean_data['person'] = person
            if ain7member is not None:
                f.clean_data['member'] = ain7member
            f.save()
        request.user.message_set.create(message=msg_done)
        return HttpResponseRedirect('/annuaire/%s/edit/' % user_id)


@login_required
def generic_delete(request, user_id, object_id, object_type,
                   msg_confirm, msg_done):

    obj = get_object_or_404(object_type, pk=object_id)
    
    # 1er passage: on demande confirmation
    if request.method != 'POST':
        msg = msg_confirm
        return render_to_response('pages/confirm.html',
                                  {'message': msg_confirm,
                                  'description': str(obj),
                                  'section': "annuaire/base.html", 
                                  'user': request.user},
                                  context_instance=RequestContext(request))

    # 2eme passage: on supprime si c'est confirmé
    else:
        if request.POST['choice']=="1":
            obj.delete()
            request.user.message_set.create(message=msg_done)
        return HttpResponseRedirect('/annuaire/%s/edit/' % user_id)


@login_required
def generic_add(request, user_id, object_type, person, ain7member,
                action_title, msg_done):

    # 1er passage : on propose un formulaire vide
    if request.method == 'GET':
        PosForm = forms.models.form_for_model(object_type,
            formfield_callback=form_callback)
        f = PosForm()
        return render_to_response('annuaire/edit_form.html',
                                  {'person': person, 'ain7member': ain7member,
                                   'user': request.user, 'form': f,
                                   'action_title': action_title},
                                  context_instance=RequestContext(request))

    # 2e passage : sauvegarde et redirection
    if request.method == 'POST':
        PosForm = forms.models.form_for_model(object_type,
            formfield_callback=form_callback)
        f = PosForm(request.POST.copy())
        if f.is_valid():
            if person is not None:
                f.clean_data['person'] = person
            if ain7member is not None:            
                f.clean_data['member'] = ain7member
            f.save()
        request.user.message_set.create(message=msg_done)
        return HttpResponseRedirect('/annuaire/%s/edit/' % user_id)

# Adresses

def address_edit(request, user_id=None, address_id=None):

    return generic_edit(request, user_id, address_id, Address,
                        get_object_or_404(Person, user=user_id), None,
                        _("Modification of an address"),
                        _("Address informations updated successfully."))

def address_delete(request, user_id=None, address_id=None):

    return generic_delete(request, user_id, address_id, Address, 
                          _("Do you really want to delete this address?"),
                          _("Address successfully deleted."))

def address_add(request, user_id=None):

    return generic_add(request, user_id, Address,
                        get_object_or_404(Person, user=user_id), None,
                       _("Creation of an address"),
                       _("Address successfully added."))

# Numeros de telephone

def phone_edit(request, user_id=None, phone_id=None):

    return generic_edit(request, user_id, phone_id, PhoneNumber,
                        get_object_or_404(Person, user=user_id), None,
                        _("Modification of a phone number"),
                        _("Phone number informations updated successfully."))

def phone_delete(request, user_id=None, phone_id=None):

    return generic_delete(request, user_id, phone_id, PhoneNumber, 
                          _("Do you really want to delete this phone number?"),
                          _("Phone number successfully deleted."))

def phone_add(request, user_id=None):

    return generic_add(request, user_id, PhoneNumber,
                       get_object_or_404(Person, user=user_id), None,
                       _("Creation of a phone number"),
                       _("Phone number successfully added."))

# Adresses de courriel

def email_edit(request, user_id=None, email_id=None):

    return generic_edit(request, user_id, email_id, Email,
                        get_object_or_404(Person, user=user_id), None,
                        _("Modification of an email address"),
                        _("Email informations updated successfully."))

def email_delete(request, user_id=None, email_id=None):

    return generic_delete(request, user_id, email_id, Email, 
                          _("Do you really want to delete this email address?"),
                          _("Email address successfully deleted."))

def email_add(request, user_id=None):

    return generic_add(request, user_id, Email,
                       get_object_or_404(Person, user=user_id), None,
                       _("Creation of an email address"),
                       _("Email address successfully added."))

# Comptes de messagerie instantanée

def im_edit(request, user_id=None, im_id=None):

    return generic_edit(request, user_id, im_id, InstantMessaging,
                        get_object_or_404(Person, user=user_id), None,
                        _("Modification of an instant messaging account"),
                        _("Instant messaging informations updated successfully."))

def im_delete(request, user_id=None, im_id=None):

    return generic_delete(request, user_id, im_id, InstantMessaging, 
                          _("Do you really want to delete this instant messaging account?"),
                          _("Instant messaging account successfully deleted."))

def im_add(request, user_id=None):

    return generic_add(request, user_id, Im,
                       get_object_or_404(Person, user=user_id), None,
                       _("Creation of an instant messaging account"),
                       _("Instant messaging account successfully added."))

# Comptes IRC

def irc_edit(request, user_id=None, irc_id=None):

    return generic_edit(request, user_id, irc_id, IRC,
                        get_object_or_404(Person, user=user_id), None,
                        _("Modification of an IRC account"),
                        _("IRC account informations updated successfully."))

def irc_delete(request, user_id=None, irc_id=None):

    return generic_delete(request, user_id, irc_id, IRC, 
                          _("Do you really want to delete this IRC account?"),
                          _("IRC account successfully deleted."))

def irc_add(request, user_id=None):

    return generic_add(request, user_id, IRC,
                       get_object_or_404(Person, user=user_id), None,
                       _("Creation of an IRC account"),
                       _("IRC account successfully added."))

# Sites Internet

def website_edit(request, user_id=None, website_id=None):

    return generic_edit(request, user_id, website_id, WebSite,
                        get_object_or_404(Person, user=user_id), None,
                        _("Modification of a website"),
                        _("Website informations updated successfully."))

def website_delete(request, user_id=None, website_id=None):

    return generic_delete(request, user_id, website_id, WebSite, 
                          _("Do you really want to delete this website?"),
                          _("Website successfully deleted."))

def website_add(request, user_id=None):

    return generic_add(request, user_id, WebSite,
                       get_object_or_404(Person, user=user_id), None,
                       _("Creation of a website"),
                       _("Website successfully added."))

# Vie associative a l'n7

@login_required
def club_membership_edit(request, user_id=None, club_membership_id=None):

    person = get_object_or_404(Person, user=user_id)
    return generic_edit(request, user_id, club_membership_id, ClubMembership,
                        person, get_object_or_404(AIn7Member, person=person),
                        _("Modification of a club membership"),
                        _("Club membership informations updated successfully."))

def club_membership_delete(request, user_id=None, club_membership_id=None):

    return generic_delete(request, user_id, club_membership_id,ClubMembership, 
                          _("Do you really want to delete this club membership?"),
                          _("Club membership successfully deleted."))

def club_membership_add(request, user_id=None):

    person = get_object_or_404(Person, user=user_id)
    return generic_add(request, user_id, ClubMembership,
                       person, get_object_or_404(AIn7Member, person=person),
                       _("Creation of a club membership"),
                       _("Club membership successfully added."))

# une petite fonction pour exclure les champs
# person user ain7member
# des formulaires créés avec form_for_model et form_for_instance
def form_callback(f, **args):
  exclude_fields = ("person", "user", "member")
  if f.name in exclude_fields:
    return None
  return f.formfield(**args)
