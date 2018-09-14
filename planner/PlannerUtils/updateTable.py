from django.core.exceptions import ObjectDoesNotExist
from planner.models import Trailhead, MajorCity, DriveTimeMajorCity


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
