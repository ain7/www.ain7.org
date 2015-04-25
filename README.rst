The AIn7 portal code
=====================

Overview of contents and licensing:

ain7/
 - Application maison Django du portail AIn7, GNU GPL v2
apache/
 - Configuration apache utilisée pour le domaine ain7.com
forum/
 - Thème Fluxbb pour l'AIn7
galerie/
 - Thème Gallery2 pour l'AIn7
media/
 - Contenu statique (css, images)
scripts/
 - Scripts utilises par les differents applications
wiki/
 - Theme Wiki moinmoin pour l'AIn7
 
 Portail AIn7
=====================

Pour installer le portail AIn7 en version de développement, il faut :
- installer les packages Debian/Ubuntu: 
  sudo apt-get install python-django python-pysqlite2 python-imaging python-vobject python-pexpect python-pygments
- récupérer les sources du portail (a priori si vous lisez ce fichier, c'est
  déjà fait. Sinon: bzr co bzr+ssh://<name>@bazaar.launchpad.net/~ain7-devel/ain7-portal/ain7-portal.dev
  ou <name> est votre identifiant launchpad.
- éditer le fichier ain7-website/ain7/settings_local.py pour adapter la configuration
- créer la base de donnée initiale (elle n'est pas comprise dans l'archive bzr):
  aller dans le répertoire ain7-website/ain7 et puis taper :
  python build_database.py
- lancer le serveur : python manage.py runserver
- vous pouvez accéder à l'application à l'URL : http://localhost:8000
- l'interface d'administration est accessible à http://localhost:8000/admin
