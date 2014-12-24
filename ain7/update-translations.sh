#!/bin/sh

PYTHONPATH=.. django-admin makemessages --settings=ain7.settings --locale=en --locale=fr

PYTHONPATH=.. django-admin compilemessages --settings=ain7.settings

