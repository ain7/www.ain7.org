from django.conf.urls.defaults import *


urlpatterns = patterns('',

    # Annuaire
    (r'^$', 'ain7.annuaire.views.index'),
    (r'^(?P<personne_id>\d+)/$', 'ain7.annuaire.views.detail'),

)
