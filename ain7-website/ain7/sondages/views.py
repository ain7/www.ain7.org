# -*- coding: utf-8
#
# sondages/views.py
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
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django import newforms as forms

from ain7.sondages.models import Choice, Survey, Vote

def index(request):
    surveys = Survey.objects.all()

    return render_to_response('sondages/index.html', {'surveys': surveys})


def view(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    already_vote = request.user.is_authenticated()\
                    and survey.has_been_voted_by(request.user.person)

    return render_to_response('sondages/view.html', 
                             {'survey': survey, 'already_vote': already_vote},
                              context_instance=RequestContext(request))

@login_required
def vote(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    voter = request.user.person
    if not survey.has_been_voted_by(voter):
        try:
            choice = survey.choices.get(pk=request.GET['choice'])
        except (KeyError, Choice.DoesNotExist):
            # Go to vote form
            return render_to_response('sondages/vote.html', 
                                     {'survey': survey},
                                     context_instance=RequestContext(request))
        else:
            # Create vote
            request.user.message_set.create(message=_("Your vote has been registered."))
            vote = Vote(choice=choice, voter=voter, survey=survey)
            vote.save()
    else :
        # Already voted
        request.user.message_set.create(message=_("You have already vote for this survey."))

    return HttpResponseRedirect('/sondages/%s/view' % (survey.id))

@login_required
def create(request):
    Form = forms.models.form_for_model(Survey)

    return generic_form(request, None, Form, _("Survey creation"), _("Survey succesfully created."))

@login_required
def details(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)

    return render_to_response('sondages/details.html',
                              {'survey': survey},
                              context_instance=RequestContext(request))

@login_required
def edit(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    Form = forms.models.form_for_instance(survey)

    return generic_form(request, None, Form, _("Survey edition"), _("Survey succesfully updated."))


@login_required
def delete(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)

    if request.method != 'POST':
        return render_to_response('pages/confirm.html',
                                  {'message': _("Do you really want to delete this survey?"),
                                   'description': str(survey), 'section': "sondages/base.html"},
                                  context_instance=RequestContext(request))
    else:
        if request.POST['choice']=="1":
            survey.delete()
            request.user.message_set.create(message=_("Survey successfully deleted."))
        return HttpResponseRedirect('/sondages/')

@login_required
def choice_add(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    Form = forms.models.form_for_model(Choice, formfield_callback=form_callback)

    return generic_form(request, survey, Form, _("Choice creation"), _("Choice succesfully added."))

@login_required
def choice_edit(request, survey_id, choice_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    choice = get_object_or_404(Choice, pk=choice_id)
    Form = forms.models.form_for_instance(choice, formfield_callback=form_callback)

    return generic_form(request, survey, Form, _("Choice edition"), _("Choice succesfully updated."))

@login_required
def choice_delete(request, survey_id, choice_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    choice = get_object_or_404(Choice, pk=choice_id)

    if request.method != 'POST':
        return render_to_response('pages/confirm.html',
                                  {'message': _("Do you really want to delete this choice?"),
                                   'description': str(choice), 'section': "sondages/base.html"},
                                  context_instance=RequestContext(request))
    else:
        if request.POST['choice']=="1":
            choice.delete()
            request.user.message_set.create(message=_("Choice successfully deleted."))
        return HttpResponseRedirect('/sondages/%s/details/' % survey.id)


def generic_form(request, survey, Form, title, message):
    form = Form()

    if request.method == 'POST':
        form = Form(request.POST.copy())
        if form.is_valid():
            if survey is not None:
                form.clean_data['survey'] = survey
                form.save()
            else:
                survey = form.save()
            request.user.message_set.create(message=message)
            return HttpResponseRedirect('/sondages/%s/details/' % survey.id)
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))

    return render_to_response('sondages/form.html',
                              {'form': form, 'title': title},
                              context_instance=RequestContext(request))

def form_callback(field, **args):
  if field.name == "survey":
    return None
  return field.formfield(**args)