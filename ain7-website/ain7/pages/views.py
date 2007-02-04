from django.shortcuts import render_to_response
from ain7.news.models import Actualite
from ain7.sondages.models import Sondage

def homepage(request):
    liste_actualites = Actualite.objects.all().order_by('titre')[:5]
    liste_sondages = Sondage.objects.all()[:2]
    return render_to_response('pages/index.html', {'liste_actualites': liste_actualites , 'liste_sondages': liste_sondages })

def apropos(request):
    return render_to_response('pages/apropos.html')

def contact(request):
    return render_to_response('pages/contact.html')

