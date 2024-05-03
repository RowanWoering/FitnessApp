from django import template

register = template.Library()

@register.simple_tag
def get_range(value):
    """Generates a range list from 0 to value."""
    return range(value)