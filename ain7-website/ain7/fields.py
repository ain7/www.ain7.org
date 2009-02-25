# -*- coding: utf-8 -*-

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
from ain7.ajax.views import ajaxed_fields, ajaxed_strings

class AutoCompleteField(TextInput):

    # ce dictionnaire me semble inutilisé
#     entities = { 
#                  'nationality': { 'url': '/ajax/nationality/', 'add_url': '/manage/nationality/add', 'add_title': _('Add a new nationality') },
#                  'office': { 'url': '/ajax/office/', 'add_url': '/manage/office/add', 'add_title': _('Add a new office') },
#                  'person': { 'url': '/ajax/person/' },
#                  'promoyear': { 'url': '/ajax/promoyear/' },
#                  'track': { 'url': '/ajax/track/' },
#                  'organization': { 'url': '/ajax/organization/' },
#                  'activityfield': { 'url': '/ajax/activityfield/' },
#                  'activitycode': { 'url': '/ajax/activitycode/' },
#                  'permission': { 'url': '/ajax/permission/' },
#                }

    def __init__(self, url='', options='{ paramName: "text", autoSelect:true, afterUpdateElement:setSelected }', addable=False, attrs=None):
        self.url = url
        self.addable = addable
        self.options = options
        if attrs is None:
            attrs = {}
        self.attrs = attrs

    def render(self, name, value=None, attrs=None):
        final_attrs = self.attrs
        valueTxt = ''
        addlink = ''
        if self.addable:
            addlink =  '<script type="text/javascript">'
            addlink += 'window.addEvent(\'domready\', function() {'
            addlink += 'window.floatingPane = new FloatingPane({title: "Adding", height: 400, width: 600, opacity: 0.75, draggable: true});'
            addlink += '});'
	    addlink += '</script>'
            addlink += '<a href="javascript:floatingPane.show(\'/manage/nationality/add/\',\'Add a new nationality\');" class="addlink">'+_('Add')+'</a>'

        # si une valeur a été saisie, je remplis le champ
        # avec la description de l'objet
        if value != "-1" and value != None:
            for objClass, objName in ajaxed_fields().iteritems():
                if objName == name:
                    obj = objClass.objects.get(pk=value)
                    valueTxt = obj.autocomplete_str()
            if name in ajaxed_strings():
                valueTxt = value
        if value:
            value = smart_unicode(value)
        else:
            value = "-1"
        return (u'<input type="hidden" name="%(name)s" value="%(value)s" id="%(id)s" />'
                  '<input type="text" name="text" id="%(id)s_text" size="40" autocomplete="off" value="%(valueTxt)s" %(attrs)s/>'+addlink+'<div class="complete" id="box_%(name)s"></div>'
                  '<script type="text/javascript">'
                  'window.myAutoComplete = new AutoComplete($(\'%(id)s_text\'), window.location.protocol+"//"+window.location.host+"%(url)s", "displayValue", {maxHeight: 350, zIndex: 6, method: \'post\'});'
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
                                  'url'	: self.url,
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
        return val

