from django import template 
from orders.constants import COUNTRY_DICT

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})



@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(key)
    except Exception as e:
        return None
    

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter
def country_name(code):
    return COUNTRY_DICT.get(code, code)