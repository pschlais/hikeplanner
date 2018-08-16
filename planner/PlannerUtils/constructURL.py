"""
This module provides functions to construct various URLs for buttons/links
"""
import urllib.parse
import os


def validLatLon(lat=None, lon=None):
    """
    Tests -90 < lat < 90 and -180 < lon < 180.

    Parameters
    ----------------
    lat : float [OPTIONAL]
        Latitude of the point
    lon : float [OPTIONAL]
        Longitude of the point

    Returns
    ----------------
    bool
        True if valid, False if not
    """
    if lat is not None and (lat <= -90 or lat >= 90):
        return False
    if lon is not None and (lon <= -180 or lon >= 180):
        return False

    # all provided inputs are valid
    return True


def googleMapsPointExternal(latitude, longitude, layer, zoom=15):
    """
    Builds a URL for Google Maps centered at a point for various layer options.

    Parameters
    ----------------
    latitude : float
        Latitude of the point
    longitude : float
        Longitude of the point
    layer : string
        Map layer to display. Supported inputs are:
            -"terrain"
            -"satellite"
            -"roadmap"

    Returns
    ----------------
    string
        URL for google maps standalone page
    """
    # input validation
    BASE_LAYER_OPTIONS = ["terrain", "satellite", "roadmap"]

    if not validLatLon(lat=latitude):
        raise ValueError("latitude input must be between -90 and 90 degrees. Input value was {0}".format(latitude))
    if not validLatLon(lon=longitude):
        raise ValueError("longitude input must be between -180 and 180 degrees. Input value was {0}".format(longitude))
    if layer.lower() not in BASE_LAYER_OPTIONS:
        raise ValueError("base layer input 'layer' expected to be 'terrain', 'satellite', or 'roadmap'. Input value was '{0}'".format(layer))

    # URL construction
    base_url = "https://www.google.com/maps/@?api=1&map_action=map"
    center = "center=" + str(latitude) + "," + str(longitude)
    zoom = "zoom=" + str(zoom)
    layer = "basemap=" + layer.lower()

    return "&".join([base_url, center, zoom, layer])


def googleMapsPointEmbed(latitude, longitude, width=500, height=400,
                         maptype="terrain", zoom=14):
    """
    Builds a URL for Google Maps centered at a point for various layer options.

    Parameters
    ----------------
    latitude : float
        Latitude of the point
    longitude : float
        Longitude of the point
    width : float
        width of the returned image, in pixels
    height: float
        height of the returned image, in pixels
    maptype : string
        Map layer to display. Supported inputs are:
            -"terrain"
            -"satellite"
            -"roadmap"
            -"hybrid" (satellite + roadmap)
    zoom : int
        zoom level of the map
            1: world
            5: landmass/continent
            10: city
            15: streets
            20: buildings

    Returns
    ----------------
    string
        URL for google maps standalone page
    """

    # input validation
    MAP_TYPE_OPTIONS = ["terrain", "satellite", "roadmap", "hybrid"]

    if not validLatLon(lat=latitude):
        raise ValueError("latitude input must be between -90 and 90 degrees. Input value was {0}".format(latitude))
    if not validLatLon(lon=longitude):
        raise ValueError("longitude input must be between -180 and 180 degrees. Input value was {0}".format(longitude))
    if maptype.lower() not in MAP_TYPE_OPTIONS:
        raise ValueError("map type input expected to be 'terrain', 'satellite', 'roadmap', or 'hybrid'. Input value was '{0}'".format(maptype))

    # # URL construction
    base_url = "https://maps.googleapis.com/maps/api/staticmap?"
    params = {
        "center": str(latitude) + "," + str(longitude),
        "size": str(width) + "x" + str(height),
        "zoom": str(zoom),
        "maptype": maptype.lower(),
        "markers": str(latitude) + "," + str(longitude),
        "key": os.environ.get("HIKEPLANNER_GOOGLE_MAPS_EMBED_API_KEY"),
    }

    # construct URL and encode characters
    return base_url + urllib.parse.urlencode(params)



def googleMapsDirectionsExternal(origin, destination):
    """
    Builds a URL for Google Maps directions URL between the origin and destination.

    Parameters
    ----------------
    origin : string
        The input to the "origin" field on the Google Maps interface
    destination : string
        The input to the "destination" field on the Google Maps interface

    Returns
    ----------------
    string
        URL for google maps directions standalone page
    """

    # URL components
    base_url = "https://google.com/maps/dir/?api=1&"
    params = {
        "origin": origin,
        "destination": destination,
        "travelmode": "driving",
    }

    return base_url + urllib.parse.urlencode(params)


def googleMapsDistanceAPI(origins, destinations):
    """
    Builds a URL for Google Maps directions URL between the origin and destination.

    Parameters
    ----------------
    origins : string or [string]
        The input to the "origins" field on the Google Maps interface
    destinations : string or [string]
        The input to the "destinations" field on the Google Maps interface

    Returns
    ----------------
    string
        URL for google maps directions standalone page
    """

    # input processing: make sure origins and destinations are lists. If not,
    # put single origin/destination
    if type(origins) is not list:
        origin_str = origins
    else:
        origin_str = "|".join(origins)

    if type(destinations) is not list:
        destination_str = destinations
    else:
        destination_str = "|".join(destinations)

    # URL components
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json?"
    params = {
        "origins": origin_str,
        "destinations": destination_str,
        "mode": "driving",
        "units": "imperial",
        # "departure_time" or
        # "arrival_time" (can't specify both)
        "key": os.environ.get("HIKEPLANNER_GOOGLE_DISTANCE_MATRIX_API_KEY"),
    }

    return base_url + urllib.parse.urlencode(params)


def buildCalTopoURL(latitude, longitude):
    """
    Builds a URL for CalTopo.

    Parameters
    ----------------
    latitude : float
        Latitude of the point
    longitude : float
        Longitude of the point

    Returns
    ----------------
    string
        URL for CalTopo standalone page centered at given latitude/longitude
    """

    # parameter list
    paramDict = {'z': 15, 'b': 't', 'o': 'r', 'n': 0.25}
    # build URL
    CalTopoURL = 'https://caltopo.com/map.html#ll=' + str(latitude) + ',' + str(longitude)
    for param, val in paramDict.items():
        CalTopoURL += '&' + str(param) + '=' + str(val)

    return CalTopoURL


def buildNOAAURL(latitude, longitude):
    """
    Builds a URL for NOAA weather forecast.

    Parameters
    ----------------
    latitude : float
        Latitude of the point
    longitude : float
        Longitude of the point

    Returns
    ----------------
    string
        URL for NOAA standalone page centered at given latitude/longitude
    """

    NOAA_URL = ("https://forecast.weather.gov/MapClick.php?lon=" +
                str(longitude) + "&lat=" + str(latitude))

    return NOAA_URL

def buildNOAAembedURL(latitude, longitude):
    """
    Builds a URL for an embedded widget for NOAA weather forecast.

    Parameters
    ----------------
    latitude : float
        Latitude of the point
    longitude : float
        Longitude of the point

    Returns
    ----------------
    string
        URL for NOAA iframe-embedded page centered at given latitude/longitude
    """

    NOAA_embed_URL = ("https://forecast-v3.weather.gov/point/" + str(latitude)
                      + "," + str(longitude) + "?mode=widget")

    return NOAA_embed_URL

def buildNOAAapiURL(latitude, longitude):
    """
    Builds a URL for an API call for NOAA weather forecast.

    Parameters
    ----------------
    latitude : float
        Latitude of the point
    longitude : float
        Longitude of the point

    Returns
    ----------------
    string
        URL for NOAA forecast API call at given latitude/longitude
    """

    NOAA_API_URL = ("https://api.weather.gov/points/" + str(latitude)
                      + "," + str(longitude) + "/forecast")
    # NOAA_API_URL = ("https://api.weather.gov/points/" + str(latitude)
    #                   + "," + str(longitude))

    return NOAA_API_URL
