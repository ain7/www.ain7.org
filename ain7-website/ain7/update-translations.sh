#!/bin/sh

python /usr/share/python-support/python-django/django/bin/make-messages.py -l fr
python /usr/share/python-support/python-django/django/bin/make-messages.py -l en

python /usr/share/python-support/python-django/django/bin/compile-messages.py
