"""This module provides utilities for datetime operations"""
from datetime import datetime

def ISO_to_datetime(iso_str, keep_UTC=False):
    """
    Takes ISO 8601 string and transforms it into datetime object.

    INPUT:
        iso_str: string, ISO 8601 format (e.g. 2002-12-25T05:42:16-05:00)
        keep_UTC: bool, keeps & converts UTC offset if True, ignores if False
    OUTPUT:
        dt: datetime.datetime() object
    """

    iso_format = "%Y-%m-%dT%H:%M:%S%z"

    if not keep_UTC:
        #find "T", then strip all values after HH:MM:SS
        i_T = iso_str.find("T")
        iso_str = iso_str[:i_T+len("HH:MM:SS")+1]
        iso_format = "%Y-%m-%dT%H:%M:%S"
    else:
        # THIS DOES NOT WORK WITH NOAA API DATA CURRENTLY
        iso_format = "%Y-%m-%dT%H:%M:%S%z"

    return datetime.strptime(iso_str, iso_format)
