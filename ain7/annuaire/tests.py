# -*- coding: utf-8
"""
 ain7/annuaire/tests.py
"""
#
#   Copyright © 2007-2011 AIn7 Devel Team
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

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from ain7.ajax.views import ajax_resolve


class AjaxResolveTestCase(TestCase):
    """
    Tests relative to ajax (which is not an app, so these
    tests are put here)
    """
    
    def test_mapping(self):
        """Tests whether all fields listed in ajax_resolve exist in models."""
        for model, pairs in ajax_resolve().iteritems():
            if model.objects.count() > 0:
                model_inst = model.objects.all()[0]
                for field_name, completed_name in pairs:
                    getattr(model_inst, field_name)
                
                
    def test_url_uniqueness(self):
        """Tests the uniqueness of Ajax URLs."""
        urls = []
        for model, pairs in ajax_resolve().iteritems():
            for field_name, completed_name in pairs:
                assert( completed_name not in urls )
                urls.append( completed_name )

