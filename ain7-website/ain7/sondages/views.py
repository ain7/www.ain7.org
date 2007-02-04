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

