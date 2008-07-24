#!/bin/sh

django-admin.py makemessages -l fr
django-admin.py makemessages -l en

django-admin.py compilemessages
