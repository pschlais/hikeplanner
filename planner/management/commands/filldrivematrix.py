from django.core.management.base import BaseCommand
from planner.PlannerUtils import updateTable

class Command(BaseCommand):
    help = ('Adds any missing trailhead-major city combinations in the ' +
            'DriveTimeMajorCity table/intermediate model.')

    def handle(self, *args, **options):
        # create new drive time matrix table entries
        output = updateTable.createNewDriveTimeEntries()
        # print output
        for s in output['print_output']:
            self.stdout.write(s)
