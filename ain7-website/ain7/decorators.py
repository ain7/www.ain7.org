# -*- coding: utf-8
#
# decorators.py
#
#   Copyright (C) 2007 AIn7
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

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django import newforms as forms

def confirmation_required(get_description, section='base.html', message=_('Are you sure you want to do this action?')):
    """
    Decorator for views that need confirmation.
    """

    def _dec(view_func):
        def _checkconfirm(request, *args, **kwargs):
            if request.method != 'POST':
                description = get_description(*args, **kwargs)
                back = request.META.get('HTTP_REFERER', '/');
                return render_to_response('pages/confirm.html',
                                          {'description': description, 'section': section,
                                           'message': message, 'back': back},
                                          context_instance=RequestContext(request))
            else:
                # Go to the decorated view
                return view_func(request, *args, **kwargs)
        _checkconfirm.__doc__ = view_func.__doc__
        _checkconfirm.__dict__ = view_func.__dict__

        return _checkconfirm
    return _dec

