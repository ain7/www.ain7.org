# -*- coding: utf-8
#
# views.py
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
from ain7.sondages.models import Choix, Sondage

def vote(request, sondage_id):
    sondage = get_object_or_404(Sondage, pk=sondage_id)
    try:
        selected_choice = sondage.choix_set.get(pk=request.POST['choix'])
    except (KeyError, Choix.DoesNotExist):
        # Redisplay the poll voting form.
        return render_to_response('sondages/detail.html', {
            'sondage': sondage,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect('/sondages/%s/resultats/' % sondage.id)

def resultats(request, sondage_id):
    sondage = get_object_or_404(Sondage, pk=sondage_id)
    return render_to_response('sondages/resultats.html', {'sondage': sondage})

