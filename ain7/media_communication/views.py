# -*- coding: utf-8
"""
 ain7/media_communications/views.py
"""
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

from ain7.pages.models import Text
from ain7.utils import ain7_render_to_response


def index(request):
    """media communication index page"""
    text = Text.objects.get(textblock__shortname='publication_ain7')
    return ain7_render_to_response(request, 
            'media_communication/index.html', {'text': text})

def canal_n7(request):
    """Canal N7 page"""
    text1 = Text.objects.get(textblock__shortname='presentation_canal_n7')
    text2 = Text.objects.get(textblock__shortname='redaction_canal_n7')
    text3 = Text.objects.get(textblock__shortname='canal_n7')
    text4 = Text.objects.get(textblock__shortname='sommaire_canal_n7')
    return ain7_render_to_response(request, 'media_communication/canal_n7.html',
                  {'text1': text1, 'text2': text2, 'text3': text3, 'text4': text4})

def canal_n7_edito(request): 
    """Canal N7 edito"""
    text1 = Text.objects.get(textblock__shortname='edito_canal_n7')
    text2 = Text.objects.get(textblock__shortname='sommaire_canal_n7')
    return ain7_render_to_response(request, 
                      'media_communication/canal_n7_edito.html', 
                     {'text1': text1, 'text2': text2})

