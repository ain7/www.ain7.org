# -*- coding: utf-8
#
# media_communications/views.py
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
    text = Text.objects.get(pk=10)
    return ain7_render_to_response(request, 
            'media_communication/index.html', {'text': text})

def canal_n7(request):
    text1 = Text.objects.get(pk=11)
    text2 = Text.objects.get(pk=12)
    text3 = Text.objects.get(pk=13)
    text4 = Text.objects.get(pk=14)
    return ain7_render_to_response(request, 'media_communication/canal_n7.html',
                  {'text1': text1, 'text2': text2, 'text3': text3, 'text4': text4})

def canal_n7_edito(request): 
    text1 = Text.objects.get(pk=15)
    text2 = Text.objects.get(pk=14)
    return ain7_render_to_response(request, 
                      'media_communication/canal_n7_edito.html', 
                     {'text1': text1, 'text2': text2})

def website(request): 
    text = Text.objects.get(pk=16)
    return ain7_render_to_response(request, 
                 'media_communication/website.html', {'text': text})

