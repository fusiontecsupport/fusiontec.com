from django import template

register = template.Library()

@register.filter
def get_attribute(obj, attr):
    """
    Template filter to get an attribute of an object dynamically.
    Usage: {{ object|get_attribute:"attribute_name" }}
    """
    try:
        return getattr(obj, attr)
    except (AttributeError, TypeError):
        return "" 