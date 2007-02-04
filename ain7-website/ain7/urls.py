from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^ain7/', include('ain7.apps.foo.urls.foo')),

    # servir le contenu statique pendant le dev
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/lionel/dev/ain7/ain7-website/ain7/media'}),

    # Uncomment this for admin:
     (r'^admin/', include('django.contrib.admin.urls')),

    # annuaire
    (r'^annuaire/', include('ain7.annuaire.urls')),

    # sondage
    (r'^sondages/', include('ain7.sondages.urls')),

    # Pages particulieres au contenu pseudo statique
    (r'^contact/','ain7.pages.views.contact'),
    (r'^apropos/','ain7.pages.views.apropos'),
    (r'^$','ain7.pages.views.homepage'),

)
