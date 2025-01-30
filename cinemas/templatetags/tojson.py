import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def tojson(value):
    """Convert a Python object into a JSON string."""
    return mark_safe(json.dumps(value))
