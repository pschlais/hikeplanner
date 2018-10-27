from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet
from planner.models import Trailhead, MajorCity, DriveTimeMajorCity
from planner.PlannerUtils import constructURL, accessAPI, parseAPI
from datetime import date

# constant parameters for Google Distance Matrix API query limits
# see: "https://developers.google.com/maps/documentation/distance-matrix/usage-and-billing", section "Other Usage Limits"
DISTANCE_MATRIX_API_MAX_ORIGINS = 25
DISTANCE_MATRIX_API_MAX_DESTINATIONS = 25


def createNewDriveTimeEntries():
    """
    Adds any missing trailhead-major city combinations in the DriveTimeMajorCity table/intermediate model.
    """
    trailheads = Trailhead.objects.all()
    majorcities = MajorCity.objects.all()
    tablematrix = DriveTimeMajorCity.objects.all()
    new_count = 0
    output_strings = []  # contains optional console strings to print

    # loop through major cities
    for majorcity in majorcities:
        mc_count = 0
        # loop through trailheads
        for trailhead in trailheads:
            # if combination exists, do nothing
            try:
                tablematrix.get(trailhead=trailhead, majorcity=majorcity)
            except ObjectDoesNotExist:
                # if combination doesn't exist, add it to the database
                new_entry = DriveTimeMajorCity(trailhead=trailhead,
                        majorcity=majorcity)
                new_entry.save()
                mc_count += 1
                new_count += 1
                output_strings.append("Added {0} - {1}".format(majorcity.name,
                                        trailhead.name))
        # write total added for current city
        output_strings.append("Entries added for {0}: {1}".format(majorcity.name, mc_count))
    # write total new entries created
    output_strings.append("Total new entries: {0}".format(new_count))
    # return optional output
    return {'num_added': new_count, 'print_output': output_strings}


def updateDriveTimeEntries(run_new=True, run_errors=False,
                           origin_type="majorcity"):
    """
    Calls Google Distance Matrix API and adds results to the table.
    Requests are created and called per single-origin, looped over all
    available origin points to all available destinations. The origin type is
    defined by the "origin_type" optional input, defaulted to "majorcity"

    INPUTS:
    run_new (bool): run any combinations marked as "NEW_ITEM"
    run_errors (bool): run any combinations marked as "ERROR"
    origin_type (str): Input to set origins in API request. "majorcity"
                        does loop per MajorCity object, "trailhead" does loop
                        per Trailhead object
    """
    num_updated = 0
    # max destinations constant defined at top of this module
    max_destinations = DISTANCE_MATRIX_API_MAX_DESTINATIONS
    output_strings = []

    # get all origin objects
    if origin_type == "trailhead":
        origins = Trailhead.objects.all()
    else:
        origins = MajorCity.objects.all()

    # loop over origins
    for origin in origins:
        # get queryset for current origin
        if origin_type == "trailhead":
            origin_filter = {'trailhead': origin}
        else:
            origin_filter = {'majorcity': origin}

        if run_new:
            qs_new = DriveTimeMajorCity.objects.filter(**origin_filter,
                        api_call_status=DriveTimeMajorCity.NEW_ITEM)
            qs = qs_new
        if run_errors:
            qs_error = DriveTimeMajorCity.objects.filter(**origin_filter,
                        api_call_status=DriveTimeMajorCity.ERROR)
            qs = qs_error

        # combine both new and error entries if both flags True
        if run_new and run_errors:
            qs = qs_new.union(qs_error)

        # create url if values to update
        if qs.count() > 0:
            output_strings.append("Records to update for origin {0}: ".format(origin.name) + str(qs.count()))

            # get origin latitude/longitude
            origin_latlon = origin.latlon_str

            # split queryset into limit on destination calls
            qs_slice_indices = _get_slice_indices(qs.count(), max_destinations)

            # loop over each queryset slice
            for slice_ind in qs_slice_indices:

                i_start = slice_ind[0]
                i_end = slice_ind[1]

                # create sliced queryset
                if i_start + 1 == i_end:  # don't slice a single element
                    sliced_qs = qs[i_start]
                else:
                    sliced_qs = qs[i_start:i_end]

                # reset destinations array
                destinations = []

                # add destinations to list for URL
                for combo in sliced_qs:
                    output_strings.append(combo.api_call_status_expanded +
                        " ----- " + combo.majorcity.name + " : " +
                        combo.trailhead.name)

                    if origin_type == "trailhead":
                        destinations.append(combo.majorcity.latlon_str)
                    else:
                        destinations.append(combo.trailhead.latlon_str)

                # create URL
                apiURL = constructURL.googleMapsDistanceAPI(origin_latlon,
                                                            destinations)
                output_strings.append("API call: " + apiURL)
                # call API
                apiOutput = accessAPI.googleMapsDistanceAPI(apiURL)
                # parse API results
                for i_dest, dest in enumerate(destinations):
                    apiParse = parseAPI.unpackDriveProperties(apiOutput,
                                            destination_index=i_dest)
                    if apiParse["APIStatus"] != "OK":
                        # set entry to error, save error message
                        output_strings.append(
                            "API error for " + qs[i_dest].majorcity.name + " : " +
                            qs[i_dest].trailhead.name + " -- '" +
                            apiParse["APIMessage"] + "'")

                        qs[i_dest].api_call_status = DriveTimeMajorCity.ERROR
                        qs[i_dest].error_message = apiParse["APIMessage"]
                        qs[i_dest].drive_distance = None
                        qs[i_dest].drive_time = None
                        qs[i_dest].save()

                    else:  # overall API call returned data
                        if apiParse["dataStatus"] != "OK":
                            # set entry to error, save error message
                            output_strings.append(
                                "Data error for " + qs[i_dest].majorcity.name +
                                " : " + qs[i_dest].trailhead.name + " -- '" +
                                apiParse["dataMessage"] + "'")

                            qs[i_dest].api_call_status = DriveTimeMajorCity.ERROR
                            qs[i_dest].error_message = apiParse["dataMessage"]
                            qs[i_dest].drive_distance = None
                            qs[i_dest].drive_time = None
                            qs[i_dest].save()

                        else:
                            # data is valid, save results
                            output_strings.append(
                                "VALID -- " + qs[i_dest].majorcity.name + " : " +
                                qs[i_dest].trailhead.name + " -- '" +
                                apiParse["dataMessage"] + "'")

                            output_strings.append("     distance: " +
                                str(apiParse["distance"]["value"]) + ", time: " +
                                str(apiParse["duration"]["value"]))

                            qs[i_dest].api_call_status = DriveTimeMajorCity.OK
                            qs[i_dest].error_message = ""
                            qs[i_dest].drive_distance = apiParse["distance"]["value"]
                            qs[i_dest].drive_time = apiParse["duration"]["value"]
                            qs[i_dest].date_updated = date.today()
                            qs[i_dest].save()

                            num_updated += 1

        else:
            output_strings.append("No records to update for origin " +
                                  origin.name)

    output_strings.append("Number updated: " + str(num_updated))

    return {'num_updated': num_updated,
            'print_output': output_strings}


def _get_slice_indices(length, multiple):
    """
    Returns an array of start and end incides to slice an array by a certain
    multiple. For example, if a queryset has 8 elements and you want to limit
    evaluations at a given time to 3, this function would return:
        [[0,3], [3,6], [6,8]]
    The result can be used in a loop to evaluate queries in groups of 3.

    --CORNER CASES--
    If the length is <= 0, returns a ValueError.
    If the length is less than the multiple, returns [[0, 1ength]].

    INPUTS:
        length (int): length of the set to slice.
        multiple (int): the number of elements to include per slice
    OUTPUT:
        Array of start/end indices (e.g. [[0,5], [5,10], [10, 15]]).
    """

    if length <= 0:
        raise ValueError("input length must be greater than 0")
    elif length <= multiple:
        # return indices corresponding to full set
        return [[0, length]]
    else:
        # create container array
        ind_list = []
        # calculate number of full multiples in length
        n_multiples = int(length / multiple)
        # loop over multiples
        for i in range(0, n_multiples):
            ind_list.append([i * multiple, (i + 1) * multiple])

        # add last segment of the length if it is not a clean multiple
        if n_multiples * multiple != length:
            ind_list.append([n_multiples * multiple, length])

        return ind_list
