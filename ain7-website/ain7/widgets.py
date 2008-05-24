# -*- coding: utf-8 -*-
#
#
# Widget from http://www.djangosnippets.org/snippets/391/
# widgets.py
#
# To use you have to put calendar/ (from http://www.dynarch.com/projects/calendar/)
# to your MEDIA folder and then include such links on your page:
# <!-- calendar -->
# <link rel="stylesheet" type="text/css" href="{{ MEDIA_URL }}calendar/calendar-win2k-cold-2.css" />
#<script type="text/javascript" src="{{ MEDIA_URL }}calendar/calendar.js"></script>
# <!-- this is translation file - choose your language here -->
#<script type="text/javascript" src="{{ MEDIA_URL }}calendar/lang/calendar-pl.js"></script>
#<script type="text/javascript" src="{{ MEDIA_URL }}calendar/calendar-setup.js"></script>
#<!-- /calendar -->

#from django.utils.encoding import force_unicode
from django.conf import settings
from django import newforms as forms
from datetime import datetime, date
from time import strptime

# DATETIMEWIDGET
calbtn = u"""<img src="%simages/calbutton.gif" alt="calendar" id="%s_btn" style="cursor: pointer; border: 1px solid #8888aa;" title="Select date and time"
            onmouseover="this.style.background='#444444';" onmouseout="this.style.background=''" />
<script type="text/javascript">
    Calendar.setup({
        inputField     :    "%s",
        ifFormat       :    "%s",
        button         :    "%s_btn",
        singleClick    :    true,
        showsTime      :    true
    });
</script>"""

class DateTimeWidget(forms.widgets.TextInput):
    dformat = '%d/%m/%Y %H:%M'
    def render(self, name, value, attrs=None):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '': 
            try:
                final_attrs['value'] = \
                                   value.strftime(self.dformat)
            except:
                final_attrs['value'] = \
                                   value
        if not final_attrs.has_key('id'):
            final_attrs['id'] = u'%s_id' % (name)
        id = final_attrs['id']
        
        jsdformat = self.dformat #.replace('%', '%%')
        cal = calbtn % (settings.MEDIA_URL, id, id, jsdformat, id)
        a = u'<input%s />%s' % (forms.util.flatatt(final_attrs), cal)
        return a

    def value_from_datadict(self, data, files, name):
        dtf = forms.fields.DEFAULT_DATETIME_INPUT_FORMATS
        empty_values = forms.fields.EMPTY_VALUES

        value = data.get(name, None)
        # print "Value = %s " % value
        if value in empty_values:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime(value.year, value.month, value.day)
        try:
            return datetime(*strptime(value, self.dformat)[:6])
        except ValueError:
            pass
        for format in dtf:
            try:
                return datetime(*strptime(value, format)[:6])
            except ValueError:
                continue
        return None
