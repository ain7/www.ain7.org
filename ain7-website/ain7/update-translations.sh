#!/bin/sh

./manage.py makemessages -l fr
./manage.py makemessages -l en

./manage.py compilemessages
