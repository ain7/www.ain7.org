AIn7 Web Portal
===============

This project host the ENSEEIHT (n7) alumni group (AIn7) portal code:

- ENSEEIHT is a French engineering school: http://www.enseeiht.fr
- ENSEEIHT Almuni group: https://ain7.com

All the code has been released under GPLv2 license. Portal is maintained by volonteers of the alumni group.

Contributions (pull requests) and bugs are welcome.

For using the code, just clone this repository. We recommend to use a virtualenv::

 $ mkvirtualenv www.ain7.org
 $ pip install -r requirements-dev.txt
 $ python manage.py runserver

Then point your browser to http://localhost:8000
