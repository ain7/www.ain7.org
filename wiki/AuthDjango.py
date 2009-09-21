# -*- coding: utf-8
#
# AuthDjango.py
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

def AuthDjango(request, **kw):
    """ authenticate to Django db
    © 2007-2009 Lionel Porcheron <lionel@alveonet.org>
    """
    username = kw.get('name')
    password = kw.get('password')
    login = kw.get('login')
    user_obj = kw.get('user_obj')
    cfg = request.cfg
    verbose = cfg.auth_django_verbose
    if verbose:
        request.log("auth_django: got name=%s login=%r" % (username, login))
    # we just intercept login, other requests have to be
    # handled by another auth handler
    if not login:
        return user_obj, True
    import sys
    import traceback
    from MoinMoin import user
    from django.contrib.auth.models import User
    from django.contrib import auth

    u = None
    try:

         django_user = auth.authenticate(username=username, password=password)

         u = user.User(request,
                       auth_username=username,
                       name=username,
                       password=password,
                       auth_method='auth_django',
                       auth_attribs=('name', 'auth_username', 'password',))

         django_user.last_login = datetime.datetime.now()
         django_user.save()

    except:
        info = sys.exc_info()
        request.log("auth_django: caught an exception, traceback follows...")
        request.log(''.join(traceback.format_exception(*info)))
    if u:
        u.create_or_update(True)
    return u, True

