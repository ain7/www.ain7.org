# -*- coding: utf-8
#
# media_communications/views.py
#
#   Copyright (C) 2007-2008 AIn7
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

from ain7.utils import ain7_render_to_response

def index(request): 
    return ain7_render_to_response(request, 'media_communication/index.html', {})

def canal_n7(request): 
    return ain7_render_to_response(request, 'media_communication/canal_n7.html', {})

def canal_n7_edito(request): 
    return ain7_render_to_response(request, 'media_communication/canal_n7_edito.html', {})

def website(request): 
    return ain7_render_to_response(request, 'media_communication/website.html', {})

