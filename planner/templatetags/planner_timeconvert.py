from django import template

register = template.Library()


@register.filter
def sec_to_hour_min_trunc(value, arg):
    """
    Converts a time in seconds to hours and minutes depending on arg. Should be called twice on the value with the different arg parameters for hour and minute, since the minute call will only print the remainder after hours are removed, not total minutes.

    arg options:
    "hour" --> provides rounded-down value in hours, int
    "min" --> provides rounded-down value in minutes after hours removed, int
    """
    hour = int(value / 3600)
    if arg == "hour":
        return hour
    elif arg == "min":
        return int((value - hour * 3600) / 60)
    else:  # if invalid arg, just return the input
        return value
