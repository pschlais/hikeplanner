"""This module provides utility functions to parse API outputs."""
from . import date_utils
import calendar


def unpackDriveProperties(apiObj, origin_index=0, destination_index=0):
    """
    Returns a simplified object with the drive properties to display for the given origin/destination combo, specified by index numbers in the upstream URL request
    """

    returnDict = {
        "APIStatus": apiObj["status"],
        "APIMessage": "",
        "dataStatus": "",
        "dataMessage": "",
        "duration": {
            "value": None,
            "text": "Not Available",
        },
        "distance": {
            "value": None,
            "text": "Not Available",
        },
    }

    if apiObj["status"] == "OK":
        # unpack data
        drive_data = apiObj["rows"][origin_index]["elements"][destination_index]
        returnDict["dataStatus"] = drive_data["status"]

        if drive_data["status"] == "OK":
            returnDict["duration"] = drive_data["duration"]
            returnDict["distance"] = drive_data["distance"]

        elif drive_data["status"] == "NOT_FOUND":
            returnDict["dataMessage"] = drive_data.get("message",
                    "Distance Matrix API could not geocode origin " +
                    "and/or destination.")

        elif drive_data["status"] == "ZERO_RESULTS":
            returnDict["dataMessage"] = drive_data.get("message",
                    "Distance Matrix API could not find a route between " +
                    "origin and destination.")

        elif drive_data["status"] == "MAX_ROUTE_LENGTH_EXCEEDED":
            returnDict["dataMessage"] = drive_data.get("message",
                    "Max route length limit of Distance Matrix API exceeded," +
                    " cannot be processed.")

        else:
            returnDict["dataMessage"] = ("Unhandled Distance Matrix API " +
                     "route error encountered.")

    elif apiObj["status"] == "URL_ERROR":
        returnDict["APIMessage"] = apiObj.get("message",
                    "HTTP error accessing Google Distance API.")

    elif apiObj["status"] == "SSL_ERROR":
        returnDict["APIMessage"] = apiObj.get("message",
                    "SSL error accessing Google Distance API.")

    elif apiObj["status"] == "INVALID_REQUEST":
        returnDict["APIMessage"] = apiObj.get("message",
                    "Distance Matrix API request is invalid.")

    elif apiObj["status"] == "MAX_ELEMENTS_EXCEEDED":
        returnDict["APIMessage"] = apiObj.get("message",
                    "Distance Matrix API request has too many query entries.")

    elif apiObj["status"] == "OVER_DAILY_LIMIT":
        returnDict["APIMessage"] = apiObj.get("message",
                    "Over Distance Matrix API query daily limit.")

    elif apiObj["status"] == "REQUEST_DENIED":
        returnDict["APIMessage"] = apiObj.get("message",
                    "Service denied from Distance Matrix API for this " +
                    "application.")

    elif apiObj["status"] == "UNKNOWN_ERROR":
        returnDict["APIMessage"] = apiObj.get("message",
                    "Unknown Distance Matrix API server error.")

    else:
        returnDict["APIMessage"] = "No data processed, unhandled API status."

    return returnDict


def NOAA_by_day(NOAAdict):
    """
    Takes the accessAPI.NOAA_API() output and organizes the
    period data by calendar days, returned in array format. Each
    array entry is a dictionary with data about the day, and all
    weather period data that pertains to that day.
    """
    return_array = []

    if NOAAdict["status"] != "OK":
        # fail gracefully, return empty array
        pass
    else:
        # unpack NOAA dict for period data
        period_data = NOAAdict["properties"]["periods"]

        i = 0  # keep track of length of array
        i_day = -1  # day (integer) corresponding last element of return array

        # for each period with data
        for period in period_data:
            # check which day of the week it falls in
            period_datetime = date_utils.ISO_to_datetime(period["startTime"])

            # if the day of the period isn't in the array already, add the day
            if period_datetime.day != i_day:
                # initialize dict corresponding to day
                if i == 0:
                    day_name = "Today"
                elif i == 1:
                    day_name = "Tomorrow"
                else:
                    day_name = calendar.day_name[period_datetime.weekday()]

                day_dict = {
                    'dayOfWeek': day_name,
                    'month': period_datetime.month,
                    'day': period_datetime.day,
                    'periodData': [],
                }

                # append initialized dictionary to array
                return_array.append(day_dict)

                # reset day flag for current day
                i += 1
                i_day = period_datetime.day

            # add period to the current day (last index in array)
            return_array[-1]['periodData'].append(period)

    # return data
    return return_array
