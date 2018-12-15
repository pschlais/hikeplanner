# Single functions for quickly accessing and parsing data from external APIs
from . import constructURL, accessAPI, parseAPI

def sunTimeData(lat, lon, date=None):
    """
    Access sunrise, sunset, first light, last light, and day length for
    a given lat/lon. Accesses both the sunrise/sunset API and Google Time Zone
    API.

    INPUTS:
    lat: latitude (float)
    lon: longitude (float)
    date: retrieve data for this date (datetime.datetime object)
    """

    # access sunrise/sunset API
    sunDataURL = constructURL.sunriseSunsetAPI(lat, lon, date)
    sunAPIdata_raw = accessAPI.sunriseSunset_API(sunDataURL)
    sunAPIdata = parseAPI.sunrise_sunset_properties(sunAPIdata_raw)

    # access time zone API
    tzURL = constructURL.googleTimeZoneAPI(lat, lon, date)
    tzAPIdata_raw = accessAPI.googleTimeZoneAPI(tzURL)
    tzAPIdata = parseAPI.googleTimeZoneProperties(tzAPIdata_raw)

    # combine data from both sources
    if sunAPIdata["status"] == "OK" and tzAPIdata["status"] == "OK":
        # the base return values are the same as sunAPIdata
        returnObj = sunAPIdata

        # adjust the times based on UTC and DST time zone data
        adj_list = ["sunrise", "sunset", "first_light", "last_light"]

        for key in adj_list:
            returnObj[key] += (tzAPIdata["dstOffset"] + tzAPIdata["utcOffset"])

        # add time zone string to object
        returnObj ["timezone"] = tzAPIdata["timezone"]
        # return data
        return returnObj

    else:  # return error for the first API that provides a non-OK status code
        if sunAPIdata["status"] != "OK":
            # Sunrise-Sunset API
            return sunAPIdata
        else:  # Time Zone API
            return tzAPIdata
