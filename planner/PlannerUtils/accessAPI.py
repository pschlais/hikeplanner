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
        apiCall = requests.get(requestURL)
    except URLError:
        # i.e. CERTIFICATE_VERIFY_FAILED error
        # Create dictionary for view to parse wtih error information
        apiObj = {}
        apiObj["status"] = "URL_ERROR"
        apiObj["message"] = "HTTP error accessing Google Distance Matrix API."

        response = apiObj
    else:
        response = apiCall.json()

    return response


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
