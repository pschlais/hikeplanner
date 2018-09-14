from django.core.management.base import BaseCommand
from planner.PlannerUtils import updateTable

class Command(BaseCommand):
    help = ('Updates trailhead-major city combinations in the ' +
            'DriveTimeMajorCity table/intermediate model.')

    def handle(self, *args, **options):
        # update drive time matrix table entries
        output = updateTable.updateDriveTimeEntries(run_errors = True)
        # print output
        for s in output['print_output']:
            self.stdout.write(s)
