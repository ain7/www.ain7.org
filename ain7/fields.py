# -*- coding: utf-8 -*-
#
# fields.py
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

#
# http://www.djangosnippets.org/snippets/493/
#
from django.conf import settings
from django.db import models

class LanguageField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('maxlength', 5)
        kwargs.setdefault('choices', settings.LANGUAGES)

        super(LanguageField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"


#
# http://www.djangosnippets.org/snippets/253/
#

from django.forms.widgets import TextInput,flatatt
from django.forms.util import smart_unicode
from django.utils.translation import ugettext as _
from django.utils.html import escape
from ain7.ajax.views import ajaxed_strings, ajax_get_elements, ajax_request, ajax_field_value
from django.core.urlresolvers import reverse

class AutoCompleteField(TextInput):

    def __init__(self, completed_obj_name='', options='{ paramName: "text", autoSelect:true, afterUpdateElement:setSelected }', addable=False, attrs=None):
        self.completed_obj_name = completed_obj_name
        self.addable = addable
        self.options = options
        if attrs is None:
            attrs = {}
        self.attrs = attrs

    def render(self, name, value=None, attrs=None):
        final_attrs = self.attrs
        valueTxt = ''
        addlink = ''
        url = reverse(ajax_request, args=(self.completed_obj_name,name))
        if self.addable:
            addlink =  '<script type="text/javascript">'
            addlink += 'window.addEvent(\'domready\', function() {'
            addlink += 'window.floatingPane = new FloatingPane({title: "Adding", height: 400, width: 600, opacity: 0.75, draggable: true});'
            addlink += '});'
	    addlink += '</script>'
            addlink += '<a href="javascript:floatingPane.show(\'/manage/nationality/add/\',\'Add a new nationality\');" class="addlink">'+_('Add')+'</a>'

        # si une valeur a été saisie, je remplis le champ
        # avec la description de l'objet
        if value != "-1" and value != None and value != '':
            valueTxt = ajax_field_value(self.completed_obj_name, value)
            if self.completed_obj_name in ajaxed_strings():
                valueTxt = value
        if value:
            value = smart_unicode(value)
        else:
            value = "-1"
        return (u'<input type="hidden" name="%(name)s" value="%(value)s" id="%(id)s" />'
                  '<input type="text" name="%(name)s_text" id="%(id)s_text" size="40" autocomplete="off" value="%(valueTxt)s" %(attrs)s/>'+addlink+'<div class="complete" id="box_%(name)s"></div>'
                  '<script type="text/javascript">'
                  'window.myAutoComplete = new AutoComplete($(\'%(id)s_text\'), window.location.protocol+"//"+window.location.host+"%(url)s", "displayValue", {maxHeight: 350, zIndex: 6, method: \'post\'}, $(\'%(id)s\'));'
                  'myAutoComplete.addEvent(\'onItemChoose\', function(item) {'
                  '	document.getElementById(\'%(id)s\').value = item.getProperty(\'id\');'
		  '});'
                  'window.floatingPane = new FloatingPane({title: "floating pane", height: 400, width: 600, opacity: 0.75, draggable: true});'
                  'floatingPane.addEvent(\'onFloatingPaneClose\', function(event) {'
                  '	event.stop();'
                  '	myAutoComplete.canClose = true;'
                  '});'
                  'function showContactDetails(url, title) {'
                  'myAutoComplete.canClose = false;'
                  'floatingPane.show(url, title);'
                  '}'
                  '</script>') % {'attrs'	: flatatt(final_attrs),
                                  'name'	: name,
                                  'id'	: 'id_%s' % name,
                                  'url'	: url,
                                  'value': value,
                                  'valueTxt': valueTxt,
                                  'options' : self.options}

    def valuefromid(self):
        pass

    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, returns the value
        of this widget. Returns None if it's not provided.
        """
        val = data.get(name, None)
        if val=="-1":
            val = None

        value_text = data.get(name + "_text", None)
        if val == None and value_text:
            # used didn't selected something with autocomplet field
            # but he/she typed something... check if he/she typed something
            # which is unique (eg: "2003" was type for a year... the unique
            #  answer is the year 2003 :) )

            # But for ajaxed_strings... we simple use what used entered
            if self.completed_obj_name in ajaxed_strings():
                val = value_text
            else:
                # get the search method
                result = ajax_get_elements(self.completed_obj_name, value_text)
                if len(result) == 1:
                    # yes! got one and only one answer. Use it
                    val = result[0]['id']

        return val

