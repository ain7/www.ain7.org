# -*- coding: utf-8
#
# sondages/views.py
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
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django import newforms as forms
from django.utils.translation import ugettext as _

from ain7.annuaire.models import UserContributionType, UserContribution
from ain7.sondages.models import Choice, Survey, Vote
from ain7.sondages.forms import *
from ain7.decorators import confirmation_required
from ain7.utils import ain7_render_to_response

def index(request):
    surveys = Survey.objects.all()

    return ain7_render_to_response(request, 'sondages/index.html',
                            {'surveys': surveys})


def view(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    already_vote = request.user.is_authenticated()\
                    and survey.has_been_voted_by(request.user.person)

    return ain7_render_to_response(request, 'sondages/view.html',
                             {'survey': survey, 'already_vote': already_vote})

@login_required
def vote(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    voter = request.user.person
    if not survey.has_been_voted_by(voter):
        try:
            choice = survey.choices.get(pk=request.GET['choice'])
        except (KeyError, Choice.DoesNotExist):
            # Go to vote form
            return ain7_render_to_response(request, 'sondages/vote.html',
                                     {'survey': survey})
        else:
            # Create vote
            request.user.message_set.create(message=_('Your vote has been registered.'))
            vote = Vote(choice=choice, voter=voter, survey=survey)
            vote.save()
            contrib_type = UserContributionType.objects.filter(key='poll_vote')[0]
            contrib = UserContribution(user=voter, type=contrib_type)
            contrib.save()
    else :
        # Already voted
        request.user.message_set.create(message=_('You have already vote for this survey.'))
    return HttpResponseRedirect('/sondages/%s/view' % (survey.id))

@login_required
def create(request):
    return _form(request, None, SurveyForm, None,
                 _('Survey creation'), _('Survey succesfully created.'))

@login_required
def details(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    return ain7_render_to_response(request, 'sondages/details.html',
                            {'survey': survey})

@login_required
def edit(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    return _form(request, None, SurveyForm, survey,
                 _('Survey edition'), _('Survey succesfully updated.'))

@confirmation_required(lambda survey_id: str(get_object_or_404(Survey, pk=survey_id)),
                       'sondages/base.html', _('Do you really want to delete this survey?'))
@login_required
def delete(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    survey.delete()
    request.user.message_set.create(message=_('Survey successfully deleted.'))
    return HttpResponseRedirect('/sondages/')

@login_required
def choice_add(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    return _form(request, survey, ChoiceForm, None,
                 _('Choice creation'), _('Choice succesfully added'))

@login_required
def choice_edit(request, survey_id, choice_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    choice = get_object_or_404(Choice, pk=choice_id)
    return _form(request, survey, ChoiceForm, choice,
                 _('Choice edition'), _('Choice succesfully updated.'))

@confirmation_required(lambda survey_id, choice_id: str(get_object_or_404(Choice, pk=choice_id)),'sondages/base.html', _('Do you really want to delete the choice'))
@login_required
def choice_delete(request, survey_id, choice_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    choice = get_object_or_404(Choice, pk=choice_id)
    choice.delete()
    request.user.message_set.create(message=_('Choice successfully deleted.'))
    return HttpResponseRedirect('/sondages/%s/details/' % survey.id)


def _form(request, survey, Form, instance, title, message):
    form = Form()
    if instance:
        form = Form(instance=instance)

    if request.method == 'POST':
        form = Form(request.POST.copy())
        if instance:
            form = Form(request.POST.copy(), instance=instance)
        if form.is_valid():
            if survey is not None:
                form.cleaned_data['survey'] = survey
                form.save()
            else:
                survey = form.save()
                contrib_type = UserContributionType.objects.get(key='poll_register')
                contrib = UserContribution(user=request.user.person, type=contrib_type)
                contrib.save()
            request.user.message_set.create(message=message)
            return HttpResponseRedirect('/sondages/%s/details/' % survey.id)
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))

    return ain7_render_to_response(request, 'sondages/form.html',
                              {'form': form, 'title': title})

