"""This module provides functions for simple common conversions"""


def min_to_sec(minutes):
    """
    Converts minutes to seconds.

    INPUT:
    duration in minutes [int or float]

    OUTPUT:
    duration in seconds [int or float]
    """
    return minutes * 60


def m_to_miles(meters):
    """
    Converts meters to miles.

    INPUT:
    distance in meters [int or float]

    OUTPUT:
    distance in miles [float]
    """
    return meters / 1609.34

def miles_to_m(miles):
    """
    Converts miles to meters.

    INPUT:
    distance in miles [int or float]
    OUTPUT:
    distance in meters [float]
    """
    return miles * 1609.34
