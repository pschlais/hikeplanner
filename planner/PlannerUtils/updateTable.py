from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet
from planner.models import Trailhead, MajorCity, DriveTimeMajorCity
from planner.PlannerUtils import constructURL, accessAPI, parseAPI
from datetime import date


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


def updateDriveTimeEntries(run_new=True, run_errors=False):
    """
    Calls Google Distance Matrix API and adds results to the table.

    INPUTS:
    run_new (bool): run any combinations marked as "NEW_ITEM"
    run_errors (bool): run any combinations marked as "ERROR"
    """
    num_updated = 0
    output_strings = []

    # get all major cities
    majorcities = MajorCity.objects.all()
    # loop over major cities
    for majorcity in majorcities:
        # get queryset for current majorcity
        if run_new:
            qs_new = DriveTimeMajorCity.objects.filter(majorcity=majorcity,
                        api_call_status=DriveTimeMajorCity.NEW_ITEM)
            qs = qs_new
        if run_errors:
            qs_error = DriveTimeMajorCity.objects.filter(majorcity=majorcity,
                        api_call_status=DriveTimeMajorCity.ERROR)
            qs = qs_error

        # combine both new and error entries if both flags True
        if run_new and run_errors:
            qs = qs_new.union(qs_error)

        # create url if values to update
        if qs.count() > 0:
            output_strings.append("Records to update: " + str(qs.count()))
            # add origin and destinations to URL
            origin = majorcity.latlon_str
            destinations = []
            for combo in qs:
                output_strings.append(combo.api_call_status_expanded +
                    " ----- " + majorcity.name + " : " + combo.trailhead.name)
                destinations.append(combo.trailhead.latlon_str)

            # create URL
            apiURL = constructURL.googleMapsDistanceAPI(origin, destinations)
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
            output_strings.append("No records to update for major city " +
                                  majorcity.name)

    output_strings.append("Number updated: " + str(num_updated))

    return {'num_updated': num_updated,
            'print_output': output_strings}
