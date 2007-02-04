from django.shortcuts import render_to_response
from ain7.annuaire.models import Actualite

def index(request):
    liste_actus = Actualite.objects.all().order_by('titre')[:5]
    return render_to_response('page/index.html', {'liste_actus': liste_actus })

