import dateutil.parser
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter("dot")
@stringfilter
def dot(value):
    """Removes all values of arg from the given string"""
    return dateutil.parser.parse(value).strftime("%b %d, %Y")
