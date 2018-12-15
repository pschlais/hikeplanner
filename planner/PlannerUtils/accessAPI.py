""" This module provides access to external web APIs """
import requests
from requests.exceptions import HTTPError, SSLError


def googleMapsDistanceAPI(requestURL):
    """
    Sends API request to Google Directions Matrix API and returns json results
    in python object format
    """

    # make sure the URL call does not throw an error
    try:
        apiCall = requests.get(requestURL)
    except HTTPError:
        # i.e. CERTIFICATE_VERIFY_FAILED error
        # Create dictionary for view to parse wtih error information
        apiObj = {}
        apiObj["status"] = "HTTP_ERROR"
        apiObj["message"] = "HTTP error accessing Google Distance Matrix API."

        response = apiObj
    except SSLError:
        # i.e. CERTIFICATE_VERIFY_FAILED error
        # Create dictionary for view to parse wtih error information
        apiObj = {}
        apiObj["status"] = "SSL_ERROR"
        apiObj["message"] = "SSL error accessing Google Distance Matrix API."

        response = apiObj
    else:
        response = apiCall.json()

    return response


def googleTimeZoneAPI(requestURL):
    """
    Sends API request to Google Time Zone API and returns json results
    in python object format
    """

    # make sure the URL call does not throw an error
    try:
        apiCall = requests.get(requestURL)
    except HTTPError:
        # i.e. CERTIFICATE_VERIFY_FAILED error
        # Create dictionary for view to parse wtih error information
        apiObj = {}
        apiObj["status"] = "HTTP_ERROR"
        apiObj["message"] = "HTTP error accessing Google Time Zone API."

        response = apiObj
    except SSLError:
        # i.e. CERTIFICATE_VERIFY_FAILED error
        # Create dictionary for view to parse wtih error information
        apiObj = {}
        apiObj["status"] = "SSL_ERROR"
        apiObj["message"] = "SSL error accessing Google Time Zone API."

        response = apiObj
    else:
        response = apiCall.json()

    return response


def NOAA_API(requestURL):
    """
    Sends API request to NOAA forecast API and returns json results
    in python object format
    """

    # make sure the URL call does not throw an error
    try:
        apiCall = requests.get(requestURL)

    except HTTPError:
        # i.e. CERTIFICATE_VERIFY_FAILED error
        # Create dictionary for view to parse wtih error information
        apiObj = {}
        apiObj["status"] = "HTTP_ERROR"
        apiObj["message"] = "HTTP error accessing NOAA forecast API."

    else:
        apiObj = apiCall.json()
        apiObj["status"] = "OK"
        apiObj["message"] = ""

    return apiObj


def sunriseSunset_API(requestURL):
    """
    Sends API request to sunrise-sunset API and returns json results
    in python object format
    """

    # make sure the URL call does not throw an error
    try:
        apiCall = requests.get(requestURL)

    except HTTPError:
        # i.e. CERTIFICATE_VERIFY_FAILED error
        # Create dictionary for view to parse wtih error information
        apiObj = {}
        apiObj["status"] = "HTTP_ERROR"
        apiObj["message"] = "HTTP error accessing sunrise/sunset API."

        response = apiObj

    else:
        apiObj = apiCall.json()
        # apiObj returns with "status" and "results" properties
        api_status = apiObj.get("status")

        if api_status == "OK":
            # do nothing, return full object
            apiObj["message"] = ""
        else:
            # other statuses are "INVALID_REQUEST", "INVALID_DATE", and
            # "UNKNOWN ERROR"
            apiObj["message"] = "Sunrise/sunset times unavailable."

        return apiObj
