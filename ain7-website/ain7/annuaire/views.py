from django.shortcuts import get_object_or_404, render_to_response
from ain7.annuaire.models import Personne

def index(request):
    liste_personnes = Personne.objects.all().order_by('nom')[:5]
    return render_to_response('annuaire/index.html', {'liste_personnes': liste_personnes})

def detail(request, personne_id):
    p = get_object_or_404(Personne, pk=personne_id)
    return render_to_response('annuaire/detail.html', {'personne': p})

