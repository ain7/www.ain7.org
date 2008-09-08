from django import template
from ain7.utils import generic_show_last_change

register = template.Library()
@register.inclusion_tag('pages/last_change.html')
def show_last_change(obj):
    return generic_show_last_change(obj)
