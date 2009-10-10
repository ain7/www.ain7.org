# -*- coding: utf-8
#
# middleware/portalexceptions.py
#
#   Copyright © 2007-2009 AIn7 Devel Team
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#

import datetime
import sys
import traceback

from django import http
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import MiddlewareNotUsed
from django.shortcuts import render_to_response

from ain7.manage.models import PortalError

class PortalException:
    """
        If you are not in debug, log every exception.
        Exception are logged in database
    """

    def __init__(self):
        if hasattr(settings,'DEBUG') and settings.DEBUG:
            raise MiddlewareNotUsed("MiddleWare only used in production mode")

    def process_exception(self, request, exception):

        if isinstance(exception, http.Http404):
            return # do nothing, let standard processing happen


        exc_info = sys.exc_info()

        e = PortalError()
        if request.user and request.user.is_authenticated():
            e.user = request.user
        e.date = datetime.datetime.now()
        e.url = request.path
        e.title = str(exception)
        e.referer = request.META['HTTP_REFERER']
        e.browser_info = request.META['HTTP_USER_AGENT']
        e.client_address = request.META['REMOTE_HOST']
        e.exception = str(traceback.format_exception(*exc_info))
        try:
            e.save()
        except Exception, ee:
            print ee

        return render_to_response('500.html', {'exception_code': e.pk})

