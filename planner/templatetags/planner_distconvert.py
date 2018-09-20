from django import template

register = template.Library()


@register.filter
def m_to_miles(value):
    """
    Converts a value in meters to miles. Takes float or int and returns a float.
    """
    return value / 1609.34
