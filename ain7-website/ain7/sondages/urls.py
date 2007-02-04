from django.conf.urls.defaults import *

urlpatterns = patterns('',

    # Sondage
    (r'^$', 'ain7.sondages.views.index'),
    (r'^(?P<sondage_id>\d+)/vote/$', 'ain7.sondages.views.vote'),
    (r'^(?P<sondage_id>\d+)/resultats/$', 'ain7.sondages.views.resultats'),

)
