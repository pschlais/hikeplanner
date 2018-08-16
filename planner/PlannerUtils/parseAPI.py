"""This module provides utility functions to parse API outputs."""
from . import date_utils
import calendar


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
