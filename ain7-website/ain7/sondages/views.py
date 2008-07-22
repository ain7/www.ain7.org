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
from django import forms
from django.utils.translation import ugettext as _

from ain7.annuaire.models import UserContributionType, UserContribution
from ain7.sondages.models import Choice, Survey, Vote
from ain7.sondages.forms import *
from ain7.decorators import confirmation_required
from ain7.utils import ain7_render_to_response, ain7_generic_edit, ain7_generic_delete

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
    return ain7_generic_edit(
        request, None, SurveyForm, {}, 'sondages/form.html',
        {'title': _('Survey creation')}, {}, '/sondages/$objid/details/',
        _('Survey succesfully created.'))

@login_required
def details(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    return ain7_render_to_response(request, 'sondages/details.html',
                            {'survey': survey})

@login_required
def edit(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    return ain7_generic_edit(
        request, survey, SurveyForm, {}, 'sondages/form.html',
        {'title': _('Survey edition')},  {},
        '/sondages/%s/details/' % survey_id, _('Survey succesfully updated.'))

@confirmation_required(lambda survey_id: str(get_object_or_404(Survey, pk=survey_id)),
                       'sondages/base.html', _('Do you really want to delete this survey?'))
@login_required
def delete(request, survey_id):
    return ain7_generic_delete(request,
        get_object_or_404(Survey, pk=survey_id), '/sondages/',
        _('Survey successfully deleted.'))

@login_required
def choice_add(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    return ain7_generic_edit(
        request, None, ChoiceForm, {'survey': survey}, 'sondages/form.html',
        {'title': _('Choice creation')}, {},
        '/sondages/%s/details/' % survey_id, _('Choice succesfully added'))

@login_required
def choice_edit(request, survey_id, choice_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    choice = get_object_or_404(Choice, pk=choice_id)
    return ain7_generic_edit(
        request, choice, ChoiceForm, {'survey': survey}, 'sondages/form.html',
        {'title': _('Choice edition')}, {},
        '/sondages/%s/details/' % survey_id, _('Choice succesfully updated.'))

@confirmation_required(lambda survey_id, choice_id: str(get_object_or_404(Choice, pk=choice_id)),'sondages/base.html', _('Do you really want to delete the choice'))
@login_required
def choice_delete(request, survey_id, choice_id):
    return ain7_generic_delete(request,
        get_object_or_404(Choice, pk=choice_id),
        '/sondages/%s/details/' % survey_id, _('Choice successfully deleted.'))

