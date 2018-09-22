from django import template
import math

register = template.Library()


@register.filter
def m_to_miles(value):
    """
    Converts a value in meters to miles. Takes float or int and returns a float.
    """
    return value / 1609.34


@register.filter
def dist_roundup(value):
    """
    Rounds the distance up to the next integer value.
    """
    return math.ceil(value)
