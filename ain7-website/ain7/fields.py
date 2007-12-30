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

from django.newforms.widgets import TextInput,flatatt
from django.newforms.util import smart_unicode

from django.utils.html import escape

class AutoCompleteField(TextInput):
    def __init__(self, url='', options='{ paramName: "text", autoSelect:true, afterUpdateElement:setSelected }', attrs=None):
        self.url = url
        self.options = options
        if attrs is None:
            attrs = {}
        self.attrs = attrs

    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        if value:
            value = smart_unicode(value)
            final_attrs['value'] = escape(value)
        if not self.attrs.has_key('id'):
            final_attrs['id'] = 'id_%s' % name
        return (u'<input type="hidden" name="%(name)s" value="-1" id="%(id)s" />'
                  '<input type="text" name="%(name)s_text" id="%(id)s_text" size="50" /> <div class="complete" id="box_%(name)s"></div>'
                        '<script type="text/javascript">'
                        'function setSelected(text, li) {'
                        '    $(\'%(id)s\').value = li.id;'
                        '}'
                        ' new Ajax.Autocompleter(\'%(id)s_text\', \'box_%(name)s\', \'%(url)s\', %(options)s);'
                        '</script>') % {'attrs'	: flatatt(final_attrs),
                                        'name'	: name,
                                        'id'	: final_attrs['id'],
                                        'url'	: self.url,
                                        'options' : self.options}

