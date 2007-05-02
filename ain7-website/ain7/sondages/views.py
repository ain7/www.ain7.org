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
from django.http import HttpResponseRedirect
from ain7.sondages.models import Choice, Survey

def vote(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    try:
        choice = survey.choices.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the poll voting form.
        return render_to_response('sondages/detail.html', {
            'survey': survey,
            'error_message': "Vous n'avez rien sélectionné.",
        })
    else:
        choice.votes += 1
        choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect('/sondages/%s/detail/%s' % (survey.id, choice.id))

def resultats(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    return render_to_response('sondages/resultats.html', {'survey': survey})

def detail(request, survey_id, choice_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    choice = get_object_or_404(Choice, pk=choice_id)
    return render_to_response('sondages/detail.html', {'survey': survey, 'choice': choice})

