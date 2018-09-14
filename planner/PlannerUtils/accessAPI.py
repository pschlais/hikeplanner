""" This module provides access to external web APIs """
import urllib.request
import requests
from urllib.error import URLError
import json


def googleMapsDistanceAPI(requestURL):
    """
    Sends API request to Google Directions Matrix API and returns json results
    in python object format
    """

    # make sure the URL call does not throw an error
    try:
        apiCall = urllib.request.urlopen(requestURL)
    except URLError:
        # i.e. CERTIFICATE_VERIFY_FAILED error
        # Create dictionary for view to parse wtih error information
        apiObj = {}
        apiObj["status"] = "URL_ERROR"
        apiObj["message"] = "HTTP error accessing Google Distance API."

        response = apiObj
    else:
        with apiCall:
            # response as JSON string
            response_json = apiCall.read().decode('utf-8')

        response = json.loads(response_json)

    return response


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


def NOAA_API(requestURL):
    """
    Sends API request to NOAA forecast API and returns json results
    in python object format
    """
    # # create a request object with header data
    # header_data = {'User-Agent': "personal_app_contact_pschlais@gmail.com"}
    # req_obj = urllib.request.Request(requestURL, headers=header_data)
    # make sure the URL call does not throw an error
    try:
        # apiCall = urllib.request.urlopen(requestURL)
        apiCall = requests.get(requestURL)
    except URLError:
        # i.e. CERTIFICATE_VERIFY_FAILED error
        # Create dictionary for view to parse wtih error information
        apiObj = {}
        apiObj["status"] = "URL_ERROR"
        apiObj["message"] = "HTTP error accessing NOAA forecast API."

        response = apiObj
    else:
        # with apiCall:
        #     # response as JSON string
        #     response_json = apiCall.read().decode('utf-8')
        # apiObj = json.loads(response_json)
        apiObj = apiCall.json()
        apiObj["status"] = "OK"
        apiObj["message"] = ""

        response = apiObj

    # apiCall = urllib.request.urlopen(requestURL)
    # with apiCall:
    #     # response as JSON string
    #     response_json = apiCall.read().decode('utf-8')

    # apiObj = json.loads(response_json)
    # apiObj["status"] = "OK"
    # apiObj["message"] = ""

    # response = apiObj


    return response
